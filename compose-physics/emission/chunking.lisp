;;; Chunked C source emission.
;;;
;;; A residual or update form with K (or N) rows is written across
;;; ceil(rows/chunk-row-count) C source files, each containing one
;;; chunk function that assigns its slice of the output buffer. The
;;; dispatcher in dispatch.lisp calls every chunk function in order.
;;;
;;; Chunking exists because the C compiler's optimizer scales
;;; super-linearly with function size; splitting the work across
;;; many smaller files lets `make -j` parallelize and finish in
;;; reasonable time on large problems. For small problems chunking
;;; is overhead in the form of extra compilation units, but the
;;; output is always correct: each chunk writes to a disjoint range
;;; of the output buffer.
;;;
;;; This file is pure: it returns chunk-source records describing
;;; what to write where. The persistence layer is responsible for
;;; actually creating files. The records carry the union of
;;; emission identifiers each chunk references so the dispatcher
;;; can decide which inline helpers (cp_reciprocal, principally) to
;;; provide.

(in-package #:compose-physics)


(defparameter *default-chunk-row-count* 32
  "Default rows per chunk. 32 keeps individual translation units
   small enough that gcc -O3 stays in its linear-time regime on
   typical residual / update expressions, while leaving room for
   parallel compilation on large problems.")


(defparameter *reciprocal-emission-identifier* "cp_reciprocal"
  "C identifier that the :reciprocal vocabulary entry registers.
   Chunks that reference this identifier emit a static inline
   definition at the top of their translation unit so the chunk
   compiles independently of the dispatcher.")


(defstruct chunk-source
  "Describes one C source file: its filename, the C function name
   defined inside, the function body source, the first row index it
   covers in the output buffer, the number of rows it covers, and
   the union of vocabulary emission identifiers referenced by any
   row's expression. Pure data — the persistence layer writes it
   to disk and the dispatcher emits forward declarations and call
   sites for it."
  (filename             ""  :type string  :read-only t)
  (function-name        ""  :type string  :read-only t)
  (text                 ""  :type string  :read-only t)
  (first-row-index      0   :type fixnum  :read-only t)
  (row-count            0   :type fixnum  :read-only t)
  (emission-identifiers nil :type list    :read-only t))


(defun %assert-positive-chunk-row-count (chunk-row-count)
  (check-type chunk-row-count fixnum)
  (unless (plusp chunk-row-count)
    (error "chunk-row-count must be positive, got ~D" chunk-row-count)))


(defun %partition-rows-into-chunks (rows chunk-row-count)
  "Split ROWS into a list of (first-index, sub-rows) pairs of length
   chunk-row-count except possibly the last."
  (let ((partitions '())
        (length-of-rows (length rows)))
    (loop for start from 0 below length-of-rows by chunk-row-count
          for end = (min (+ start chunk-row-count) length-of-rows)
          do (push (list start (subseq rows start end)) partitions))
    (nreverse partitions)))


(defun %sanitize-emission-identifier-set (per-row-identifier-lists)
  "Return the sorted unique union of identifier lists."
  (let ((set '()))
    (dolist (identifiers per-row-identifier-lists)
      (dolist (identifier identifiers)
        (pushnew identifier set :test #'string=)))
    (sort set #'string<)))


;;; Helper: write one chunk function body. ROW-DESCRIPTORS is a list
;;; of (output-buffer-name index expression) tuples; the chunk emits
;;; one assignment per descriptor.

(defun %render-chunk-function (function-name
                               output-buffer-name
                               input-buffer-name
                               row-descriptors
                               emission-identifiers)
  "Format a complete C source string defining FUNCTION-NAME and
   assigning each row descriptor's expression to the corresponding
   slot of OUTPUT-BUFFER-NAME. EMISSION-IDENTIFIERS is the set of
   vocabulary identifiers referenced by any row in this chunk; the
   chunk file emits its own libm include and any inline helpers
   so that it is independently compilable without depending on the
   dispatcher's translation unit for declarations."
  (with-output-to-string (stream)

    (format stream "#include <math.h>~%")
    (when (member *reciprocal-emission-identifier* emission-identifiers
                  :test #'string=)
      (format stream
              "static inline double ~A(double x) { return 1.0 / x; }~%"
              *reciprocal-emission-identifier*))
    (terpri stream)

    (format stream "void ~A(const double *~A, double *~A) {~%"
            function-name input-buffer-name output-buffer-name)
    (dolist (descriptor row-descriptors)
      (destructuring-bind (output-name output-index expression) descriptor
        (declare (ignore output-name))
        (format stream "    ~A[~D] = ~A;~%"
                output-buffer-name
                output-index
                (emit-expression-c expression
                                   :state-buffer-name input-buffer-name))))
    (format stream "}~%")))


;;; Public emitters. Both return a list of chunk-source records, in
;;; chunk order. The list may be empty when the form has zero rows
;;; (a degenerate but legal case for residual; never for update).

(defun emit-residual-chunks (problem
                             &key (chunk-row-count *default-chunk-row-count*))
  "Emit chunked C sources for PROBLEM's residual form. Each chunk
   defines compute_residual_chunk_NNN with signature

       void compute_residual_chunk_NNN(const double *state,
                                       double *out_r);

   that assigns its slice of the residual output buffer."
  (check-type problem problem)
  (%assert-positive-chunk-row-count chunk-row-count)
  (let* ((rows (coerce (problem-residual-rows problem) 'list))
         (partitions (%partition-rows-into-chunks rows chunk-row-count))
         (chunks '()))
    (loop for chunk-index from 0
          for (first-row-index sub-rows) in partitions
          do
       (let* ((row-descriptors
               (loop for row in sub-rows
                     for offset from 0
                     collect (list "out_r"
                                   (+ first-row-index offset)
                                   (residual-row-expression row))))
              (per-row-identifier-lists
               (mapcar (lambda (row)
                         (collect-emission-identifiers
                          (residual-row-expression row)))
                       sub-rows))
              (function-name (format nil "compute_residual_chunk_~3,'0D"
                                     chunk-index))
              (filename (format nil "residual_chunk_~3,'0D.c" chunk-index))
              (chunk-identifier-set
               (%sanitize-emission-identifier-set per-row-identifier-lists))
              (text (%render-chunk-function function-name
                                            "out_r" "state"
                                            row-descriptors
                                            chunk-identifier-set)))
         (push (make-chunk-source
                :filename filename
                :function-name function-name
                :text text
                :first-row-index first-row-index
                :row-count (length sub-rows)
                :emission-identifiers chunk-identifier-set)
               chunks)))
    (nreverse chunks)))


(defun emit-update-chunks (problem
                           &key (chunk-row-count *default-chunk-row-count*))
  "Emit chunked C sources for PROBLEM's update form. Each chunk
   defines compute_update_chunk_NNN with signature

       void compute_update_chunk_NNN(const double *state_curr,
                                     double *state_next);

   that assigns its slice of the next-state output buffer. Identity
   rows are emitted explicitly so callers can rely on the full N-
   length output buffer."
  (check-type problem problem)
  (%assert-positive-chunk-row-count chunk-row-count)
  (let* ((rows (coerce (problem-update-rows problem) 'list))
         (partitions (%partition-rows-into-chunks rows chunk-row-count))
         (chunks '()))
    (loop for chunk-index from 0
          for (first-row-index sub-rows) in partitions
          do
       (let* ((row-descriptors
               (loop for row in sub-rows
                     for offset from 0
                     collect (list "state_next"
                                   (+ first-row-index offset)
                                   (update-row-expression row))))
              (per-row-identifier-lists
               (mapcar (lambda (row)
                         (collect-emission-identifiers
                          (update-row-expression row)))
                       sub-rows))
              (function-name (format nil "compute_update_chunk_~3,'0D"
                                     chunk-index))
              (filename (format nil "update_chunk_~3,'0D.c" chunk-index))
              (chunk-identifier-set
               (%sanitize-emission-identifier-set per-row-identifier-lists))
              (text (%render-chunk-function function-name
                                            "state_next" "state_curr"
                                            row-descriptors
                                            chunk-identifier-set)))
         (push (make-chunk-source
                :filename filename
                :function-name function-name
                :text text
                :first-row-index first-row-index
                :row-count (length sub-rows)
                :emission-identifiers chunk-identifier-set)
               chunks)))
    (nreverse chunks)))


;;; Inline self-checks. Build a tiny problem and verify the chunking
;;; layer's outputs respect the contract.

(eval-when (:load-toplevel :execute)

  ;; Problem with 5 residual rows and 5 slots, chunk-row-count = 2 →
  ;; expect 3 chunks of sizes 2, 2, 1. Slots: a,b,c,d,e.
  (let* ((problem
          (make-problem
           :name "chunk-self-check"
           :slot-names '("a" "b" "c" "d" "e")
           :residual-specs
           (list (cons "row-a"
                       (sum (term 1.0d0 0 :name "a")
                            (scale -1.0d0 (term 1.0d0 1 :name "b"))))
                 (cons "row-b"
                       (apply :sin (term 1.0d0 1 :name "b")))
                 (cons "row-c"
                       (term 2.0d0 2 :name "c"))
                 (cons "row-d"
                       (sum (term 1.0d0 3 :name "d")
                            (apply :cos (term 1.0d0 4 :name "e"))))
                 (cons "row-e"
                       (term 1.0d0 4 :name "e")))))
         (chunks (emit-residual-chunks problem :chunk-row-count 2)))

    (assert (= (length chunks) 3) ()
            "expected 3 residual chunks, got ~D" (length chunks))

    (assert (string= (chunk-source-filename (first chunks))
                     "residual_chunk_000.c"))
    (assert (string= (chunk-source-filename (second chunks))
                     "residual_chunk_001.c"))
    (assert (string= (chunk-source-filename (third chunks))
                     "residual_chunk_002.c"))

    (assert (= (chunk-source-row-count (first chunks)) 2))
    (assert (= (chunk-source-row-count (third chunks)) 1))

    (assert (= (chunk-source-first-row-index (first chunks)) 0))
    (assert (= (chunk-source-first-row-index (second chunks)) 2))
    (assert (= (chunk-source-first-row-index (third chunks)) 4))

    ;; Chunk 0 mentions out_r[0] and out_r[1] but not out_r[2].
    (let ((text (chunk-source-text (first chunks))))
      (assert (search "out_r[0]" text))
      (assert (search "out_r[1]" text))
      (assert (not (search "out_r[2]" text)))
      (assert (search "compute_residual_chunk_000" text))
      (assert (search "const double *state" text))
      (assert (search "double *out_r" text))
      (assert (search "sin(" text)))

    ;; The union of emission identifiers across chunks: sin appears
    ;; in chunk 0, cos in chunk 1, none in chunk 2.
    (assert (equal (chunk-source-emission-identifiers (first chunks))
                   '("sin")))
    (assert (equal (chunk-source-emission-identifiers (second chunks))
                   '("cos")))
    (assert (null (chunk-source-emission-identifiers (third chunks)))))

  ;; Update path: a 3-slot problem with one explicit nontrivial
  ;; update and two implicit identity rows. Chunk size 5 (single
  ;; chunk). Confirm explicit and identity rows both make it into
  ;; the C source and reference state_curr / state_next.
  (let* ((problem
          (make-problem
           :name "chunk-update-self-check"
           :slot-names '("x" "y" "z")
           :residual-specs (list (cons "consistency"
                                       (sum (term 1.0d0 0 :name "x")
                                            (term 1.0d0 1 :name "y")
                                            (term 1.0d0 2 :name "z"))))
           :update-specs
           (list (cons "x"
                       (sum (term 1.0d0 0 :name "x")
                            (term 1.0d0 1 :name "y"))))))
         (chunks (emit-update-chunks problem :chunk-row-count 5)))
    (assert (= (length chunks) 1) ()
            "expected exactly 1 update chunk, got ~D" (length chunks))
    (let ((text (chunk-source-text (first chunks))))
      (assert (search "compute_update_chunk_000" text))
      (assert (search "const double *state_curr" text))
      (assert (search "double *state_next" text))
      (assert (search "state_next[0]" text))
      (assert (search "state_next[1]" text))
      (assert (search "state_next[2]" text)))
    (assert (= (chunk-source-row-count (first chunks)) 3)))

  ;; Default chunk-row-count is positive.
  (assert (plusp *default-chunk-row-count*))

  ;; Negative or zero chunk-row-count is rejected loudly.
  (handler-case
      (let ((problem (make-problem
                      :name "neg-chunk"
                      :slot-names '("a")
                      :residual-specs (list (cons "row"
                                                  (term 1.0d0 0 :name "a"))))))
        (emit-residual-chunks problem :chunk-row-count 0)
        (assert nil () "expected error on chunk-row-count = 0"))
    (error () nil)))
