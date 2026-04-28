;;; Source-file disposition for the registry.
;;;
;;; When a problem is registered from a Lisp source file, the
;;; --source-dest flag governs what happens to that file. Three
;;; behaviors are supported:
;;;
;;;   :move   the source file is moved into the problem directory.
;;;           Default. The author's working directory ends up clean.
;;;   :copy   the source file is duplicated into the problem
;;;           directory and left untouched at its original path.
;;;   :leave  the source file is not touched. The problem directory
;;;           does not include a copy of it. Useful when the file is
;;;           under version control and the registry is treated as
;;;           a derived artifact directory.
;;;
;;; Programmatic registration (no source-file path supplied) skips
;;; this whole step.

(in-package #:compose-physics)


(deftype source-disposition-tag () '(member :move :copy :leave))


(defparameter *default-source-disposition* :move
  "The default behavior for the user's input .lisp file when
   registering from a path. Matches the CLI default. Programmatic
   API callers may override per registration call.")


(defun %target-pathname-for-source (source-pathname target-directory)
  "Return the target pathname under TARGET-DIRECTORY for the file
   at SOURCE-PATHNAME, preserving the original filename."
  (merge-pathnames (file-namestring source-pathname)
                   (pathname target-directory)))


(defun handle-source-file (source-pathname target-directory disposition)
  "Apply DISPOSITION to SOURCE-PATHNAME relative to TARGET-DIRECTORY
   and return the pathname inside the registry where the source now
   lives, or nil if disposition is :leave (no copy in the registry).

   :move   the file is renamed into the registry directory; the
           original path no longer exists.
   :copy   the file is duplicated; both paths exist afterward.
   :leave  the registry directory is unchanged."
  (check-type source-pathname (or string pathname))
  (check-type target-directory (or string pathname))
  (check-type disposition source-disposition-tag)
  (ensure-directories-exist target-directory)
  (let* ((source-truename (truename source-pathname))
         (target-pathname
          (%target-pathname-for-source source-truename target-directory)))
    (ecase disposition
      (:leave
       nil)
      (:copy
       (uiop:copy-file source-truename target-pathname)
       target-pathname)
      (:move
       (uiop:copy-file source-truename target-pathname)
       (delete-file source-truename)
       target-pathname))))


(eval-when (:load-toplevel :execute)

  (let* ((tmp-root (format nil "/tmp/cp-source-handling-~A/"
                           (get-universal-time)))
         (work-dir (concatenate 'string tmp-root "work/"))
         (registry-dir (concatenate 'string tmp-root "registry/")))
    (ensure-directories-exist work-dir)
    (ensure-directories-exist registry-dir)


    (let ((src (concatenate 'string work-dir "leave.lisp")))
      (with-open-file (stream src
                              :direction :output
                              :if-does-not-exist :create
                              :if-exists :supersede)
        (write-string ";; leave self-check" stream))
      (let ((result (handle-source-file src registry-dir :leave)))
        (assert (null result))
        (assert (probe-file src) ()
                "leave must not touch the original")
        (assert (not (probe-file
                      (concatenate 'string registry-dir "leave.lisp"))) ()
                "leave must not write into the registry")))


    (let ((src (concatenate 'string work-dir "copy.lisp")))
      (with-open-file (stream src
                              :direction :output
                              :if-does-not-exist :create
                              :if-exists :supersede)
        (write-string ";; copy self-check" stream))
      (let ((result (handle-source-file src registry-dir :copy)))
        (assert (probe-file src) ()
                "copy must keep the original")
        (assert (probe-file result) ()
                "copy must produce a target file")
        (assert (string= (file-namestring result) "copy.lisp"))))


    (let ((src (concatenate 'string work-dir "move.lisp")))
      (with-open-file (stream src
                              :direction :output
                              :if-does-not-exist :create
                              :if-exists :supersede)
        (write-string ";; move self-check" stream))
      (let ((result (handle-source-file src registry-dir :move)))
        (assert (not (probe-file src)) ()
                "move must remove the original")
        (assert (probe-file result) ()
                "move must produce a target file")))))
