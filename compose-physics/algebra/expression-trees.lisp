;;; Funcallable expression-tree IR for compose-physics.
;;;
;;; Five node kinds — term, sum, product, scale, apply — each a funcallable
;;; CLOS instance over a (simple-array double-float (*)) state buffer. The
;;; tree is the only IR: every algebraic transformation downstream produces
;;; trees built from this same primitive set, and every node remains
;;; directly numerically evaluable at every stage of the pipeline.
;;;
;;; This file owns the IR data definitions, a small traversal API, and a
;;; pure-numeric simplifier that flattens associative children and folds
;;; nested scale factors. The simplifier is conservative — it never
;;; introduces a node kind it did not already have, and it never produces
;;; a tree whose evaluation differs from the input's at any state.

(in-package #:compose-physics)


;;; Abstract base. The metaclass is what makes instances funcallable;
;;; concrete subclasses install their per-shape evaluator in
;;; initialize-instance :after via sb-mop:set-funcallable-instance-function.

(defclass expression ()
  ()
  (:metaclass sb-mop:funcallable-standard-class)
  (:documentation
   "Abstract base for every IR node. Subclasses are funcallable instances
    over a (simple-array double-float (*)) state buffer."))


(defgeneric expression-children (expression)
  (:documentation
   "Return the immediate child expressions of EXPRESSION as a list,
    or nil for leaf nodes."))


(defmethod expression-children ((expression expression))
  nil)


(defun ensure-double-float (value)
  (coerce value 'double-float))


(defun ensure-expression (object)
  (check-type object expression)
  object)


;;; term — the only leaf node. Evaluates to coefficient * state[index].
;;; The name slot carries the human-facing slot identifier for diagnostics
;;; and for the with-state binding macro; it is not used at evaluation
;;; time and never appears in C emission (only the index does).

(defclass term (expression)
  ((coefficient :type double-float :initarg :coefficient :reader term-coefficient)
   (index       :type fixnum       :initarg :index       :reader term-index)
   (name        :type string       :initarg :name        :reader term-name))
  (:metaclass sb-mop:funcallable-standard-class))


(defun term-p (object)
  (typep object 'term))


(defmethod initialize-instance :after ((node term) &key)
  (let ((coefficient (term-coefficient node))
        (index (term-index node)))
    (declare (type double-float coefficient)
             (type fixnum index))
    (sb-mop:set-funcallable-instance-function
     node
     (lambda (state-vector)
       (declare (type (simple-array double-float (*)) state-vector)
                (optimize (speed 3) (safety 1)))
       (* coefficient (aref state-vector index))))))


(defun term (coefficient index &key (name ""))
  "Construct a leaf term: COEFFICIENT * state[INDEX]. NAME is a
   human-readable label for diagnostics and authoring macros."
  (check-type index (integer 0))
  (check-type name string)
  (make-instance 'term
                 :coefficient (ensure-double-float coefficient)
                 :index index
                 :name name))


;;; sum — n-ary sum of children. The constructor enforces a non-empty
;;; child list; an empty sum is not a meaningful pointwise residual or
;;; update expression and silently zero-folding it would mask authoring
;;; mistakes.

(defclass sum (expression)
  ((children :type list :initarg :children :reader sum-children))
  (:metaclass sb-mop:funcallable-standard-class))


(defun sum-p (object)
  (typep object 'sum))


(defmethod expression-children ((expression sum))
  (sum-children expression))


(defmethod initialize-instance :after ((node sum) &key)
  (let ((children (sum-children node)))
    (sb-mop:set-funcallable-instance-function
     node
     (lambda (state-vector)
       (declare (type (simple-array double-float (*)) state-vector)
                (optimize (speed 3) (safety 1)))
       (let ((accumulator 0.0d0))
         (declare (type double-float accumulator))
         (dolist (child children accumulator)
           (setf accumulator
                 (+ accumulator
                    (the double-float (funcall child state-vector))))))))))


(defun sum (&rest children)
  "Construct an n-ary sum node. At least one child is required; every
   child must be an expression."
  (when (null children)
    (error "sum requires at least one child expression"))
  (dolist (child children)
    (ensure-expression child))
  (make-instance 'sum :children (copy-list children)))


;;; product — n-ary product of children. Same authoring discipline as sum.

(defclass product (expression)
  ((children :type list :initarg :children :reader product-children))
  (:metaclass sb-mop:funcallable-standard-class))


(defun product-p (object)
  (typep object 'product))


(defmethod expression-children ((expression product))
  (product-children expression))


(defmethod initialize-instance :after ((node product) &key)
  (let ((children (product-children node)))
    (sb-mop:set-funcallable-instance-function
     node
     (lambda (state-vector)
       (declare (type (simple-array double-float (*)) state-vector)
                (optimize (speed 3) (safety 1)))
       (let ((accumulator 1.0d0))
         (declare (type double-float accumulator))
         (dolist (child children accumulator)
           (setf accumulator
                 (* accumulator
                    (the double-float (funcall child state-vector))))))))))


(defun product (&rest children)
  "Construct an n-ary product node. At least one child is required;
   every child must be an expression."
  (when (null children)
    (error "product requires at least one child expression"))
  (dolist (child children)
    (ensure-expression child))
  (make-instance 'product :children (copy-list children)))


;;; scale — constant factor times a single child. Distinct from product
;;; with a constant child because there is no constant-leaf node kind in
;;; the IR; scale carries the constant directly.

(defclass scale (expression)
  ((factor :type double-float :initarg :factor :reader scale-factor)
   (child  :type expression   :initarg :child  :reader scale-child))
  (:metaclass sb-mop:funcallable-standard-class))


(defun scale-p (object)
  (typep object 'scale))


(defmethod expression-children ((expression scale))
  (list (scale-child expression)))


(defmethod initialize-instance :after ((node scale) &key)
  (let ((factor (scale-factor node))
        (child (scale-child node)))
    (declare (type double-float factor))
    (sb-mop:set-funcallable-instance-function
     node
     (lambda (state-vector)
       (declare (type (simple-array double-float (*)) state-vector)
                (optimize (speed 3) (safety 1)))
       (* factor (the double-float (funcall child state-vector)))))))


(defun scale (factor child)
  "Construct a scale node: FACTOR * CHILD where FACTOR is a constant."
  (ensure-expression child)
  (make-instance 'scale
                 :factor (ensure-double-float factor)
                 :child child))


;;; apply — applies a named vocabulary function to its single child.
;;; The forward closure is captured at construction time so evaluation
;;; does not consult the vocabulary registry; the keyword name is
;;; carried for emission and inversion lookups elsewhere in the system.

(defclass apply (expression)
  ((function-name    :type keyword  :initarg :function-name    :reader apply-name)
   (forward-function :type function :initarg :forward-function :reader apply-forward)
   (child            :type expression :initarg :child          :reader apply-child))
  (:metaclass sb-mop:funcallable-standard-class))


(defun apply-p (object)
  (typep object 'apply))


(defmethod expression-children ((expression apply))
  (list (apply-child expression)))


(defmethod initialize-instance :after ((node apply) &key)
  (let ((forward-function (apply-forward node))
        (child (apply-child node)))
    (declare (type function forward-function))
    (sb-mop:set-funcallable-instance-function
     node
     (lambda (state-vector)
       (declare (type (simple-array double-float (*)) state-vector)
                (optimize (speed 3) (safety 1)))
       (funcall forward-function
                (the double-float (funcall child state-vector)))))))


(defun make-apply-node (function-name forward-function child)
  "Low-level apply constructor binding the keyword FUNCTION-NAME to the
   FORWARD-FUNCTION closure over CHILD. The user-facing constructor of
   the same intent — apply, defined in the vocabulary module — resolves
   the closure from the registry; this primitive is for callers that
   already hold a closure in hand (the algebraic solver, in particular,
   constructs apply nodes from inverse closures it just looked up)."
  (check-type function-name keyword)
  (check-type forward-function function)
  (ensure-expression child)
  (make-instance 'apply
                 :function-name function-name
                 :forward-function forward-function
                 :child child))


;;; Traversal. walk-expression invokes VISITOR on every node in pre-order
;;; (parent before children). collect-term-* gather the leaf metadata that
;;; the problem object needs to determine its input width and slot map.

(defun walk-expression (expression visitor)
  "Call VISITOR on EXPRESSION and on every descendant in pre-order."
  (funcall visitor expression)
  (dolist (child (expression-children expression))
    (walk-expression child visitor)))


(defun collect-term-indices (expression)
  "Return the sorted set of state-buffer indices referenced by any
   term leaf in EXPRESSION."
  (let ((indices '()))
    (walk-expression expression
                     (lambda (node)
                       (when (term-p node)
                         (pushnew (term-index node) indices))))
    (sort indices #'<)))


(defun collect-term-names (expression)
  "Return the sorted set of distinct slot names referenced by any
   term leaf in EXPRESSION. Empty names are omitted."
  (let ((names '()))
    (walk-expression expression
                     (lambda (node)
                       (when (and (term-p node)
                                  (plusp (length (term-name node))))
                         (pushnew (term-name node) names :test #'string=))))
    (sort names #'string<)))


;;; Simplification. Strict, conservative, and pure-numeric:
;;;   - flatten nested same-kind sums and products
;;;   - fold scale-of-scale into a single scale with the product factor
;;;   - reduce a unary sum or product to its single child
;;;   - reduce a scale of factor 1.0 to its child
;;;
;;; The simplifier never inspects coefficients of terms, never reassociates
;;; across kinds, and never invents a new node kind. It is safe to call at
;;; any point in the pipeline.

(defgeneric simplify-expression (expression)
  (:documentation
   "Return a simplified expression equivalent to EXPRESSION at every
    state. Conservative: flattening and trivial-arity reductions only."))


(defmethod simplify-expression ((expression expression))
  expression)


(defmethod simplify-expression ((expression term))
  expression)


(defmethod simplify-expression ((expression sum))
  (let ((flattened '()))
    (dolist (raw-child (sum-children expression))
      (let ((child (simplify-expression raw-child)))
        (if (sum-p child)
            (dolist (grandchild (sum-children child))
              (push grandchild flattened))
            (push child flattened))))
    (let ((children (nreverse flattened)))
      (if (= (length children) 1)
          (first children)
          (make-instance 'sum :children children)))))


(defmethod simplify-expression ((expression product))
  (let ((flattened '()))
    (dolist (raw-child (product-children expression))
      (let ((child (simplify-expression raw-child)))
        (if (product-p child)
            (dolist (grandchild (product-children child))
              (push grandchild flattened))
            (push child flattened))))
    (let ((children (nreverse flattened)))
      (if (= (length children) 1)
          (first children)
          (make-instance 'product :children children)))))


(defmethod simplify-expression ((expression scale))
  (let* ((factor (scale-factor expression))
         (simplified-child (simplify-expression (scale-child expression))))
    (cond
      ((= factor 1.0d0)
       simplified-child)
      ((scale-p simplified-child)
       (make-instance 'scale
                      :factor (* factor (scale-factor simplified-child))
                      :child (scale-child simplified-child)))
      (t
       (make-instance 'scale :factor factor :child simplified-child)))))


(defmethod simplify-expression ((expression apply))
  (make-instance 'apply
                 :function-name (apply-name expression)
                 :forward-function (apply-forward expression)
                 :child (simplify-expression (apply-child expression))))


;;; Inline self-checks. Evaluated at load time so any breakage of the
;;; IR contract is caught before downstream files compile against it.

(eval-when (:load-toplevel :execute)
  (let ((state (make-array 3 :element-type 'double-float
                             :initial-contents '(2.0d0 3.0d0 5.0d0))))

    ;; Term evaluation: 4.0 * state[1] = 12.0.
    (let ((expression (term 4.0d0 1 :name "x")))
      (assert (= (funcall expression state) 12.0d0))
      (assert (term-p expression))
      (assert (equal (collect-term-indices expression) '(1)))
      (assert (equal (collect-term-names expression) '("x"))))

    ;; Sum: 2*state[0] + 3*state[1] = 4 + 9 = 13.
    (let ((expression (sum (term 2.0d0 0 :name "a")
                           (term 3.0d0 1 :name "b"))))
      (assert (= (funcall expression state) 13.0d0))
      (assert (sum-p expression))
      (assert (equal (collect-term-indices expression) '(0 1)))
      (assert (equal (collect-term-names expression) '("a" "b"))))

    ;; Product: state[0] * state[2] = 2 * 5 = 10.
    (let ((expression (product (term 1.0d0 0 :name "a")
                               (term 1.0d0 2 :name "c"))))
      (assert (= (funcall expression state) 10.0d0))
      (assert (product-p expression)))

    ;; Scale: -2.0 * (state[0] + state[1]) = -2 * 5 = -10.
    (let ((expression (scale -2.0d0
                             (sum (term 1.0d0 0 :name "a")
                                  (term 1.0d0 1 :name "b")))))
      (assert (= (funcall expression state) -10.0d0))
      (assert (scale-p expression)))

    ;; Apply: identity closure on state[2] yields 5.
    (let ((expression (make-apply-node :identity #'identity (term 1.0d0 2 :name "c"))))
      (assert (= (funcall expression state) 5.0d0))
      (assert (apply-p expression))
      (assert (eq (apply-name expression) :identity)))

    ;; Simplification — flattening of nested sums:
    ;; (sum (sum a b) c)  =>  one sum with three children.
    (let* ((leaf-a (term 1.0d0 0 :name "a"))
           (leaf-b (term 1.0d0 1 :name "b"))
           (leaf-c (term 1.0d0 2 :name "c"))
           (nested (sum (sum leaf-a leaf-b) leaf-c))
           (simplified (simplify-expression nested)))
      (assert (sum-p simplified))
      (assert (= (length (sum-children simplified)) 3))
      (assert (= (funcall nested state) (funcall simplified state))))

    ;; Simplification — scale-of-scale collapse:
    ;; scale 2 (scale 3 t)  =>  scale 6 t.
    (let* ((leaf (term 1.0d0 0 :name "a"))
           (nested (scale 2.0d0 (scale 3.0d0 leaf)))
           (simplified (simplify-expression nested)))
      (assert (scale-p simplified))
      (assert (= (scale-factor simplified) 6.0d0))
      (assert (eq (scale-child simplified) leaf))
      (assert (= (funcall nested state) (funcall simplified state))))

    ;; Simplification — scale of factor 1.0 unwraps.
    (let* ((leaf (term 7.0d0 1 :name "x"))
           (simplified (simplify-expression (scale 1.0d0 leaf))))
      (assert (eq simplified leaf)))

    ;; Simplification — unary sum and product reduce to their child.
    (let* ((leaf (term 1.0d0 2 :name "c")))
      (assert (eq (simplify-expression (sum leaf)) leaf))
      (assert (eq (simplify-expression (product leaf)) leaf)))

    ;; Walk-expression visits every node exactly once in pre-order.
    (let* ((leaf-a (term 1.0d0 0 :name "a"))
           (leaf-b (term 1.0d0 1 :name "b"))
           (root (sum leaf-a leaf-b))
           (visited '()))
      (walk-expression root (lambda (node) (push node visited)))
      (assert (= (length visited) 3))
      (assert (eq (first (last visited)) root)))))
