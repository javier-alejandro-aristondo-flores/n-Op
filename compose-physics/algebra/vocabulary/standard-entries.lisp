;;; Standard vocabulary entries.
;;;
;;; Registers the canonical numerical functions every physics author is
;;; likely to need: the elementary exponential / logarithmic family, the
;;; circular trig family and its principal-value inverses, the hyperbolic
;;; family and its inverses, and the principal-value square root. Each
;;; entry binds its forward and inverse closures, its libm C identifier,
;;; and (where the inverse is itself a registered vocabulary entry) the
;;; inverse-key back-link used by the algebraic solver.
;;;
;;; All forward and inverse closures are declared (double-float) ->
;;; double-float; the forms after `the double-float` are required so the
;;; SBCL compiler can prove the return type and emit float arithmetic
;;; without boxing.

(in-package #:compose-physics)


(defmacro define-vocabulary-entry (keyword
                                   emission-identifier
                                   forward-expression
                                   &key inverse-key inverse-expression)
  "Register one vocabulary entry. FORWARD-EXPRESSION and (when given)
   INVERSE-EXPRESSION are evaluated against a single double-float
   parameter named X."
  `(register-function
    ,keyword
    (lambda (x)
      (declare (type double-float x)
               (optimize (speed 3) (safety 1)))
      (the double-float ,forward-expression))
    :emission-identifier ,emission-identifier
    :inverse-key ,inverse-key
    :inverse-function
    ,(when inverse-expression
       `(lambda (x)
          (declare (type double-float x)
                   (optimize (speed 3) (safety 1)))
          (the double-float ,inverse-expression)))))


;;; Exponential and logarithmic.

(define-vocabulary-entry :exp "exp" (exp x)
                         :inverse-key :log
                         :inverse-expression (log x))

(define-vocabulary-entry :log "log" (log x)
                         :inverse-key :exp
                         :inverse-expression (exp x))

;;; Principal-value square root. Its inverse on the non-negative reals
;;; is the squaring function, which is not itself a registered entry,
;;; so the inverse-key is nil.

(define-vocabulary-entry :sqrt "sqrt" (sqrt x)
                         :inverse-key nil
                         :inverse-expression (* x x))


;;; Reciprocal. Not a libm function; the codegen path emits an inline
;;; helper named cp_reciprocal in the dispatcher translation unit. The
;;; reciprocal is its own inverse on the non-zero reals, so the
;;; inverse-key back-links to itself and the inverse closure is the
;;; same expression as the forward one. Every algebraic rearrangement
;;; that introduces division does so by wrapping the denominator in
;;; an apply :reciprocal node, never by introducing a new IR primitive.

(define-vocabulary-entry :reciprocal "cp_reciprocal" (/ 1.0d0 x)
                         :inverse-key :reciprocal
                         :inverse-expression (/ 1.0d0 x))


;;; Circular trigonometry and principal-value inverses.

(define-vocabulary-entry :sin "sin" (sin x)
                         :inverse-key :asin
                         :inverse-expression (asin x))

(define-vocabulary-entry :cos "cos" (cos x)
                         :inverse-key :acos
                         :inverse-expression (acos x))

(define-vocabulary-entry :tan "tan" (tan x)
                         :inverse-key :atan
                         :inverse-expression (atan x))

(define-vocabulary-entry :asin "asin" (asin x)
                         :inverse-key :sin
                         :inverse-expression (sin x))

(define-vocabulary-entry :acos "acos" (acos x)
                         :inverse-key :cos
                         :inverse-expression (cos x))

(define-vocabulary-entry :atan "atan" (atan x)
                         :inverse-key :tan
                         :inverse-expression (tan x))


;;; Hyperbolic trigonometry and inverses.

(define-vocabulary-entry :sinh "sinh" (sinh x)
                         :inverse-key :asinh
                         :inverse-expression (asinh x))

(define-vocabulary-entry :cosh "cosh" (cosh x)
                         :inverse-key :acosh
                         :inverse-expression (acosh x))

(define-vocabulary-entry :tanh "tanh" (tanh x)
                         :inverse-key :atanh
                         :inverse-expression (atanh x))

(define-vocabulary-entry :asinh "asinh" (asinh x)
                         :inverse-key :sinh
                         :inverse-expression (sinh x))

(define-vocabulary-entry :acosh "acosh" (acosh x)
                         :inverse-key :cosh
                         :inverse-expression (cosh x))

(define-vocabulary-entry :atanh "atanh" (atanh x)
                         :inverse-key :tanh
                         :inverse-expression (tanh x))


;;; Inline self-checks. Numerical equality uses a small absolute
;;; tolerance to admit machine-precision drift in the libm round-trips.

(eval-when (:load-toplevel :execute)
  (flet ((approximately-equal (left right)
           (< (abs (- left right)) 1.0d-12)))

    ;; Every advertised entry is registered.
    (dolist (key '(:exp :log :sqrt :reciprocal
                   :sin :cos :tan :asin :acos :atan
                   :sinh :cosh :tanh :asinh :acosh :atanh))
      (assert (lookup-function-record key) ()
              "vocabulary entry missing: ~S" key))

    ;; Forward evaluations match the underlying CL implementations.
    (assert (approximately-equal (funcall (lookup-forward-function :exp) 1.0d0)
                                 (exp 1.0d0)))
    (assert (approximately-equal (funcall (lookup-forward-function :sin) 0.5d0)
                                 (sin 0.5d0)))
    (assert (approximately-equal (funcall (lookup-forward-function :cosh) 0.5d0)
                                 (cosh 0.5d0)))

    ;; Forward composed with inverse is identity on a sample point.
    (dolist (pair '((:exp . 0.7d0)
                    (:log . 0.7d0)
                    (:sin . 0.3d0)
                    (:cos . 0.3d0)
                    (:tan . 0.3d0)
                    (:sinh . 0.4d0)
                    (:cosh . 0.6d0)
                    (:tanh . 0.4d0)))
      (let* ((key (car pair))
             (point (cdr pair))
             (forward (lookup-forward-function key))
             (inverse (lookup-inverse-function key)))
        (assert forward () "no forward for ~S" key)
        (assert inverse () "no inverse for ~S" key)
        (assert (approximately-equal (funcall inverse (funcall forward point))
                                     point)
                ()
                "round-trip failed for ~S at ~S" key point)))

    ;; Inverse-key back-links resolve to themselves for paired entries.
    (assert (eq (lookup-inverse-key :exp) :log))
    (assert (eq (lookup-inverse-key :log) :exp))
    (assert (eq (lookup-inverse-key :sin) :asin))
    (assert (eq (lookup-inverse-key :asin) :sin))
    (assert (eq (lookup-inverse-key :cosh) :acosh))

    ;; sqrt has an inverse closure but no inverse-key (square is not
    ;; itself a registered vocabulary entry).
    (assert (null (lookup-inverse-key :sqrt)))
    (assert (approximately-equal
             (funcall (lookup-inverse-function :sqrt)
                      (funcall (lookup-forward-function :sqrt) 9.0d0))
             9.0d0))

    ;; reciprocal is its own inverse and back-links to itself.
    (assert (eq (lookup-inverse-key :reciprocal) :reciprocal))
    (assert (approximately-equal
             (funcall (lookup-forward-function :reciprocal) 4.0d0)
             0.25d0))
    (assert (approximately-equal
             (funcall (lookup-inverse-function :reciprocal)
                      (funcall (lookup-forward-function :reciprocal) 7.0d0))
             7.0d0))

    ;; Emission identifiers match libm names.
    (assert (string= (lookup-emission-identifier :exp) "exp"))
    (assert (string= (lookup-emission-identifier :tanh) "tanh"))
    (assert (string= (lookup-emission-identifier :asinh) "asinh"))))
