;;; Per-problem manifest.sexp and root-level index.sexp.
;;;
;;; The manifest is the metadata sidecar that turns a problem
;;; directory from a heap of files into a self-describing artifact.
;;; A consumer can read manifest.sexp alone and know:
;;;
;;;   - the problem's name and content hash
;;;   - what slot names the input buffer has, in index order
;;;   - the K of compute_residual and the N of compute_update
;;;   - the names of every file in the directory (sources, sexp,
;;;     Makefile, library)
;;;   - the toolchain that was used to build the library
;;;   - the build timestamp (universal-time integer)
;;;   - the entry-point function names (compute_residual,
;;;     compute_update, get_n, get_k)
;;;
;;; The flat root-level index.sexp maps problem-name -> hash so
;;; that consumers can look a problem up by name without scanning
;;; the directory tree. The index is rewritten in full on every
;;; registration; readers must tolerate concurrent rewriting (the
;;; registry orchestrator does the actual file-replacement, this
;;; module only generates the contents).

(in-package #:compose-physics)


(defstruct manifest-toolchain
  (c-compiler ""  :type string :read-only t)
  (c-flags    ""  :type string :read-only t)
  (library-extension "" :type string :read-only t))


(defun build-manifest-sexp (&key
                              problem
                              content-hash
                              source-filename
                              residual-filenames
                              update-filenames
                              dispatch-filename
                              makefile-filename
                              library-filename
                              toolchain
                              build-timestamp)
  "Return the canonical sexp form of the manifest for PROBLEM. All
   filename arguments are bare filenames (no directory components)
   because the manifest sits next to the files it lists. SOURCE-FILENAME
   may be nil if the problem was registered programmatically or with
   :leave disposition."
  (check-type problem problem)
  (check-type content-hash string)
  (check-type residual-filenames list)
  (check-type update-filenames list)
  (check-type dispatch-filename string)
  (check-type makefile-filename string)
  (check-type library-filename string)
  (check-type toolchain manifest-toolchain)
  (check-type build-timestamp integer)
  (flet ((to-portable-string (s)
           (when s (coerce s '(simple-array character (*))))))
    (list :manifest
          (cons :problem-name (to-portable-string (problem-name problem)))
          (cons :content-hash (to-portable-string content-hash))
          (cons :slot-count (problem-slot-count problem))
          (cons :residual-count (problem-residual-count problem))
          (cons :slot-names
                (mapcar #'to-portable-string
                        (coerce (problem-slot-names problem) 'list)))
          (cons :build-timestamp build-timestamp)
          (list :toolchain
                (cons :c-compiler
                      (to-portable-string
                       (manifest-toolchain-c-compiler toolchain)))
                (cons :c-flags
                      (to-portable-string
                       (manifest-toolchain-c-flags toolchain)))
                (cons :library-extension
                      (to-portable-string
                       (manifest-toolchain-library-extension toolchain))))
          (list :files
                (cons :source (to-portable-string source-filename))
                (cons :residual-sexp "residual.sexp")
                (cons :update-sexp "update.sexp")
                (cons :problem-sexp "problem.sexp")
                (cons :residual-chunks
                      (mapcar #'to-portable-string residual-filenames))
                (cons :update-chunks
                      (mapcar #'to-portable-string update-filenames))
                (cons :dispatch (to-portable-string dispatch-filename))
                (cons :makefile (to-portable-string makefile-filename))
                (cons :library (to-portable-string library-filename)))
          (list :entry-points
              :compute-residual "compute_residual"
              :compute-update "compute_update"
              :get-n "get_n"
              :get-k "get_k"))))


(defun write-manifest-to-file (manifest-sexp pathname)
  "Write MANIFEST-SEXP as canonical text to PATHNAME. Intermediate
   directories are created as needed."
  (ensure-directories-exist pathname)
  (with-open-file (stream pathname
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (write-string (canonical-sexp-string manifest-sexp) stream)
    (terpri stream)))


(defun read-index-sexp (registry-root)
  "Return the registry-root index sexp, or nil if no index file
   exists yet. The on-disk form is (:index (NAME . HASH) ...)."
  (let ((path (merge-pathnames "index.sexp" (pathname registry-root))))
    (when (probe-file path)
      (let ((*read-default-float-format* 'double-float))
        (with-open-file (stream path :direction :input)
          (read stream))))))


(defun update-index-sexp (registry-root problem-name content-hash)
  "Rewrite REGISTRY-ROOT/index.sexp so that PROBLEM-NAME maps to
   CONTENT-HASH. Every other entry is preserved. The write replaces
   the file in full to keep the on-disk form a single canonical
   sexp."
  (check-type registry-root (or string pathname))
  (check-type problem-name string)
  (check-type content-hash string)
  (let* ((existing (read-index-sexp registry-root))
         (existing-entries (if (and (consp existing) (eq :index (first existing)))
                               (rest existing)
                               nil))
         (filtered (remove problem-name existing-entries
                           :key #'car :test #'string=))
         (updated (append filtered
                          (list (cons problem-name content-hash))))
         (sorted (sort (copy-list updated) #'string< :key #'car))
         (sexp (cons :index sorted))
         (path (merge-pathnames "index.sexp" (pathname registry-root))))
    (ensure-directories-exist path)
    (with-open-file (stream path
                            :direction :output
                            :if-exists :supersede
                            :if-does-not-exist :create)
      (write-string (canonical-sexp-string sexp) stream)
      (terpri stream))
    sexp))


(eval-when (:load-toplevel :execute)

  (let* ((problem
          (with-state (x y)
            (make-problem
             :name "manifest-self-check"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "balance" (sum x (scale -1.0d0 y))))
             :update-specs (list (cons "x" (sum x y))))))
         (toolchain (make-manifest-toolchain :c-compiler "cc"
                                             :c-flags "-O2"
                                             :library-extension "so"))
         (sexp (build-manifest-sexp
                :problem problem
                :content-hash "0123456789abcdef0123456789abcdef"
                :source-filename "manifest-self-check.lisp"
                :residual-filenames '("residual_chunk_000.c")
                :update-filenames '("update_chunk_000.c")
                :dispatch-filename "dispatch.c"
                :makefile-filename "Makefile"
                :library-filename "libmanifest-self-check.so"
                :toolchain toolchain
                :build-timestamp 12345))
         (text (canonical-sexp-string sexp)))
    (assert (eq :manifest (first sexp)))
    (assert (search "manifest-self-check" text))
    (assert (search "0123456789abcdef" text))
    (assert (search "residual_chunk_000.c" text))
    (assert (search "compute_residual" text)))


  (let* ((tmp-root (format nil "/tmp/cp-index-self-check-~A/"
                           (get-universal-time))))
    (ensure-directories-exist tmp-root)
    (assert (null (read-index-sexp tmp-root)))
    (update-index-sexp tmp-root "alpha" "aaaa")
    (update-index-sexp tmp-root "bravo" "bbbb")
    (update-index-sexp tmp-root "alpha" "cccc")
    (let ((index (read-index-sexp tmp-root)))
      (assert (eq :index (first index)))
      (let ((alpha-entry (find "alpha" (rest index) :key #'car :test #'string=))
            (bravo-entry (find "bravo" (rest index) :key #'car :test #'string=)))
        (assert (string= "cccc" (cdr alpha-entry)) ()
                "second registration must replace the prior hash")
        (assert (string= "bbbb" (cdr bravo-entry)) ()
                "unrelated entries must be preserved")
        (assert (= 2 (length (rest index))) ()
                "no duplicate entries should remain")))))
