;;; Stream and file IO for canonical sexp persistence.
;;;
;;; Serialization is the file-IO half of the persistence layer.
;;; The canonical sexp form itself is built by canonicalize.lisp;
;;; this file's job is to write that form to streams and files
;;; with byte-identical output and to expose the per-form file
;;; layout (residual.sexp, update.sexp, problem.sexp) used by the
;;; registry orchestrator.
;;;
;;; A persisted problem directory contains three sexp files. Each
;;; is the canonical sexp string of one viewpoint:
;;;
;;;   residual.sexp : the K residual rows, in declared order.
;;;   update.sexp   : the N update rows, in slot-index order, with
;;;                   identity defaults tagged distinctly from
;;;                   author-explicit rows.
;;;   problem.sexp  : the whole problem (slot map + residual + update),
;;;                   the form whose hash is the problem's identity.
;;;
;;; The three files are deterministic functions of the problem; the
;;; same problem produces the same bytes every time.

(in-package #:compose-physics)


(defun %write-canonical-sexp-line (canonical-sexp stream)
  "Write CANONICAL-SEXP to STREAM as a single line followed by a
   newline. The newline is part of the canonical surface so that
   the file ends with a trailing newline (POSIX convention) without
   introducing any internal whitespace."
  (write-string (canonical-sexp-string canonical-sexp) stream)
  (terpri stream))


(defun serialize-residual-rows-to-stream (problem stream)
  "Write the canonical sexp form of PROBLEM's residual rows to
   STREAM. The form is a list whose first element is :residuals and
   whose remaining elements are per-row canonical sexps."
  (check-type problem problem)
  (let ((sexp
         (cons :residuals
               (mapcar #'canonicalize-residual-row
                       (coerce (problem-residual-rows problem) 'list)))))
    (%write-canonical-sexp-line sexp stream)))


(defun serialize-update-rows-to-stream (problem stream)
  "Write the canonical sexp form of PROBLEM's update rows to STREAM."
  (check-type problem problem)
  (let ((sexp
         (cons :updates
               (mapcar #'canonicalize-update-row
                       (coerce (problem-update-rows problem) 'list)))))
    (%write-canonical-sexp-line sexp stream)))


(defun serialize-problem-to-stream (problem stream)
  "Write the canonical sexp form of the entire PROBLEM to STREAM."
  (check-type problem problem)
  (%write-canonical-sexp-line (canonicalize-problem problem) stream))


(defun serialize-problem-to-file (problem pathname)
  "Write the canonical sexp form of PROBLEM to PATHNAME, creating
   intermediate directories as needed and replacing any existing
   file."
  (check-type problem problem)
  (ensure-directories-exist pathname)
  (with-open-file (stream pathname
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (serialize-problem-to-stream problem stream)))


(defun serialize-residual-rows-to-file (problem pathname)
  "Write PROBLEM's residual rows in canonical form to PATHNAME."
  (ensure-directories-exist pathname)
  (with-open-file (stream pathname
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (serialize-residual-rows-to-stream problem stream)))


(defun serialize-update-rows-to-file (problem pathname)
  "Write PROBLEM's update rows in canonical form to PATHNAME."
  (ensure-directories-exist pathname)
  (with-open-file (stream pathname
                          :direction :output
                          :if-exists :supersede
                          :if-does-not-exist :create)
    (serialize-update-rows-to-stream problem stream)))


(eval-when (:load-toplevel :execute)

  (let* ((problem
          (with-state (x y)
            (make-problem
             :name "serialize-self-check"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "balance" (sum x (scale -1.0d0 y))))
             :update-specs (list (cons "x" (sum x y)))))))

    (let ((round-trip (with-output-to-string (stream)
                        (serialize-problem-to-stream problem stream))))
      (assert (search "(:problem \"serialize-self-check\"" round-trip))
      (assert (search "(:slots \"x\" \"y\")" round-trip))
      (assert (search "(:residual \"balance\"" round-trip))
      (assert (eql #\Newline
                   (char round-trip (1- (length round-trip))))))

    (let ((residual-text (with-output-to-string (stream)
                           (serialize-residual-rows-to-stream problem stream)))
          (update-text   (with-output-to-string (stream)
                           (serialize-update-rows-to-stream problem stream))))
      (assert (search "(:residuals (:residual \"balance\"" residual-text))
      (assert (search "(:update \"x\" 0 :explicit" update-text))
      (assert (search "(:update \"y\" 1 :identity" update-text)))


    (let* ((tmp-dir (format nil "/tmp/cp-serialize-selfcheck-~A/"
                            (get-universal-time)))
           (problem-path (concatenate 'string tmp-dir "problem.sexp"))
           (residual-path (concatenate 'string tmp-dir "residual.sexp"))
           (update-path (concatenate 'string tmp-dir "update.sexp")))
      (serialize-problem-to-file problem problem-path)
      (serialize-residual-rows-to-file problem residual-path)
      (serialize-update-rows-to-file problem update-path)
      (assert (probe-file problem-path))
      (assert (probe-file residual-path))
      (assert (probe-file update-path))


      (let ((again-1 (with-output-to-string (stream)
                       (serialize-problem-to-stream problem stream)))
            (again-2 (with-output-to-string (stream)
                       (serialize-problem-to-stream problem stream))))
        (assert (string= again-1 again-2) ()
                "serialization must be byte-deterministic")))))
