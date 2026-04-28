;;; Vocabulary registry — function-record struct, registration API, lookup.
;;;
;;; Named numerical functions (sin, cos, exp, log, sqrt, ...) are the IR's
;;; only extensibility point. Each entry binds a keyword to a record that
;;; carries everything four downstream consumers need:
;;;
;;;   - the funcallable IR (forward closure, used at evaluation time)
;;;   - the algebraic solver (inverse closure plus inverse-key back-link,
;;;     used to invert nested apply chains during update-rule derivation)
;;;   - C emission (the C identifier written into generated source)
;;;   - persistence (the keyword itself, written into the canonical sexp)
;;;
;;; The registry is a single hash table guarded by SBCL's per-table
;;; synchronization. Standard entries are loaded by standard-entries.lisp;
;;; users extend the vocabulary at any time via register-function.

(in-package #:compose-physics)


(defstruct function-record
  (forward-function    nil :type function)
  (inverse-function    nil :type (or function null))
  (emission-identifier ""  :type string)
  (inverse-key         nil :type (or keyword null)))


(defvar *function-registry*
  (make-hash-table :test 'eq :synchronized t)
  "Singleton vocabulary registry. Keys are keywords; values are
   function-record instances. Writes and reads are coordinated by
   the table's per-bucket lock.")


(defun register-function (name forward-function
                          &key inverse-function
                               (emission-identifier "")
                               inverse-key)
  "Register or replace a vocabulary entry under the keyword NAME.

   FORWARD-FUNCTION is the (double-float) -> double-float closure used
   at IR evaluation time and is required.

   INVERSE-FUNCTION is the (double-float) -> double-float closure used
   by the algebraic solver to invert nested apply chains; it may be
   omitted for one-way functions.

   EMISSION-IDENTIFIER is the C identifier written into generated
   source. The empty default is intentionally invalid for emission and
   must be overridden by any function that participates in codegen.

   INVERSE-KEY is the keyword of the inverse entry, recorded for the
   solver's back-link. May be omitted.

   Returns the function-record stored in the registry."
  (check-type name keyword)
  (check-type forward-function function)
  (check-type emission-identifier string)
  (when inverse-function
    (check-type inverse-function function))
  (when inverse-key
    (check-type inverse-key keyword))
  (let ((record (make-function-record
                 :forward-function forward-function
                 :inverse-function inverse-function
                 :emission-identifier emission-identifier
                 :inverse-key inverse-key)))
    (setf (gethash name *function-registry*) record)
    record))


(defun lookup-function-record (name)
  "Return the function-record registered under the keyword NAME, or
   nil if no such entry exists."
  (check-type name keyword)
  (gethash name *function-registry*))


(defun lookup-forward-function (name)
  "Return the forward closure for NAME, or nil."
  (let ((record (lookup-function-record name)))
    (and record (function-record-forward-function record))))


(defun lookup-inverse-function (name)
  "Return the inverse closure for NAME, or nil if NAME is not
   registered or the entry has no inverse."
  (let ((record (lookup-function-record name)))
    (and record (function-record-inverse-function record))))


(defun lookup-emission-identifier (name)
  "Return the C identifier registered for NAME, or nil."
  (let ((record (lookup-function-record name)))
    (and record (function-record-emission-identifier record))))


(defun lookup-inverse-key (name)
  "Return the inverse-entry keyword registered for NAME, or nil."
  (let ((record (lookup-function-record name)))
    (and record (function-record-inverse-key record))))


(defun vocabulary-keys ()
  "Return the list of keyword names currently registered, sorted by
   their symbol-name for deterministic output."
  (let ((keys '()))
    (maphash (lambda (key value)
               (declare (ignore value))
               (push key keys))
             *function-registry*)
    (sort keys #'string< :key #'symbol-name)))


;;; User-facing apply constructor. Resolves the forward closure from
;;; the registry so authors write (apply :sin x) without holding a
;;; closure themselves. Internal callers that already have a closure
;;; in hand (the algebraic solver, principally) call make-apply-node
;;; from expression-trees.lisp directly.

(defun apply (function-name child)
  "Construct an apply node for the registered keyword FUNCTION-NAME
   over CHILD. Signals an error if no vocabulary entry is registered
   under FUNCTION-NAME at call time."
  (check-type function-name keyword)
  (let ((forward (lookup-forward-function function-name)))
    (unless forward
      (error "no vocabulary entry registered under keyword ~S" function-name))
    (make-apply-node function-name forward child)))


;;; Inline self-checks. The registry is global, so we register entries
;;; under reserved test keywords and remove them afterwards to keep the
;;; standard vocabulary in standard-entries.lisp authoritative.

(eval-when (:load-toplevel :execute)
  (let ((forward (lambda (value)
                   (declare (type double-float value))
                   (* 2.0d0 value)))
        (inverse (lambda (value)
                   (declare (type double-float value))
                   (* 0.5d0 value))))

    (let ((record (register-function :--self-check-double
                                     forward
                                     :inverse-function inverse
                                     :emission-identifier "self_check_double"
                                     :inverse-key :--self-check-half)))
      (assert (function-record-p record))
      (assert (eq (function-record-forward-function record) forward))
      (assert (eq (function-record-inverse-function record) inverse))
      (assert (string= (function-record-emission-identifier record)
                       "self_check_double"))
      (assert (eq (function-record-inverse-key record) :--self-check-half)))

    (assert (eq (lookup-forward-function :--self-check-double) forward))
    (assert (eq (lookup-inverse-function :--self-check-double) inverse))
    (assert (string= (lookup-emission-identifier :--self-check-double)
                     "self_check_double"))
    (assert (eq (lookup-inverse-key :--self-check-double)
                :--self-check-half))
    (assert (null (lookup-function-record :--self-check-not-registered)))
    (assert (null (lookup-forward-function :--self-check-not-registered)))
    (assert (member :--self-check-double (vocabulary-keys)))

    ;; Replacement: re-registering the same keyword overwrites cleanly.
    (let ((replacement (lambda (value)
                         (declare (type double-float value))
                         (+ value 1.0d0))))
      (register-function :--self-check-double replacement
                         :emission-identifier "self_check_replaced")
      (assert (eq (lookup-forward-function :--self-check-double) replacement))
      (assert (string= (lookup-emission-identifier :--self-check-double)
                       "self_check_replaced"))
      (assert (null (lookup-inverse-function :--self-check-double))))

    (remhash :--self-check-double *function-registry*)
    (assert (null (lookup-function-record :--self-check-double)))))
