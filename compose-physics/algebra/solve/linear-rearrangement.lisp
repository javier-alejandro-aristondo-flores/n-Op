;;; Linear rearrangement strategy for solve-for.
;;;
;;; Given a relation R(state) = 0 and a target slot index t, this module
;;; rearranges R into the form
;;;
;;;     state_next[t] = -rest(state) / coefficient(state)
;;;
;;; whenever R is linear in state[t]. Both the constant and the
;;; state-dependent coefficient cases are handled, the latter by wrapping
;;; the denominator in (apply :reciprocal ...). The IR is never extended:
;;; division is purely a vocabulary entry, and every output expression is
;;; built from the same five primitives the input was.
;;;
;;; Restrictions, all signaled with the corresponding solve-failure
;;; subclass:
;;;
;;;   - The target must appear at least once.
;;;   - The target must not appear under an apply node (apply-inversion
;;;     handles that case as a separate strategy).
;;;   - A product node may carry at most one target-bearing factor;
;;;     more than one would generate a target^2 term that is not
;;;     representable in the IR.
;;;   - The linear coefficient must be either purely constant or purely
;;;     state-dependent. A relation whose linear coefficient mixes both
;;;     a non-zero constant and a non-empty state-dependent expression
;;;     would require representing a constant as an additive expression,
;;;     which the IR cannot do without a constant-leaf primitive.
;;;
;;; The dispatcher in apply-inversion.lisp peels apply layers from the
;;; outside before invoking this strategy on the inner linear core.

(in-package #:compose-physics)


(defun count-target-occurrences (expression target-index)
  "Return the number of term leaves in EXPRESSION whose index equals
   TARGET-INDEX."
  (let ((count 0))
    (walk-expression
     expression
     (lambda (node)
       (when (and (term-p node) (= (term-index node) target-index))
         (incf count))))
    count))


(defun %has-target-p (expression target-index)
  (plusp (count-target-occurrences expression target-index)))


;;; Constructors that tolerate nil-as-zero. The internal linearization
;;; carries optional sub-expressions (nil meaning "the additive zero");
;;; these helpers re-materialize them only when needed and never leave
;;; an empty sum or a degenerate scale-by-one in the result.

(defun %sum-or-nil (expressions)
  (let ((non-empty (remove nil expressions)))
    (cond
      ((null non-empty) nil)
      ((null (cdr non-empty)) (first non-empty))
      (t (cl:apply #'sum non-empty)))))


(defun %product-or-nil (expressions)
  (let ((non-empty (remove nil expressions)))
    (cond
      ((null non-empty) nil)
      ((null (cdr non-empty)) (first non-empty))
      (t (cl:apply #'product non-empty)))))


(defun %scale-or-nil (factor expression)
  (cond
    ((null expression) nil)
    ((= factor 1.0d0) expression)
    (t (scale factor expression))))


(defun %zero-expression-for-target (target-index target-name)
  "An expression that evaluates to 0 at every state, used when the
   solved relation reduces to target = 0. Phrased as scaling the unit
   target term by 0 so the resulting tree contains only IR primitives."
  (scale 0.0d0 (term 1.0d0 target-index :name target-name)))


;;; Linearization. Walks the relation tree and partitions it into the
;;; constant linear coefficient, the state-dependent linear coefficient,
;;; and the target-free remainder.

(defun %linearize (tree target-index residual-name target-slot-name)
  "Return three values: CONSTANT-COEF (double-float), STATE-DEP-COEF
   (expression or nil), and REST (expression or nil), such that

     tree(s) = (CONSTANT-COEF + state-dep-coef(s)) * s[target-index]
               + rest(s)

   for every state s. STATE-DEP-COEF and REST are guaranteed
   target-free. Signals a solve-failure subclass when TREE is not
   linear in the target by this strategy's rules."
  (etypecase tree

    (term
     (if (= (term-index tree) target-index)
         (values (term-coefficient tree) nil nil)
         (values 0.0d0 nil tree)))

    (sum
     (let ((accumulated-constant 0.0d0)
           (state-dep-pieces '())
           (rest-pieces '()))
       (dolist (child (sum-children tree))
         (multiple-value-bind (cc sd r)
             (%linearize child target-index residual-name target-slot-name)
           (incf accumulated-constant cc)
           (when sd (push sd state-dep-pieces))
           (when r  (push r  rest-pieces))))
       (values accumulated-constant
               (%sum-or-nil (nreverse state-dep-pieces))
               (%sum-or-nil (nreverse rest-pieces)))))

    (scale
     (let ((factor (scale-factor tree)))
       (multiple-value-bind (cc sd r)
           (%linearize (scale-child tree) target-index
                       residual-name target-slot-name)
         (values (* factor cc)
                 (%scale-or-nil factor sd)
                 (%scale-or-nil factor r)))))

    (product
     (let ((target-bearing-children '())
           (target-free-children '()))
       (dolist (child (product-children tree))
         (if (%has-target-p child target-index)
             (push child target-bearing-children)
             (push child target-free-children)))
       (let ((bearing-count (length target-bearing-children)))
         (cond

           ;; No factor mentions the target — the whole product is rest.
           ((zerop bearing-count)
            (values 0.0d0 nil tree))

           ;; Exactly one factor contains the target. Linearize that
           ;; factor; multiply its (cc, sd, r) pieces by the product of
           ;; the target-free factors. The result's constant-coefficient
           ;; portion is necessarily zero because multiplying a constant
           ;; by a state-dependent expression yields a state-dependent
           ;; expression, not a constant.
           ((= bearing-count 1)
            (let* ((bearing (first target-bearing-children))
                   (free-product (%product-or-nil
                                  (nreverse target-free-children))))
              (multiple-value-bind (cc sd r)
                  (%linearize bearing target-index
                              residual-name target-slot-name)
                (let* ((combined-coefficient
                        (%sum-or-nil
                         (list
                          ;; cc * free-product, materialized as a
                          ;; scaled copy of the free-product factor.
                          (when (and (not (zerop cc)) free-product)
                            (%scale-or-nil cc free-product))
                          ;; sd * free-product.
                          (when sd
                            (if free-product
                                (product sd free-product)
                                sd)))))
                       (combined-rest
                        (when r
                          (if free-product
                              (product r free-product)
                              r))))
                  (when (and (not (zerop cc)) (null free-product))
                    ;; The bearing factor was itself the whole product
                    ;; (no target-free factors). Constant coefficient
                    ;; survives as cc; defer it to the constant return.
                    (return-from %linearize
                      (values cc sd combined-rest)))
                  (values 0.0d0 combined-coefficient combined-rest)))))

           ;; Two or more target-bearing factors imply target^2 or
           ;; higher in the product, which the IR cannot represent.
           (t
            (signal-solve-failure
             'solve-product-multiple-target-factors
             residual-name target-slot-name
             (format nil "product carries ~D factors that reference target slot ~S; only one is supported"
                     bearing-count target-slot-name)
             :factor-count bearing-count))))))

    (apply
     ;; Apply containing the target is the apply-inversion strategy's
     ;; responsibility, not this one.
     (if (%has-target-p tree target-index)
         (signal-solve-failure
          'solve-non-linear-in-target
          residual-name target-slot-name
          (format nil "target slot ~S appears under an apply :~A node, which is non-linear; use the apply-inversion path"
                  target-slot-name (apply-name tree)))
         (values 0.0d0 nil tree)))))


;;; Public entry point. Builds the solved expression for the target.

(defun solve-linear-for (relation target-index target-slot-name residual-name)
  "Rearrange RELATION = 0 to isolate the slot at TARGET-INDEX.

   Returns an expression equivalent to state_next[TARGET-INDEX], built
   from the IR primitives plus apply :reciprocal where division by a
   state-dependent denominator is required. Signals a solve-failure
   subclass when the relation is not amenable to linear rearrangement
   in the target."
  (check-type relation expression)
  (check-type target-slot-name string)
  (check-type residual-name string)
  (multiple-value-bind (constant-coefficient state-dep-coefficient rest)
      (%linearize relation target-index residual-name target-slot-name)

    (when (and (zerop constant-coefficient) (null state-dep-coefficient))
      (signal-solve-failure
       'solve-target-not-found
       residual-name target-slot-name
       (format nil "target slot ~S does not appear linearly anywhere in the relation"
               target-slot-name)))

    (when (and (not (zerop constant-coefficient)) state-dep-coefficient)
      (signal-solve-failure
       'solve-unsupported-shape
       residual-name target-slot-name
       (format nil "linear coefficient of ~S mixes a non-zero constant (~F) with a state-dependent expression; this case requires a constant-leaf primitive that the IR does not provide"
               target-slot-name constant-coefficient)))

    (cond

      ;; Pure constant coefficient. Solution: target = -rest / cc.
      ((and (not (zerop constant-coefficient)) (null state-dep-coefficient))
       (let ((negated-inverse (- (/ 1.0d0 constant-coefficient))))
         (if (null rest)
             (%zero-expression-for-target target-index target-slot-name)
             (simplify-expression (scale negated-inverse rest)))))

      ;; Pure state-dependent coefficient. Solution:
      ;;   target = -rest * (1 / state-dep-coefficient).
      ((and (zerop constant-coefficient) state-dep-coefficient)
       (if (null rest)
           (%zero-expression-for-target target-index target-slot-name)
           (simplify-expression
            (product (scale -1.0d0 rest)
                     (apply :reciprocal state-dep-coefficient))))))))


;;; Inline self-checks. Each scenario evaluates the original relation
;;; and the solved expression at a sample state and verifies the
;;; relation equals zero when the target slot is replaced by the
;;; solved value.

(eval-when (:load-toplevel :execute)

  ;; Helper: evaluate EXPRESSION against STATE, where STATE has the
  ;; target slot replaced by the value REPLACEMENT-EVALUATES-TO. We
  ;; substitute by overwriting the buffer in place, which suffices
  ;; for these closed self-checks.
  (flet ((approximately-equal (left right)
           (< (abs (- left right)) 1.0d-10))
         (with-target-replaced (state-template target-index replacement-value)
           (let ((copy (copy-seq state-template)))
             (setf (aref copy target-index) replacement-value)
             copy)))

    ;; Constant-coefficient case. Slots: x (0), y (1). Relation:
    ;;     2*x + 3*y - 6 -- but no constant leaves; encode the "-6"
    ;; as a state-derived expression: assume slot c (2) holds 6.0
    ;; in the test state. Relation: 2*x + 3*y - c = 0.
    ;; Target = x. Expected: x = (c - 3*y) / 2.
    (let* ((slots #("x" "y" "c"))
           (declare-slots-used slots)
           (state (make-array 3 :element-type 'double-float
                                :initial-contents '(99.0d0 4.0d0 6.0d0)))
           (relation (sum
                      (term 2.0d0 0 :name "x")
                      (term 3.0d0 1 :name "y")
                      (scale -1.0d0 (term 1.0d0 2 :name "c"))))
           (solution (solve-linear-for relation 0 "x" "constant-test")))
      (declare (ignore declare-slots-used))
      (let* ((solved-value (funcall solution state))
             (with-target-replaced (with-target-replaced state 0 solved-value)))
        (assert (approximately-equal (funcall relation with-target-replaced) 0.0d0)
                ()
                "constant-coefficient case: residual not zero after substitution")))

    ;; State-dependent-coefficient case. Slots: v_next (0), v (1),
    ;; a (2), m (3), dt (4). Relation: m*v_next - m*v - a*dt = 0.
    ;; Target = v_next. Expected: v_next = (m*v + a*dt) / m = v + a*dt/m.
    (let* ((state (make-array 5 :element-type 'double-float
                                :initial-contents '(99.0d0 3.0d0 -1.0d0 4.0d0 0.1d0)))
           (term-v-next (term 1.0d0 0 :name "v_next"))
           (term-v      (term 1.0d0 1 :name "v"))
           (term-a      (term 1.0d0 2 :name "a"))
           (term-m      (term 1.0d0 3 :name "m"))
           (term-dt     (term 1.0d0 4 :name "dt"))
           (relation (sum (product term-m term-v-next)
                          (scale -1.0d0 (product term-m term-v))
                          (scale -1.0d0 (product term-a term-dt))))
           (solution (solve-linear-for relation 0 "v_next" "state-dep-test")))
      (let* ((solved-value (funcall solution state))
             (substituted (let ((copy (copy-seq state)))
                            (setf (aref copy 0) solved-value)
                            copy)))
        ;; Expected solved value: 3 + (-1)*0.1/4 = 3 - 0.025 = 2.975.
        (assert (approximately-equal solved-value 2.975d0)
                ()
                "state-dependent case: solved value ~F differs from 2.975" solved-value)
        (assert (approximately-equal (funcall relation substituted) 0.0d0)
                ()
                "state-dependent case: residual not zero after substitution")))

    ;; Multi-term linear case (legacy single-branch case generalized).
    ;; Slots: a (0), b (1), c (2). Relation: 2*a - 3*a + a*5 - b - c = 0.
    ;; Coefficient of a is 2 - 3 + 5 = 4; rest is -b - c.
    ;; Expected: a = (b + c) / 4.
    (let* ((state (make-array 3 :element-type 'double-float
                                :initial-contents '(99.0d0 8.0d0 4.0d0)))
           (term-a (term 1.0d0 0 :name "a"))
           (term-b (term 1.0d0 1 :name "b"))
           (term-c (term 1.0d0 2 :name "c"))
           (relation (sum
                      (scale 2.0d0 term-a)
                      (scale -3.0d0 term-a)
                      (scale 5.0d0 term-a)
                      (scale -1.0d0 term-b)
                      (scale -1.0d0 term-c)))
           (solution (solve-linear-for relation 0 "a" "multi-term-test")))
      (let ((solved-value (funcall solution state)))
        (assert (approximately-equal solved-value 3.0d0)
                ()
                "multi-term case: solved value ~F differs from 3.0" solved-value)))

    ;; Failure case: target absent from relation.
    (let ((relation (sum (term 1.0d0 0 :name "x") (term 1.0d0 1 :name "y"))))
      (handler-case
          (progn
            (solve-linear-for relation 2 "z" "absent-test")
            (assert nil () "expected solve-target-not-found"))
        (solve-target-not-found () nil)))

    ;; Failure case: product with two target-bearing factors.
    (let* ((target (term 1.0d0 0 :name "x"))
           (relation (sum (product target target)
                          (scale -1.0d0 (term 1.0d0 1 :name "y")))))
      (handler-case
          (progn
            (solve-linear-for relation 0 "x" "x-squared-test")
            (assert nil () "expected solve-product-multiple-target-factors"))
        (solve-product-multiple-target-factors (condition)
          (assert (= (solve-failure-factor-count condition) 2)))))

    ;; Failure case: target under an apply node.
    (let* ((target (term 1.0d0 0 :name "x"))
           (relation (sum (apply :sin target)
                          (scale -1.0d0 (term 1.0d0 1 :name "y")))))
      (handler-case
          (progn
            (solve-linear-for relation 0 "x" "apply-target-test")
            (assert nil () "expected solve-non-linear-in-target"))
        (solve-non-linear-in-target () nil)))

    ;; Failure case: mixed constant and state-dependent coefficient.
    ;; Slots: x (0), m (1). Relation: 2*x + m*x - y = 0 with y at 2.
    ;; Coefficient of x is 2 (constant) + m (state-dep). The IR cannot
    ;; represent this combination, so solve-unsupported-shape fires.
    (let* ((target (term 1.0d0 0 :name "x"))
           (m      (term 1.0d0 1 :name "m"))
           (y      (term 1.0d0 2 :name "y"))
           (relation (sum (scale 2.0d0 target)
                          (product m target)
                          (scale -1.0d0 y))))
      (handler-case
          (progn
            (solve-linear-for relation 0 "x" "mixed-coefficient-test")
            (assert nil () "expected solve-unsupported-shape"))
        (solve-unsupported-shape () nil)))))
