;;; Three-mass / four-spring chain — validation problem for compose-physics.
;;;
;;;   wall - k - m - k - m - k - m - k - wall
;;;             x1      x2      x3
;;;
;;; State (13 slots referenced by some expression):
;;;   x1, x2, x3, v1, v2, v3, a1, a2, a3, m, k, dt, t
;;;
;;; Residuals (K = 3): Newton's second law at each mass.
;;;   m*a1 - k*(x2 - 2*x1)        = 0
;;;   m*a2 - k*(x1 + x3 - 2*x2)   = 0
;;;   m*a3 - k*(x2 - 2*x3)        = 0
;;;
;;; Updates: semi-implicit (symplectic) Euler.

(defpackage :three-mass-four-spring
  (:use :common-lisp :compose-physics)
  (:shadowing-import-from :compose-physics #:apply))

(in-package :three-mass-four-spring)


(defun reciprocal-mass (m)
  (apply :reciprocal m))


(defparameter cl-user::*problem*
  (with-state (x1 x2 x3 v1 v2 v3 a1 a2 a3 m k dt time)

    (let* ((two-x1 (scale 2.0d0 x1))
           (two-x2 (scale 2.0d0 x2))
           (two-x3 (scale 2.0d0 x3))

           (residual-x1
            (sum (product m a1)
                 (scale -1.0d0
                        (product k (sum x2 (scale -1.0d0 two-x1))))))
           (residual-x2
            (sum (product m a2)
                 (scale -1.0d0
                        (product k (sum x1 x3 (scale -1.0d0 two-x2))))))
           (residual-x3
            (sum (product m a3)
                 (scale -1.0d0
                        (product k (sum x2 (scale -1.0d0 two-x3))))))

           (v1-next (sum v1 (product a1 dt)))
           (v2-next (sum v2 (product a2 dt)))
           (v3-next (sum v3 (product a3 dt)))

           (x1-next (sum x1 (product v1-next dt)))
           (x2-next (sum x2 (product v2-next dt)))
           (x3-next (sum x3 (product v3-next dt)))

           (k-over-m (product k (reciprocal-mass m)))

           (a1-next
            (product k-over-m
                     (sum x2-next (scale -1.0d0 (scale 2.0d0 x1-next)))))
           (a2-next
            (product k-over-m
                     (sum x1-next x3-next
                          (scale -1.0d0 (scale 2.0d0 x2-next)))))
           (a3-next
            (product k-over-m
                     (sum x2-next (scale -1.0d0 (scale 2.0d0 x3-next)))))

           (time-next (sum time dt)))

      (make-problem
       :name "three-mass-four-spring"
       :slot-names (list "x1" "x2" "x3"
                         "v1" "v2" "v3"
                         "a1" "a2" "a3"
                         "m" "k" "dt" "time")
       :residual-specs
       (list (cons "x1-newton" residual-x1)
             (cons "x2-newton" residual-x2)
             (cons "x3-newton" residual-x3))
       :update-specs
       (list (cons "v1" v1-next)
             (cons "v2" v2-next)
             (cons "v3" v3-next)
             (cons "x1" x1-next)
             (cons "x2" x2-next)
             (cons "x3" x3-next)
             (cons "a1" a1-next)
             (cons "a2" a2-next)
             (cons "a3" a3-next)
             (cons "time" time-next))))))
