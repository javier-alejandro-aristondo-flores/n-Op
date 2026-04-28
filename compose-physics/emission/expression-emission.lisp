;;; Per-node C-string emission for the IR.
;;;
;;; Every IR node produces a fully-parenthesized C expression that
;;; evaluates against the buffers exposed by the dispatcher
;;; (`state` for residuals, `state_curr` for updates). Numeric
;;; literals are emitted at full double precision so the C path
;;; round-trips bit-exact with the Lisp funcall path. Apply nodes
;;; defer to the vocabulary's emission identifier — every function
;;; that participates in codegen registers an identifier that the
;;; consumer's compiled object provides (math.h's standard names for
;;; the registered standard entries, plus cp_reciprocal that the
;;; dispatcher emits as a static inline helper).
;;;
;;; This file is pure: it manipulates strings, never the filesystem,
;;; and it has no opinions about chunking or buffer naming. The
;;; chunking and dispatch layers feed the buffer name in as a
;;; parameter.

(in-package #:compose-physics)


(defun format-double-literal (value)
  "Format VALUE as a C double-precision literal in scientific
   notation with 16 fractional digits (17 significant figures), the
   minimum that guarantees IEEE-754 double round-trip across any
   conforming printf / strtod pair."
  (check-type value double-float)
  (let ((formatted (format nil "~,16,,,,,'eE" value)))
    formatted))


(defgeneric %emit-expression (node state-buffer-name)
  (:documentation
   "Internal dispatch: return the C-source string for NODE referencing
    STATE-BUFFER-NAME for term lookups. Always parenthesizes its
    output so callers can splice it into surrounding expressions
    without parsing-precedence concerns."))


(defun emit-expression-c (expression &key (state-buffer-name "state"))
  "Return the C-source string for EXPRESSION evaluating against the
   double-array variable named STATE-BUFFER-NAME (defaults to
   'state', matching the residual ABI; the update ABI passes
   'state_curr')."
  (check-type expression expression)
  (check-type state-buffer-name string)
  (%emit-expression expression state-buffer-name))


(defmethod %emit-expression ((node term) state-buffer-name)
  (format nil "(~A * ~A[~D])"
          (format-double-literal (term-coefficient node))
          state-buffer-name
          (term-index node)))


(defmethod %emit-expression ((node sum) state-buffer-name)
  (let ((children (sum-children node)))
    (with-output-to-string (stream)
      (write-char #\( stream)
      (loop for child in children
            for first = t then nil
            do (unless first (write-string " + " stream))
               (write-string (%emit-expression child state-buffer-name)
                             stream))
      (write-char #\) stream))))


(defmethod %emit-expression ((node product) state-buffer-name)
  (let ((children (product-children node)))
    (with-output-to-string (stream)
      (write-char #\( stream)
      (loop for child in children
            for first = t then nil
            do (unless first (write-string " * " stream))
               (write-string (%emit-expression child state-buffer-name)
                             stream))
      (write-char #\) stream))))


(defmethod %emit-expression ((node scale) state-buffer-name)
  (format nil "(~A * ~A)"
          (format-double-literal (scale-factor node))
          (%emit-expression (scale-child node) state-buffer-name)))


(defmethod %emit-expression ((node apply) state-buffer-name)
  (let* ((function-keyword (apply-name node))
         (record (lookup-function-record function-keyword))
         (identifier (and record (function-record-emission-identifier record))))
    (when (or (null identifier) (zerop (length identifier)))
      (error "apply :~A has no emission identifier registered; cannot emit C"
             function-keyword))
    (format nil "~A(~A)"
            identifier
            (%emit-expression (apply-child node) state-buffer-name))))


(defun collect-emission-identifiers (expression)
  "Return the sorted unique list of vocabulary emission identifiers
   referenced by apply nodes anywhere in EXPRESSION. The dispatcher
   uses this to decide which inline helpers (notably cp_reciprocal)
   to provide alongside the chunk sources."
  (let ((identifiers '()))
    (walk-expression expression
                     (lambda (node)
                       (when (apply-p node)
                         (let* ((record
                                 (lookup-function-record (apply-name node)))
                                (identifier
                                 (and record
                                      (function-record-emission-identifier
                                       record))))
                           (when (and identifier
                                      (not (zerop (length identifier))))
                             (pushnew identifier identifiers
                                      :test #'string=))))))
    (sort identifiers #'string<)))


;;; Inline self-checks. Confirm shape of emitted text and round-trip
;;; of the literal formatter.

(eval-when (:load-toplevel :execute)

  ;; Literal round-trip on a few representative values.
  (dolist (value '(0.0d0 1.0d0 -1.0d0 3.141592653589793d0
                   1.0d-300 -1.7976931348623157d308 0.1d0))
    (let* ((rendered (format-double-literal value))
           (parsed (with-input-from-string (stream rendered)
                     (let ((*read-default-float-format* 'double-float))
                       (read stream)))))
      (assert (= parsed value) ()
              "literal ~S formatted as ~A re-read as ~S" value rendered parsed)))

  ;; Term emission carries coefficient and index.
  (let ((rendered (emit-expression-c (term 2.0d0 5 :name "x"))))
    (assert (search "state[5]" rendered))
    (assert (search "2." rendered)))

  ;; Sum emission lists children separated by ' + '.
  (let* ((tree (sum (term 1.0d0 0 :name "a")
                    (term 1.0d0 1 :name "b")
                    (term 1.0d0 2 :name "c")))
         (rendered (emit-expression-c tree))
         (separator-count
          (loop with start = 0
                for position = (search " + " rendered :start2 start)
                while position
                count 1
                do (setf start (+ position 3)))))
    (assert (= 2 separator-count) ()
            "expected two ' + ' separators in ~A" rendered)
    (assert (search "state[0]" rendered))
    (assert (search "state[2]" rendered)))

  ;; Product emission separates children with ' * '.
  (let ((rendered (emit-expression-c
                   (product (term 1.0d0 0 :name "a")
                            (term 1.0d0 1 :name "b")))))
    (assert (search " * " rendered))
    (assert (search "state[0]" rendered))
    (assert (search "state[1]" rendered)))

  ;; Scale emits the factor literal followed by * child.
  (let ((rendered (emit-expression-c
                   (scale 0.5d0 (term 1.0d0 0 :name "a")))))
    (assert (search " * " rendered))
    (assert (search "5." rendered)))

  ;; Apply emits the registered identifier name.
  (let ((rendered (emit-expression-c
                   (apply :sin (term 1.0d0 0 :name "x")))))
    (assert (search "sin(" rendered) ()
            "expected sin(...) in ~A" rendered)
    (assert (search "state[0]" rendered)))

  ;; Custom buffer name plumbs through.
  (let ((rendered (emit-expression-c (term 1.0d0 0 :name "x")
                                     :state-buffer-name "state_curr")))
    (assert (search "state_curr[0]" rendered)))

  ;; Apply with no emission identifier registered errors loudly.
  (let ((existing (lookup-function-record :--emission-test-no-identifier)))
    (unless existing
      (register-function :--emission-test-no-identifier (lambda (x) x))))
  (handler-case
      (progn
        (emit-expression-c
         (apply :--emission-test-no-identifier (term 1.0d0 0 :name "x")))
        (assert nil () "expected error for missing emission identifier"))
    (error () nil))

  ;; collect-emission-identifiers gathers a sorted unique set.
  (let* ((tree (sum (apply :sin (term 1.0d0 0 :name "x"))
                    (apply :cos (term 1.0d0 0 :name "x"))
                    (apply :sin (term 1.0d0 1 :name "y"))))
         (identifiers (collect-emission-identifiers tree)))
    (assert (equal identifiers '("cos" "sin")) ()
            "expected (cos sin), got ~S" identifiers)))
