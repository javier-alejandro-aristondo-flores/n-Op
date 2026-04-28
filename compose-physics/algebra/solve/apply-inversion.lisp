;;; Apply-inversion strategy for solve-for.
;;;
;;; Linear rearrangement handles relations where the target appears
;;; only at the top level of the IR — sums, scaled factors, and
;;; products with at most one target-bearing factor. When the target
;;; sits underneath one or more apply nodes (sin, exp, log, …) we
;;; first peel those layers off using the registered inverses in the
;;; vocabulary, then dispatch the remaining relation to the linear
;;; rearrangement strategy.
;;;
;;; Strategy. Find the outermost apply node in the relation that has
;;; the target somewhere inside it. Verify the relation is linear in
;;; that apply node viewed as a whole, exactly the way linear
;;; rearrangement treats a target slot. Isolate that apply node:
;;;
;;;     coefficient * apply(f, inner) + rest = 0
;;;     apply(f, inner) = -rest / coefficient
;;;
;;; Look up f's registered inverse, call it g. Build the new relation
;;;
;;;     inner - apply(g, -rest / coefficient) = 0
;;;
;;; and recurse. Eventually the target lives outside every apply node
;;; and linear rearrangement closes the deal. Each loop iteration
;;; strips exactly one apply layer, so termination is guaranteed by
;;; the depth of the deepest apply chain wrapping the target.
;;;
;;; The same constraints from linear rearrangement apply to each
;;; layer: at most one target-bearing factor in any product, and the
;;; coefficient of the apply node must be either purely constant or
;;; purely state-dependent (mixed coefficients require a constant-leaf
;;; primitive that the IR does not provide).

(in-package #:compose-physics)


(defun %subtree-contains-p (haystack needle)
  "True if NEEDLE occurs anywhere inside HAYSTACK by EQ identity."
  (let ((found nil))
    (walk-expression haystack
                     (lambda (node)
                       (when (eq node needle)
                         (setf found t))))
    found))


(defun %find-outermost-apply-containing-target (node target-index)
  "Return the highest apply ancestor of any term that references
   TARGET-INDEX, or NIL when TARGET-INDEX is not under any apply.
   Stops at the first apply layer encountered while descending."
  (etypecase node
    (term nil)
    (apply
     (when (%has-target-p node target-index)
       node))
    (scale
     (%find-outermost-apply-containing-target
      (scale-child node) target-index))
    (sum
     (some (lambda (child)
             (%find-outermost-apply-containing-target child target-index))
           (sum-children node)))
    (product
     (some (lambda (child)
             (%find-outermost-apply-containing-target child target-index))
           (product-children node)))))


(defun %linearize-against-subtree (tree target-subtree
                                   residual-name target-slot-name)
  "Return (cc, sd, r) such that

     tree(s) = (cc + sd(s)) * target-subtree(s) + r(s)

   for every state s, with sd and r target-subtree-free. EQ identity
   on TARGET-SUBTREE is the membership test, mirroring how
   %linearize uses (term-index = target-index)."
  (when (eq tree target-subtree)
    (return-from %linearize-against-subtree
      (values 1.0d0 nil nil)))

  (etypecase tree

    (term
     (values 0.0d0 nil tree))

    (sum
     (let ((accumulated-constant 0.0d0)
           (state-dep-pieces '())
           (rest-pieces '()))
       (dolist (child (sum-children tree))
         (multiple-value-bind (cc sd r)
             (%linearize-against-subtree child target-subtree
                                         residual-name target-slot-name)
           (incf accumulated-constant cc)
           (when sd (push sd state-dep-pieces))
           (when r  (push r  rest-pieces))))
       (values accumulated-constant
               (%sum-or-nil (nreverse state-dep-pieces))
               (%sum-or-nil (nreverse rest-pieces)))))

    (scale
     (let ((factor (scale-factor tree)))
       (multiple-value-bind (cc sd r)
           (%linearize-against-subtree (scale-child tree) target-subtree
                                       residual-name target-slot-name)
         (values (* factor cc)
                 (%scale-or-nil factor sd)
                 (%scale-or-nil factor r)))))

    (product
     (let ((target-bearing-children '())
           (target-free-children '()))
       (dolist (child (product-children tree))
         (if (%subtree-contains-p child target-subtree)
             (push child target-bearing-children)
             (push child target-free-children)))
       (let ((bearing-count (length target-bearing-children)))
         (cond

           ((zerop bearing-count)
            (values 0.0d0 nil tree))

           ((= bearing-count 1)
            (let* ((bearing (first target-bearing-children))
                   (free-product (%product-or-nil
                                  (nreverse target-free-children))))
              (multiple-value-bind (cc sd r)
                  (%linearize-against-subtree bearing target-subtree
                                              residual-name target-slot-name)
                (when (and (not (zerop cc)) (null free-product))
                  (return-from %linearize-against-subtree
                    (values cc sd r)))
                (let* ((combined-coefficient
                        (%sum-or-nil
                         (list
                          (when (and (not (zerop cc)) free-product)
                            (%scale-or-nil cc free-product))
                          (when sd
                            (if free-product
                                (product sd free-product)
                                sd)))))
                       (combined-rest
                        (when r
                          (if free-product
                              (product r free-product)
                              r))))
                  (values 0.0d0 combined-coefficient combined-rest)))))

           (t
            (signal-solve-failure
             'solve-product-multiple-target-factors
             residual-name target-slot-name
             (format nil "product carries ~D factors that reference the apply subtree being inverted"
                     bearing-count)
             :factor-count bearing-count))))))

    (apply
     ;; Apply nodes other than target-subtree may not contain it; if
     ;; they do, target-subtree wasn't actually outermost, which
     ;; signals a logic error in find-outermost rather than a user
     ;; problem. Treat it as solve-unsupported-shape defensively.
     (if (%subtree-contains-p tree target-subtree)
         (signal-solve-failure
          'solve-unsupported-shape
          residual-name target-slot-name
          (format nil "apply :~A node nests another apply that contains the target; outermost-apply selection is inconsistent"
                  (apply-name tree)))
         (values 0.0d0 nil tree)))))


(defun %isolate-subtree (relation target-subtree residual-name target-slot-name)
  "Solve RELATION = 0 for TARGET-SUBTREE, returning the expression
   the subtree must equal. Mirrors solve-linear-for's case grid but
   operates on an arbitrary apply subtree as the unknown."
  (multiple-value-bind (cc sd r)
      (%linearize-against-subtree relation target-subtree
                                  residual-name target-slot-name)
    (when (and (zerop cc) (null sd))
      (signal-solve-failure
       'solve-unsupported-shape
       residual-name target-slot-name
       "apply subtree dropped out of the linearized relation; the relation is not linear in it"))
    (when (and (not (zerop cc)) sd)
      (signal-solve-failure
       'solve-unsupported-shape
       residual-name target-slot-name
       (format nil "linear coefficient of the apply subtree mixes a non-zero constant (~F) with a state-dependent expression; the IR cannot represent the combined coefficient"
               cc)))
    (cond
      ((and (not (zerop cc)) (null sd))
       (let ((negated-inverse (- (/ 1.0d0 cc))))
         (cond
           ((null r)
            ;; coefficient * X = 0  =>  X = 0. Build a zero expression
            ;; via any term scaled by zero; pick a target-free term to
            ;; avoid pulling target back in. Use the constant-zero
            ;; expression seeded against the apply subtree's child.
            (scale 0.0d0 (apply-child target-subtree)))
           (t
            (simplify-expression (scale negated-inverse r))))))
      ((and (zerop cc) sd)
       (cond
         ((null r)
          (scale 0.0d0 (apply-child target-subtree)))
         (t
          (simplify-expression
           (product (scale -1.0d0 r) (apply :reciprocal sd)))))))))


(defun %peel-one-apply-layer (relation outer-apply
                              residual-name target-slot-name)
  "Strip OUTER-APPLY off RELATION. Returns the new relation in which
   the apply layer has been replaced by the inverse-applied
   right-hand side."
  (let* ((apply-keyword (apply-name outer-apply))
         (record (lookup-function-record apply-keyword))
         (inverse-key (and record (function-record-inverse-key record))))
    (unless inverse-key
      (signal-solve-failure
       'solve-no-registered-inverse
       residual-name target-slot-name
       (format nil "no inverse registered for apply :~A; cannot peel layer"
               apply-keyword)
       :function-name apply-keyword))
    (let* ((isolated-rhs (%isolate-subtree relation outer-apply
                                           residual-name target-slot-name))
           (inverted-rhs (apply inverse-key isolated-rhs))
           (inner (apply-child outer-apply)))
      (sum inner (scale -1.0d0 inverted-rhs)))))


(defun solve-for (relation target-index target-slot-name residual-name)
  "Rearrange RELATION = 0 to isolate the slot at TARGET-INDEX,
   peeling apply layers from the outside in until linear
   rearrangement can finish the job. Returns an expression
   equivalent to state_next[TARGET-INDEX] using only IR primitives
   plus apply :reciprocal and the registered inverses encountered."
  (check-type relation expression)
  (check-type target-slot-name string)
  (check-type residual-name string)
  (let ((occurrences (count-target-occurrences relation target-index)))
    (cond
      ((zerop occurrences)
       (signal-solve-failure
        'solve-target-not-found
        residual-name target-slot-name
        (format nil "slot ~S does not appear in the relation"
                target-slot-name)))
      ((> occurrences 1)
       (signal-solve-failure
        'solve-target-has-multiple-occurrences
        residual-name target-slot-name
        (format nil "slot ~S appears ~D times in the relation; only single-occurrence inversion is supported"
                target-slot-name occurrences)
        :occurrence-count occurrences))))
  (let ((current-relation relation))
    (loop
      (let ((outermost-apply
             (%find-outermost-apply-containing-target
              current-relation target-index)))
        (when (null outermost-apply)
          (return-from solve-for
            (solve-linear-for current-relation target-index
                              target-slot-name residual-name)))
        (setf current-relation
              (%peel-one-apply-layer current-relation outermost-apply
                                     residual-name target-slot-name))))))


;;; Inline self-checks. Each scenario constructs a relation, calls
;;; solve-for, substitutes the result back into the original
;;; relation, and verifies the relation evaluates to (approximately)
;;; zero on a sample state.

(eval-when (:load-toplevel :execute)

  (flet ((approximately-equal (left right)
           (< (abs (- left right)) 1.0d-9))
         (substitute-into (state target-index value)
           (let ((copy (copy-seq state)))
             (setf (aref copy target-index) value)
             copy)))

    ;; Single-layer inversion. Slots: x (0), y (1).
    ;; Relation: sin(x) - y = 0, target = x. Expected x = asin(y).
    (let* ((state (make-array 2 :element-type 'double-float
                                :initial-contents '(0.123d0 0.5d0)))
           (target-x (term 1.0d0 0 :name "x"))
           (slot-y   (term 1.0d0 1 :name "y"))
           (relation (sum (apply :sin target-x)
                          (scale -1.0d0 slot-y)))
           (solution (solve-for relation 0 "x" "sine-test"))
           (solved (funcall solution state)))
      (assert (approximately-equal solved (asin 0.5d0)) ()
              "sine inversion produced ~F, expected asin(0.5)" solved)
      (assert (approximately-equal
               (funcall relation (substitute-into state 0 solved))
               0.0d0)
              ()
              "sine inversion: residual not zero after substitution"))

    ;; Single layer with non-trivial inner expression. Slots: x (0),
    ;; y (1), z (2). Relation: exp(2*x + y) - z = 0, target = x.
    ;; Expected: 2*x + y = log(z) → x = (log(z) - y)/2.
    (let* ((state (make-array 3 :element-type 'double-float
                                :initial-contents '(0.0d0 1.0d0 7.389056098930649d0)))
           (target-x (term 1.0d0 0 :name "x"))
           (slot-y   (term 1.0d0 1 :name "y"))
           (slot-z   (term 1.0d0 2 :name "z"))
           (relation (sum (apply :exp (sum (scale 2.0d0 target-x)
                                           slot-y))
                          (scale -1.0d0 slot-z)))
           (solution (solve-for relation 0 "x" "exp-test"))
           (solved (funcall solution state)))
      ;; log(7.389056...) ≈ 2.0; (2.0 - 1.0)/2 = 0.5.
      (assert (approximately-equal solved 0.5d0) ()
              "exp inversion produced ~F, expected 0.5" solved)
      (assert (approximately-equal
               (funcall relation (substitute-into state 0 solved))
               0.0d0)
              ()
              "exp inversion: residual not zero after substitution"))

    ;; Two nested layers. Slots: x (0), y (1).
    ;; Relation: sin(cos(x)) - y = 0, target = x.
    ;; Expected x = acos(asin(y)).
    (let* ((y-value 0.4d0)
           (state (make-array 2 :element-type 'double-float
                                :initial-contents (list 0.0d0 y-value)))
           (target-x (term 1.0d0 0 :name "x"))
           (slot-y   (term 1.0d0 1 :name "y"))
           (relation (sum (apply :sin (apply :cos target-x))
                          (scale -1.0d0 slot-y)))
           (solution (solve-for relation 0 "x" "nested-test"))
           (solved (funcall solution state))
           (expected (acos (asin y-value))))
      (assert (approximately-equal solved expected) ()
              "nested inversion produced ~F, expected ~F" solved expected)
      (assert (approximately-equal
               (funcall relation (substitute-into state 0 solved))
               0.0d0)
              ()
              "nested inversion: residual not zero after substitution"))

    ;; Linear-only fallthrough. solve-for must dispatch to
    ;; solve-linear-for when target is not under any apply.
    (let* ((state (make-array 2 :element-type 'double-float
                                :initial-contents '(99.0d0 4.0d0)))
           (relation (sum (scale 2.0d0 (term 1.0d0 0 :name "x"))
                          (scale -1.0d0 (term 1.0d0 1 :name "y"))))
           (solution (solve-for relation 0 "x" "linear-fallthrough-test"))
           (solved (funcall solution state)))
      (assert (approximately-equal solved 2.0d0) ()
              "linear fallthrough produced ~F, expected 2.0" solved))

    ;; No registered inverse rejects loudly. Register a one-off
    ;; vocabulary entry without an inverse and try to peel it.
    (let ((existing (lookup-function-record :nopinverse)))
      (unless existing
        (register-function :nopinverse (lambda (x) x)
                           :emission-identifier "nop")))
    (let* ((target-x (term 1.0d0 0 :name "x"))
           (slot-y   (term 1.0d0 1 :name "y"))
           (relation (sum (apply :nopinverse target-x)
                          (scale -1.0d0 slot-y))))
      (handler-case
          (progn
            (solve-for relation 0 "x" "no-inverse-test")
            (assert nil () "expected solve-no-registered-inverse"))
        (solve-no-registered-inverse (condition)
          (assert (eq (solve-no-registered-inverse-function-name condition)
                      :nopinverse)))))

    ;; Multiple-occurrence rejection. Target appears twice.
    (let* ((target-x (term 1.0d0 0 :name "x"))
           (target-x-again (term 1.0d0 0 :name "x"))
           (relation (sum target-x target-x-again)))
      (handler-case
          (progn
            (solve-for relation 0 "x" "multi-occurrence-test")
            (assert nil () "expected solve-target-has-multiple-occurrences"))
        (solve-target-has-multiple-occurrences (condition)
          (assert (= (solve-failure-occurrence-count condition) 2)))))))
