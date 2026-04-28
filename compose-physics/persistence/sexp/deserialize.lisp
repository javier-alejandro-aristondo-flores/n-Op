;;; Deserialize canonical sexp back into expression trees and problems.
;;;
;;; This is the exact inverse of serialize: any tree produced by
;;; canonicalize-expression and rendered with canonical-sexp-string
;;; can be read back into an evaluation-equivalent IR tree. Children
;;; of sum / product nodes were sorted on the way out, and that
;;; order is preserved on the way back in. Sum and product are
;;; commutative and associative, so a re-canonicalization of the
;;; deserialized tree produces the same canonical form: round-trip
;;; identity holds at the canonical-form level, which is what the
;;; content-hash and registry layers care about.
;;;
;;; Apply nodes carry only the function-name keyword in the canonical
;;; form. The forward closure is recovered from the vocabulary at
;;; deserialization time, so the function must be registered before
;;; deserialize-expression is called. Unknown function names signal
;;; an error.

(in-package #:compose-physics)


(defun %sexp-tag (form)
  "Return the keyword tag of a canonical sexp FORM, or signal an
   error if FORM does not look like a tagged list."
  (unless (and (consp form) (keywordp (first form)))
    (error "deserialize: expected a tagged sexp list, got ~S" form))
  (first form))


(defun deserialize-expression (form)
  "Parse a canonical-sexp FORM into an IR expression tree. The
   inverse of canonicalize-expression up to commutative reordering
   inside sum and product (which is part of the canonical form
   itself, not lost information)."
  (ecase (%sexp-tag form)
    (:term
     (destructuring-bind (tag coefficient index name) form
       (declare (ignore tag))
       (term (coerce coefficient 'double-float)
             index
             :name name)))
    (:sum
     (cl:apply #'sum
               (mapcar #'deserialize-expression (rest form))))
    (:product
     (cl:apply #'product
               (mapcar #'deserialize-expression (rest form))))
    (:scale
     (destructuring-bind (tag factor child-form) form
       (declare (ignore tag))
       (scale (coerce factor 'double-float)
              (deserialize-expression child-form))))
    (:apply
     (destructuring-bind (tag function-name child-form) form
       (declare (ignore tag))
       (unless (lookup-function-record function-name)
         (error "deserialize: function ~S is not registered in the vocabulary"
                function-name))
       (apply function-name (deserialize-expression child-form))))))


(defun deserialize-residual-row (form)
  "Parse a (:residual NAME EXPRESSION) sexp into a residual-row."
  (unless (and (consp form) (eq :residual (first form)) (= 3 (length form)))
    (error "deserialize: expected (:residual NAME EXPRESSION), got ~S" form))
  (destructuring-bind (tag name expression-form) form
    (declare (ignore tag))
    (make-residual-row :name name
                       :expression (deserialize-expression expression-form))))


(defun deserialize-update-row (form)
  "Parse a (:update SLOT-NAME SLOT-INDEX (:explicit | :identity) EXPRESSION)
   sexp into an update-row."
  (unless (and (consp form) (eq :update (first form)) (= 5 (length form)))
    (error "deserialize: expected (:update SLOT-NAME INDEX TAG EXPRESSION), got ~S"
           form))
  (destructuring-bind (tag slot-name slot-index explicit-tag expression-form) form
    (declare (ignore tag))
    (let ((explicit-p (ecase explicit-tag
                        (:explicit t)
                        (:identity nil))))
      (make-update-row :slot-name slot-name
                       :slot-index slot-index
                       :expression (deserialize-expression expression-form)
                       :explicit-p explicit-p))))


(defun deserialize-problem (form)
  "Parse a (:problem NAME (:slots ...) (:residuals ...) (:updates ...))
   sexp back into a problem object. The slot index assignment, residual
   row order, and update row order are all preserved exactly; any
   identity-tagged update rows reconstitute as identity defaults via
   make-problem's normal synthesis path."
  (unless (and (consp form) (eq :problem (first form)) (= 5 (length form)))
    (error "deserialize: expected a (:problem ...) sexp of length 5, got length ~D"
           (and (consp form) (length form))))
  (destructuring-bind (problem-tag problem-name slots-form residuals-form updates-form)
      form
    (declare (ignore problem-tag))
    (unless (and (consp slots-form) (eq :slots (first slots-form)))
      (error "deserialize: missing (:slots ...) sub-form"))
    (unless (and (consp residuals-form) (eq :residuals (first residuals-form)))
      (error "deserialize: missing (:residuals ...) sub-form"))
    (unless (and (consp updates-form) (eq :updates (first updates-form)))
      (error "deserialize: missing (:updates ...) sub-form"))
    (let* ((slot-names (rest slots-form))
           (residual-rows (mapcar #'deserialize-residual-row (rest residuals-form)))
           (update-rows (mapcar #'deserialize-update-row (rest updates-form)))
           (residual-specs
            (mapcar (lambda (row)
                      (cons (residual-row-name row)
                            (residual-row-expression row)))
                    residual-rows))
           (explicit-update-specs
            (loop for row in update-rows
                  when (update-row-explicit-p row)
                  collect (cons (update-row-slot-name row)
                                (update-row-expression row)))))
      (make-problem :name problem-name
                    :slot-names slot-names
                    :residual-specs residual-specs
                    :update-specs explicit-update-specs))))


(defun deserialize-problem-from-string (canonical-string)
  "Parse a canonical-sexp string into a problem object. The inverse
   of canonical-sexp-string applied to a canonicalize-problem result."
  (check-type canonical-string string)
  (let ((*read-default-float-format* 'double-float))
    (deserialize-problem
     (with-input-from-string (stream canonical-string)
       (read stream)))))


(eval-when (:load-toplevel :execute)

  (let* ((tree (sum (term 2.0d0 0 :name "x")
                    (scale -1.0d0 (apply :sin (term 1.0d0 1 :name "y")))
                    (product (term 1.0d0 2 :name "z")
                             (term 3.0d0 0 :name "x"))))
         (canonical (canonicalize-expression tree))
         (round-trip (deserialize-expression canonical))
         (state (make-array 3 :element-type 'double-float
                              :initial-contents '(1.5d0 0.7d0 4.0d0))))
    (assert (= (funcall tree state) (funcall round-trip state)) ()
            "round-trip evaluation must match the original at every state"))


  (let* ((problem
          (with-state (a b)
            (make-problem
             :name "round-trip"
             :slot-names (list "a" "b")
             :residual-specs (list (cons "rel" (sum a (scale -2.0d0 b))))
             :update-specs (list (cons "a" (sum a b))))))
         (canonical-string (canonical-sexp-string (canonicalize-problem problem)))
         (rebuilt (deserialize-problem-from-string canonical-string))
         (rebuilt-canonical-string
          (canonical-sexp-string (canonicalize-problem rebuilt))))
    (assert (string= canonical-string rebuilt-canonical-string) ()
            "deserialize ∘ serialize must be the identity on canonical strings")
    (assert (= 2 (problem-slot-count rebuilt)))
    (assert (= 1 (problem-residual-count rebuilt)))
    (assert (string= "round-trip" (problem-name rebuilt)))
    (let* ((row-a (aref (problem-update-rows rebuilt) 0))
           (row-b (aref (problem-update-rows rebuilt) 1)))
      (assert (update-row-explicit-p row-a) ()
              "explicit update row must round-trip as explicit")
      (assert (not (update-row-explicit-p row-b)) ()
              "identity update row must round-trip as identity")))


  (let* ((tree (apply :sin (term 1.0d0 0 :name "theta")))
         (sexp (canonicalize-expression tree))
         (round-trip (deserialize-expression sexp))
         (state (make-array 1 :element-type 'double-float
                              :initial-contents '(0.5d0))))
    (assert (= (funcall tree state) (funcall round-trip state))))


  (handler-case
      (progn
        (deserialize-expression '(:apply :no-such-function-deserialize-self-check
                                  (:term 1.0d0 0 "x")))
        (error "expected unknown-function error"))
    (error () nil)))
