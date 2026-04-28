;;; The registry orchestrator.
;;;
;;; register-problem is the single entry point the Python CLI and
;;; programmatic Lisp callers hit. It composes every other module
;;; in the persistence and emission layers into one operation:
;;;
;;;   1. compute the canonical sexp + content hash.
;;;   2. lay out the problem directory under the registry root.
;;;   3. dispose of the user's source file per --source-dest.
;;;   4. write the three sexp files (problem, residual, update).
;;;   5. emit chunked C sources, dispatch.c, and a Makefile.
;;;   6. write manifest.sexp.
;;;   7. update the root-level index.sexp.
;;;
;;; The orchestrator does not invoke the C compiler. The Python
;;; CLI runs `make` against the produced directory; programmatic
;;; callers can do the same with uiop:run-program if they want.
;;; Splitting the build out of this function keeps the Lisp side
;;; pure-functional over the registry state.

(in-package #:compose-physics)


(defstruct registration-result
  (content-hash       "" :type string :read-only t)
  (problem-directory  "" :type string :read-only t)
  (manifest-pathname  "" :type string :read-only t)
  (library-filename   "" :type string :read-only t)
  (chunk-filenames    '() :type list  :read-only t))


(defun %ensure-trailing-slash (path-string)
  "Return PATH-STRING with a trailing slash, adding one if missing."
  (if (or (zerop (length path-string))
          (eql #\/ (char path-string (1- (length path-string)))))
      path-string
      (concatenate 'string path-string "/")))


(defun %problem-directory (registry-root content-hash)
  "Build the problem directory pathname (as a string with trailing
   slash) under REGISTRY-ROOT for CONTENT-HASH."
  (concatenate 'string
               (%ensure-trailing-slash (namestring registry-root))
               content-hash
               "/"))


(defun %write-chunk-source (chunk problem-directory)
  "Write CHUNK's text into PROBLEM-DIRECTORY/<filename>."
  (let ((path (concatenate 'string
                           problem-directory
                           (chunk-source-filename chunk))))
    (with-open-file (stream path
                            :direction :output
                            :if-exists :supersede
                            :if-does-not-exist :create)
      (write-string (chunk-source-text chunk) stream))
    path))


(defun register-problem (problem
                         &key
                           registry-root
                           source-pathname
                           (source-disposition *default-source-disposition*)
                           (chunk-row-count *default-chunk-row-count*)
                           (c-compiler *default-c-compiler*)
                           (c-flags *default-c-flags*)
                           (library-extension *default-shared-library-extension*))
  "Materialize PROBLEM under REGISTRY-ROOT as a self-contained
   problem directory and return a registration-result describing
   the layout. The build itself (make / cc) is not run here; that
   is the Python CLI's responsibility."
  (check-type problem problem)
  (check-type registry-root (or string pathname))
  (check-type source-disposition source-disposition-tag)
  (when source-pathname
    (check-type source-pathname (or string pathname)))
  (let* ((canonical-string
          (canonical-sexp-string (canonicalize-problem problem)))
         (content-hash (content-hash-string canonical-string))
         (problem-directory
          (%problem-directory registry-root content-hash))
         (residual-chunks
          (emit-residual-chunks problem :chunk-row-count chunk-row-count))
         (update-chunks
          (emit-update-chunks problem :chunk-row-count chunk-row-count))
         (dispatch-text
          (emit-dispatch-c problem
                           :residual-chunks residual-chunks
                           :update-chunks update-chunks))
         (makefile-text
          (emit-makefile problem
                         :residual-chunks residual-chunks
                         :update-chunks update-chunks
                         :library-stem (problem-name problem)
                         :c-compiler c-compiler
                         :c-flags c-flags
                         :library-extension library-extension))
         (library-filename
          (format nil "lib~A.~A" (problem-name problem) library-extension))
         (residual-filenames
          (mapcar #'chunk-source-filename residual-chunks))
         (update-filenames
          (mapcar #'chunk-source-filename update-chunks)))

    (ensure-directories-exist problem-directory)

    (let ((source-target-filename
           (when source-pathname
             (let ((target-pathname
                    (handle-source-file source-pathname
                                        problem-directory
                                        source-disposition)))
               (and target-pathname (file-namestring target-pathname))))))

      (serialize-problem-to-file
       problem
       (concatenate 'string problem-directory "problem.sexp"))
      (serialize-residual-rows-to-file
       problem
       (concatenate 'string problem-directory "residual.sexp"))
      (serialize-update-rows-to-file
       problem
       (concatenate 'string problem-directory "update.sexp"))

      (dolist (chunk residual-chunks)
        (%write-chunk-source chunk problem-directory))
      (dolist (chunk update-chunks)
        (%write-chunk-source chunk problem-directory))

      (with-open-file (stream
                       (concatenate 'string problem-directory "dispatch.c")
                       :direction :output
                       :if-exists :supersede
                       :if-does-not-exist :create)
        (write-string dispatch-text stream))
      (with-open-file (stream
                       (concatenate 'string problem-directory "Makefile")
                       :direction :output
                       :if-exists :supersede
                       :if-does-not-exist :create)
        (write-string makefile-text stream))

      (let* ((toolchain (make-manifest-toolchain
                         :c-compiler c-compiler
                         :c-flags c-flags
                         :library-extension library-extension))
             (manifest-sexp
              (build-manifest-sexp
               :problem problem
               :content-hash content-hash
               :source-filename source-target-filename
               :residual-filenames residual-filenames
               :update-filenames update-filenames
               :dispatch-filename "dispatch.c"
               :makefile-filename "Makefile"
               :library-filename library-filename
               :toolchain toolchain
               :build-timestamp (get-universal-time)))
             (manifest-pathname
              (concatenate 'string problem-directory "manifest.sexp")))
        (write-manifest-to-file manifest-sexp manifest-pathname)
        (update-index-sexp registry-root (problem-name problem) content-hash)
        (make-registration-result
         :content-hash content-hash
         :problem-directory problem-directory
         :manifest-pathname manifest-pathname
         :library-filename library-filename
         :chunk-filenames (append residual-filenames update-filenames))))))


(eval-when (:load-toplevel :execute)

  (let* ((registry-root (format nil "/tmp/cp-registry-self-check-~A/"
                                (get-universal-time)))
         (problem
          (with-state (x y)
            (make-problem
             :name "registry-self-check"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "balance" (sum x (scale -1.0d0 y))))
             :update-specs (list (cons "x" (sum x y))))))
         (result (register-problem problem :registry-root registry-root)))

    (let ((problem-directory (registration-result-problem-directory result)))
      (assert (probe-file (concatenate 'string problem-directory "problem.sexp")))
      (assert (probe-file (concatenate 'string problem-directory "residual.sexp")))
      (assert (probe-file (concatenate 'string problem-directory "update.sexp")))
      (assert (probe-file (concatenate 'string problem-directory "dispatch.c")))
      (assert (probe-file (concatenate 'string problem-directory "Makefile")))
      (assert (probe-file (concatenate 'string problem-directory "residual_chunk_000.c")))
      (assert (probe-file (concatenate 'string problem-directory "update_chunk_000.c")))
      (assert (probe-file (registration-result-manifest-pathname result)))


      (let ((process
             (sb-ext:run-program "/usr/bin/env"
                                 (list "make" "-C" problem-directory "-j")
                                 :output :stream
                                 :error :stream
                                 :wait t)))
        (assert (zerop (sb-ext:process-exit-code process))))
      (assert (probe-file (concatenate 'string
                                       problem-directory
                                       (registration-result-library-filename result)))))


    (let ((index (read-index-sexp registry-root)))
      (assert (find "registry-self-check" (rest index)
                    :key #'car :test #'string=)
              ()
              "registered problem must appear in index.sexp"))


    (let* ((tmp-source (format nil "~Aregistry-with-source-input.lisp"
                               registry-root)))
      (ensure-directories-exist tmp-source)
      (with-open-file (stream tmp-source
                              :direction :output
                              :if-exists :supersede
                              :if-does-not-exist :create)
        (format stream ";; placeholder source file for self-check~%"))
      (let ((problem
             (with-state (a b)
               (make-problem
                :name "registry-with-source"
                :slot-names (list "a" "b")
                :residual-specs (list (cons "r" (sum a b)))
                :update-specs nil))))
        (let ((result (register-problem
                       problem
                       :registry-root registry-root
                       :source-pathname tmp-source
                       :source-disposition :copy)))
          (assert (probe-file
                   (concatenate 'string
                                (registration-result-problem-directory result)
                                "registry-with-source-input.lisp")))
          (assert (probe-file tmp-source) ()
                  ":copy must preserve the original"))))))
