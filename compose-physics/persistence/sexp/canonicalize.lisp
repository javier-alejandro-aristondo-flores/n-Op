;;; Canonical sexp form for problems and expression trees.
;;;
;;; Canonicalization defines the byte-identical surface that the
;;; content hash is computed against and that consumers compare for
;;; equality. Two problems whose canonical sexps are byte-identical
;;; are by construction the same problem.
;;;
;;; Canonical form rules:
;;;
;;;   - Every node is a list whose first element is a keyword tag
;;;     mirroring its IR class (:term, :sum, :product, :scale, :apply,
;;;     :residual, :update, :problem). The tag is the type.
;;;   - String identifiers (term name, residual name, slot name,
;;;     problem name) are lower-cased so that source-file casing does
;;;     not perturb the hash.
;;;   - Children of commutative nodes (sum, product) are sorted by the
;;;     printed form of their canonical sexp. Sorting is the only thing
;;;     that distinguishes canonicalize from a naive serializer.
;;;   - Floating-point values are emitted as Lisp double-float literals
;;;     (the printer's standard "1.0d0" form). prin1-to-string of a
;;;     double-float is reader-stable on SBCL, which is sufficient for
;;;     content-hash determinism.
;;;
;;; The canonical sexp is a Lisp datum, not a string. canonical-sexp-string
;;; renders one with pretty-printing disabled, case downcased, and
;;; *print-readably* bound true so that deserialize can recover the
;;; original tree exactly.

(in-package #:compose-physics)


(defun %canonicalize-string (raw-string)
  "Lower-case RAW-STRING for canonical comparison. The result is a
   fresh string; the input is not mutated."
  (check-type raw-string string)
  (string-downcase raw-string))


(defun %sort-canonical-children (canonical-children)
  "Return CANONICAL-CHILDREN as a list sorted by the printed form
   of each child. Used for sum and product, the two commutative
   primitive shapes."
  (let ((annotated
         (mapcar (lambda (canonical-child)
                   (cons (prin1-to-string canonical-child) canonical-child))
                 canonical-children)))
    (mapcar #'cdr
            (sort annotated #'string< :key #'car))))


(defgeneric canonicalize-expression (expression)
  (:documentation
   "Return the canonical sexp form of EXPRESSION. Result is a
    list-tree of keywords, numbers, strings, and other lists."))


(defmethod canonicalize-expression ((expression term))
  (list :term
        (term-coefficient expression)
        (term-index expression)
        (%canonicalize-string (term-name expression))))


(defmethod canonicalize-expression ((expression sum))
  (cons :sum
        (%sort-canonical-children
         (mapcar #'canonicalize-expression
                 (sum-children expression)))))


(defmethod canonicalize-expression ((expression product))
  (cons :product
        (%sort-canonical-children
         (mapcar #'canonicalize-expression
                 (product-children expression)))))


(defmethod canonicalize-expression ((expression scale))
  (list :scale
        (scale-factor expression)
        (canonicalize-expression (scale-child expression))))


(defmethod canonicalize-expression ((expression apply))
  (list :apply
        (apply-name expression)
        (canonicalize-expression (apply-child expression))))


(defun canonicalize-residual-row (row)
  "Return the canonical sexp form of a residual row."
  (check-type row residual-row)
  (list :residual
        (%canonicalize-string (residual-row-name row))
        (canonicalize-expression (residual-row-expression row))))


(defun canonicalize-update-row (row)
  "Return the canonical sexp form of an update row. Identity-default
   rows are tagged distinctly from author-explicit rows so the hash
   is stable against synthesis order."
  (check-type row update-row)
  (list :update
        (%canonicalize-string (update-row-slot-name row))
        (update-row-slot-index row)
        (if (update-row-explicit-p row) :explicit :identity)
        (canonicalize-expression (update-row-expression row))))


(defun canonicalize-problem (problem)
  "Return the canonical sexp form of PROBLEM. Slot names are
   lower-cased but not reordered: the slot index is part of the
   problem's identity. Residual and update rows are emitted in
   their declared order, which is also part of identity (the
   hash is over the full problem, not a multiset)."
  (check-type problem problem)
  (list :problem
        (%canonicalize-string (problem-name problem))
        (cons :slots
              (map 'list #'%canonicalize-string
                   (problem-slot-names problem)))
        (cons :residuals
              (mapcar #'canonicalize-residual-row
                      (coerce (problem-residual-rows problem) 'list)))
        (cons :updates
              (mapcar #'canonicalize-update-row
                      (coerce (problem-update-rows problem) 'list)))))


(defun canonical-sexp-string (canonical-sexp)
  "Render CANONICAL-SEXP as a deterministic, reader-stable string.
   Pretty-printing is disabled; case is downcased; readably is
   bound true so floating-point literals print with their type
   tag and so all values round-trip through the reader."
  (let ((*print-pretty* nil)
        (*print-case* :downcase)
        (*print-readably* t)
        (*print-circle* nil)
        (*print-escape* t))
    (prin1-to-string canonical-sexp)))


(eval-when (:load-toplevel :execute)

  (let* ((leaf-x (term 1.0d0 0 :name "X"))
         (canonical (canonicalize-expression leaf-x)))
    (assert (equal canonical '(:term 1.0d0 0 "x")) ()
            "expected lower-cased term: ~S" canonical)
    (assert (string= (canonical-sexp-string canonical) "(:term 1.0d0 0 \"x\")")))


  (let* ((tree-1 (sum (term 1.0d0 0 :name "x")
                      (term 1.0d0 1 :name "y")))
         (tree-2 (sum (term 1.0d0 1 :name "y")
                      (term 1.0d0 0 :name "x"))))
    (assert (equal (canonicalize-expression tree-1)
                   (canonicalize-expression tree-2))
            ()
            "sum children must canonicalize to a sorted list"))


  (let* ((nested (sum (product (term 1.0d0 0 :name "x")
                               (term 1.0d0 1 :name "y"))
                      (product (term 1.0d0 1 :name "y")
                               (term 1.0d0 0 :name "x"))))
         (canonical (canonicalize-expression nested)))
    (assert (eq (first canonical) :sum))
    (assert (= (length (rest canonical)) 2))
    (assert (equal (first (rest canonical)) (second (rest canonical))) ()
            "products with reordered children must collapse under canonicalization"))


  (let* ((scaled (scale 2.5d0 (term 3.0d0 0 :name "z"))))
    (assert (equal (canonicalize-expression scaled)
                   '(:scale 2.5d0 (:term 3.0d0 0 "z")))))


  (let* ((applied (apply :sin (term 1.0d0 0 :name "x"))))
    (assert (equal (canonicalize-expression applied)
                   '(:apply :sin (:term 1.0d0 0 "x")))))


  (let* ((problem
          (with-state (x y)
            (make-problem
             :name "Canonical-Test"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "Balance" (sum y x)))
             :update-specs (list (cons "x" (sum x y))))))
         (canonical (canonicalize-problem problem))
         (text (canonical-sexp-string canonical)))
    (assert (eq (first canonical) :problem))
    (assert (string= (second canonical) "canonical-test"))
    (assert (search "\"x\"" text))
    (assert (search "(:residual \"balance\"" text))
    (assert (search "(:update \"x\" 0 :explicit" text))
    (assert (search "(:update \"y\" 1 :identity" text)))


  (let* ((problem-1
          (with-state (x y)
            (make-problem
             :name "ordering"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum x y)))
             :update-specs nil)))
         (problem-2
          (with-state (x y)
            (make-problem
             :name "ordering"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum y x)))
             :update-specs nil))))
    (assert (string= (canonical-sexp-string (canonicalize-problem problem-1))
                     (canonical-sexp-string (canonicalize-problem problem-2)))
            ()
            "two equivalent problems must produce byte-identical canonical strings")))
