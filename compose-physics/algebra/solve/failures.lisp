;;; Named condition types for the algebraic solver.
;;;
;;; The solver refuses any case it cannot rearrange cleanly; it never
;;; invents a placeholder, and it never silently emits a degraded form.
;;; Every refusal signals a named condition that carries the residual
;;; name and target slot name in its slots so the surrounding tooling
;;; (CLI, validator, programmatic users) can identify the failing
;;; relation without parsing report strings.
;;;
;;; The condition hierarchy is shallow on purpose: solve-failure is the
;;; base class consumers should specialize against, and each
;;; sub-condition names a single rearrangement strategy that gave up.

(in-package #:compose-physics)


(define-condition solve-failure (error)
  ((residual-name
    :type string
    :initarg :residual-name
    :reader solve-failure-residual-name
    :documentation
    "Name of the residual or update relation the solver was inverting.")
   (target-slot-name
    :type string
    :initarg :target-slot-name
    :reader solve-failure-target-slot-name
    :documentation
    "Slot name the solver was trying to isolate as state_next[i].")
   (reason
    :type string
    :initform ""
    :initarg :reason
    :reader solve-failure-reason
    :documentation
    "Human-readable explanation; used in the report and surfaced by
     the CLI verbatim alongside the condition class name."))
  (:report
   (lambda (condition stream)
     (format stream
             "solve-for failed on residual ~S for target slot ~S: ~A"
             (solve-failure-residual-name condition)
             (solve-failure-target-slot-name condition)
             (solve-failure-reason condition))))
  (:documentation
   "Abstract base for every solver refusal. Subclasses name the
    specific rearrangement strategy that gave up."))


(define-condition solve-target-not-found (solve-failure)
  ()
  (:documentation
   "The target slot does not appear in any term of the relation, so
    there is nothing to isolate."))


(define-condition solve-target-has-multiple-occurrences (solve-failure)
  ((occurrence-count
    :type fixnum
    :initarg :occurrence-count
    :reader solve-failure-occurrence-count))
  (:documentation
   "The target slot appears in more than one branch of a sum at depths
    that the linear-rearrangement strategy cannot collapse into a single
    coefficient. Generalizing this case would require symbolic algebra,
    which is out of scope."))


(define-condition solve-non-linear-in-target (solve-failure)
  ()
  (:documentation
   "The relation is not linear in the target slot — for example, the
    target appears under a non-invertible composite or as a factor on
    both sides of a product the solver cannot split cleanly."))


(define-condition solve-product-multiple-target-factors (solve-failure)
  ((factor-count
    :type fixnum
    :initarg :factor-count
    :reader solve-failure-factor-count))
  (:documentation
   "A product node has more than one target-bearing factor. Solving
    this in the non-symbolic IR would require introducing a square or
    higher-power node, which is not in the primitive set."))


(define-condition solve-no-registered-inverse (solve-failure)
  ((function-name
    :type keyword
    :initarg :function-name
    :reader solve-no-registered-inverse-function-name))
  (:documentation
   "An apply node sits between the surface of the relation and the
    target, but the named vocabulary function has no inverse closure
    registered. The author must register an inverse via
    register-function or rewrite the relation."))


(define-condition solve-unsupported-shape (solve-failure)
  ()
  (:documentation
   "The relation has a shape that none of the supported rearrangement
    strategies recognize. A symbolic algebra system might handle it; the
    solver, by design, does not."))


(defun signal-solve-failure (condition-class
                             residual-name target-slot-name reason
                             &rest extra-initargs)
  "Signal CONDITION-CLASS with the residual and target-slot context
   filled in. EXTRA-INITARGS are forwarded to the condition's
   make-condition call for subclass-specific slots
   (e.g. :occurrence-count, :function-name)."
  (check-type residual-name string)
  (check-type target-slot-name string)
  (check-type reason string)
  (cl:apply #'error condition-class
            :residual-name residual-name
            :target-slot-name target-slot-name
            :reason reason
            extra-initargs))


;;; Inline self-checks. Confirm the condition hierarchy resolves and
;;; that signal-solve-failure surfaces the named subtype.

(eval-when (:load-toplevel :execute)

  ;; Every named subtype is reachable as solve-failure.
  (dolist (subtype '(solve-target-not-found
                     solve-target-has-multiple-occurrences
                     solve-non-linear-in-target
                     solve-product-multiple-target-factors
                     solve-no-registered-inverse
                     solve-unsupported-shape))
    (assert (subtypep subtype 'solve-failure) ()
            "~S should be a subtype of solve-failure" subtype))

  ;; signal-solve-failure dispatches to the right class and carries
  ;; the supplied context.
  (handler-case
      (signal-solve-failure 'solve-target-not-found
                            "newton" "v1"
                            "v1 does not appear in newton")
    (solve-target-not-found (condition)
      (assert (string= (solve-failure-residual-name condition) "newton"))
      (assert (string= (solve-failure-target-slot-name condition) "v1"))
      (assert (search "v1" (solve-failure-reason condition))))
    (error () (assert nil () "wrong condition class signaled")))

  ;; Subclass-specific slots are forwarded through extra-initargs.
  (handler-case
      (signal-solve-failure 'solve-no-registered-inverse
                            "law" "x"
                            "no inverse for :weird"
                            :function-name :weird)
    (solve-no-registered-inverse (condition)
      (assert (eq (solve-no-registered-inverse-function-name condition)
                  :weird)))
    (error () (assert nil () "wrong condition class for inverse failure")))

  ;; The abstract base class catches every subclass.
  (handler-case
      (signal-solve-failure 'solve-target-has-multiple-occurrences
                            "law" "x"
                            "x appears in two sum branches"
                            :occurrence-count 2)
    (solve-failure (condition)
      (assert (= (solve-failure-occurrence-count condition) 2)))))
