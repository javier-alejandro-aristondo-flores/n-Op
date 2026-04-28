;;; The problem object and its authoring macros.
;;;
;;; A problem is the closed-form description of a physical system over a
;;; flat input buffer of N named slots. It pairs:
;;;
;;;   - K residual rows: pointwise constitutive checks on a single state
;;;     buffer; out_r[k] = 0 means the state is internally consistent.
;;;   - N update rows: per-slot one-step rules state_curr -> state_next.
;;;     Slots the author does not explicitly override default to identity
;;;     (state_next[i] = state_curr[i]); the C output buffer is always
;;;     full-N.
;;;
;;; The tool sees only doubles and names: there is no notion of state
;;; vs. parameter, no semantics of time, dt, or mass. A slot is just an
;;; integer index into a double[] paired with a string name.
;;;
;;; Authoring is layered: with-state binds Lisp symbols to unit terms at
;;; sequential indices so authors write expressions in natural Lisp
;;; syntax, and define-problem packages a set of named residuals and
;;; per-slot updates into a problem object in one form. Both macros
;;; expand into ordinary make-problem calls; programmatic construction
;;; from already-built expression trees is equally first-class.

(in-package #:compose-physics)


;;; Row records. Both are immutable plain structures: residual-row pairs
;;; a name with its expression; update-row carries the slot the rule
;;; writes to plus a flag distinguishing explicit author rules from
;;; the synthesized identity defaults (the codegen emits both, but
;;; downstream tooling sometimes wants to know which is which).

(defstruct residual-row
  (name       ""  :type string)
  (expression nil :type expression :read-only t))


(defstruct update-row
  (slot-name  ""  :type string)
  (slot-index 0   :type fixnum)
  (expression nil :type expression :read-only t)
  (explicit-p nil :type boolean    :read-only t))


;;; The problem object itself. Stored as plain CLOS so problem instances
;;; are not funcallable; only IR expressions are. The slot-names vector
;;; is the canonical (index -> name) map; problem-slot-count returns N
;;; and problem-residual-count returns K so consumers do not depend on
;;; vector length conventions.

(defclass problem ()
  ((name
    :type string
    :initarg :name
    :reader problem-name)
   (slot-names
    :type simple-vector
    :initarg :slot-names
    :reader problem-slot-names)
   (residual-rows
    :type simple-vector
    :initarg :residual-rows
    :reader problem-residual-rows)
   (update-rows
    :type simple-vector
    :initarg :update-rows
    :reader problem-update-rows)))


(defun problem-p (object)
  (typep object 'problem))


(defun problem-slot-count (problem)
  (length (problem-slot-names problem)))


(defun problem-residual-count (problem)
  (length (problem-residual-rows problem)))


;;; Validation helpers. Pure functions; signal CL errors with named
;;; format strings so that downstream code (and the eventual loud-named
;;; condition types in algebra/solve/failures.lisp) can catch and
;;; re-package them if needed.

(defun %validate-slot-names (slot-names)
  (let ((slot-count (length slot-names)))
    (when (zerop slot-count)
      (error "problem requires at least one slot, got an empty slot list"))
    (let ((seen (make-hash-table :test 'equal)))
      (dotimes (index slot-count)
        (let ((name (aref slot-names index)))
          (unless (and (stringp name) (plusp (length name)))
            (error "slot ~D has invalid name ~S (must be a non-empty string)"
                   index name))
          (when (gethash name seen)
            (error "slot name ~S is duplicated in the slot list" name))
          (setf (gethash name seen) index))))))


(defun %validate-expression-against-slots (expression slot-names where)
  (let ((slot-count (length slot-names)))
    (walk-expression
     expression
     (lambda (node)
       (when (term-p node)
         (let ((index (term-index node))
               (name  (term-name node)))
           (unless (< -1 index slot-count)
             (error "~A: term references index ~D outside slot range [0, ~D)"
                    where index slot-count))
           (when (plusp (length name))
             (let ((expected (aref slot-names index)))
               (unless (string= name expected)
                 (error "~A: term at index ~D carries name ~S but the problem's slot ~D is named ~S"
                        where index name index expected))))))))))


(defun %slot-index-of (slot-names name)
  (loop for index below (length slot-names)
        when (string= (aref slot-names index) name)
        return index
        finally (return nil)))


(defun %slots-referenced-by (expression)
  (let ((indices '()))
    (walk-expression
     expression
     (lambda (node)
       (when (term-p node)
         (pushnew (term-index node) indices))))
    indices))


;;; Constructor. residual-specs is a list of (name . expression) pairs in
;;; author order; update-specs is a list of (slot-name . expression)
;;; pairs giving explicit rules (slots not mentioned default to identity).

(defun make-problem (&key name slot-names residual-specs update-specs)
  "Construct a problem.

   NAME              : non-empty string, the problem identifier.
   SLOT-NAMES        : sequence of distinct non-empty strings; index i
                       in any term within any expression must point at
                       slot-names[i] (or carry an empty term-name).
   RESIDUAL-SPECS    : list of (name . expression) pairs. Names must be
                       non-empty and distinct; expressions must validate
                       against slot-names. The list is preserved in
                       author order; out_r[k] follows that order.
   UPDATE-SPECS      : list of (slot-name . expression) pairs. Each
                       slot-name must appear in slot-names; duplicates
                       are rejected. Slots not mentioned receive an
                       identity update (state_next[i] = state_curr[i])
                       generated by this function.

   Validates the no-useless-slot invariant: every slot must be
   referenced by some residual expression or by some explicit update
   expression."
  (check-type name string)
  (unless (plusp (length name))
    (error "problem name must be a non-empty string"))
  (let ((slot-vector (coerce slot-names 'simple-vector)))
    (%validate-slot-names slot-vector)
    (let* ((slot-count (length slot-vector))

           ;; residual rows: validate, keep order, ensure unique names.
           (residual-rows
            (let ((seen-names (make-hash-table :test 'equal))
                  (rows (make-array (length residual-specs))))
              (loop for spec in residual-specs
                    for index from 0
                    do (let ((residual-name (car spec))
                             (expression    (cdr spec)))
                         (check-type residual-name string)
                         (unless (plusp (length residual-name))
                           (error "residual at position ~D has empty name" index))
                         (when (gethash residual-name seen-names)
                           (error "residual name ~S is duplicated" residual-name))
                         (setf (gethash residual-name seen-names) t)
                         (ensure-expression expression)
                         (%validate-expression-against-slots
                          expression slot-vector
                          (format nil "residual ~S" residual-name))
                         (setf (aref rows index)
                               (make-residual-row
                                :name residual-name
                                :expression expression))))
              rows))

           ;; explicit updates: validate, keep an index map for the
           ;; default-identity fill below.
           (explicit-update-table (make-hash-table :test 'equal)))

      (dolist (spec update-specs)
        (let ((slot-name (car spec))
              (expression (cdr spec)))
          (check-type slot-name string)
          (let ((slot-index (%slot-index-of slot-vector slot-name)))
            (unless slot-index
              (error "update names slot ~S which is not in the problem's slot list"
                     slot-name))
            (when (gethash slot-name explicit-update-table)
              (error "duplicate update rule for slot ~S" slot-name))
            (ensure-expression expression)
            (%validate-expression-against-slots
             expression slot-vector
             (format nil "update for slot ~S" slot-name))
            (setf (gethash slot-name explicit-update-table)
                  (cons slot-index expression)))))

      ;; update rows: one per slot, in slot-name order, identity by default.
      (let ((update-rows (make-array slot-count)))
        (dotimes (slot-index slot-count)
          (let* ((slot-name (aref slot-vector slot-index))
                 (explicit  (gethash slot-name explicit-update-table)))
            (setf (aref update-rows slot-index)
                  (if explicit
                      (make-update-row
                       :slot-name slot-name
                       :slot-index slot-index
                       :expression (cdr explicit)
                       :explicit-p t)
                      (make-update-row
                       :slot-name slot-name
                       :slot-index slot-index
                       :expression (term 1.0d0 slot-index :name slot-name)
                       :explicit-p nil)))))

        ;; useless-slot check: a slot is referenced if any residual term
        ;; or any explicit update expression touches it.
        (let ((referenced (make-hash-table)))
          (loop for residual-row across residual-rows do
            (dolist (slot-index (%slots-referenced-by
                                 (residual-row-expression residual-row)))
              (setf (gethash slot-index referenced) t)))
          (maphash (lambda (slot-name index-and-expression)
                     (declare (ignore slot-name))
                     (dolist (slot-index (%slots-referenced-by
                                          (cdr index-and-expression)))
                       (setf (gethash slot-index referenced) t)))
                   explicit-update-table)
          (dotimes (slot-index slot-count)
            (unless (gethash slot-index referenced)
              (error "slot ~S (index ~D) is unreferenced by any residual or explicit update"
                     (aref slot-vector slot-index) slot-index))))

        (make-instance 'problem
                       :name name
                       :slot-names slot-vector
                       :residual-rows residual-rows
                       :update-rows update-rows)))))


;;; Authoring macros.
;;;
;;; with-state binds the Lisp symbols in BINDINGS to unit terms at
;;; sequential indices 0, 1, 2, ... and evaluates BODY in that lexical
;;; scope. Each term carries the symbol's name (downcased) so problem
;;; validation can cross-check term-name against slot-names.

(defmacro with-state (bindings &body body)
  "Bind each symbol in BINDINGS to a unit-coefficient term at its
   sequential index, then evaluate BODY. The slot-name string for each
   binding is (string-downcase (symbol-name binding))."
  (let ((let-bindings
         (loop for symbol in bindings
               for index from 0
               collect (let ((slot-name (string-downcase (symbol-name symbol))))
                         `(,symbol (term 1.0d0 ,index :name ,slot-name))))))
    `(let ,let-bindings
       ,@body)))


(defmacro define-problem (name &key state residuals updates)
  "High-level authoring form.

   NAME      : a string literal identifying the problem.
   STATE     : an unevaluated list of symbols; each becomes a slot
               whose string name is (string-downcase (symbol-name s)).
   RESIDUALS : a list of (residual-symbol expression-form) pairs.
               Each residual-symbol's downcased name becomes the
               residual row's name; expression-form is evaluated with
               every state symbol bound to its unit term.
   UPDATES   : a list of (slot-symbol expression-form) pairs.
               slot-symbol must appear in STATE; expression-form is
               evaluated with every state symbol bound to its unit
               term. Slots not listed receive identity updates."
  (check-type name string)
  (let ((slot-name-vector
         (map 'simple-vector
              (lambda (symbol) (string-downcase (symbol-name symbol)))
              state)))
    `(with-state ,state
       (make-problem
        :name ,name
        :slot-names ,slot-name-vector
        :residual-specs
        (list ,@(loop for (residual-symbol expression-form) in residuals
                      collect `(cons ,(string-downcase (symbol-name residual-symbol))
                                     ,expression-form)))
        :update-specs
        (list ,@(loop for (slot-symbol expression-form) in updates
                      collect `(cons ,(string-downcase (symbol-name slot-symbol))
                                     ,expression-form)))))))


;;; Inline self-checks. A small two-slot problem exercises the full
;;; construction path including default-identity update synthesis,
;;; useless-slot rejection, name-mismatch rejection, and the
;;; define-problem macro.

(eval-when (:load-toplevel :execute)

  ;; Programmatic construction. Slots: position p, velocity v.
  ;; Residual: v - p (a placeholder relation that touches both slots).
  ;; Update: p_next = p + v; v_next defaults to identity.
  (let* ((slots #("p" "v"))
         (term-p (term 1.0d0 0 :name "p"))
         (term-v (term 1.0d0 1 :name "v"))
         (residual (sum term-v (scale -1.0d0 term-p)))
         (update-p (sum term-p term-v))
         (problem (make-problem
                   :name "two-slot"
                   :slot-names slots
                   :residual-specs (list (cons "consistency" residual))
                   :update-specs (list (cons "p" update-p)))))
    (assert (problem-p problem))
    (assert (string= (problem-name problem) "two-slot"))
    (assert (= (problem-slot-count problem) 2))
    (assert (= (problem-residual-count problem) 1))
    (assert (equalp (problem-slot-names problem) #("p" "v")))

    (let ((residual-rows (problem-residual-rows problem)))
      (assert (= (length residual-rows) 1))
      (assert (string= (residual-row-name (aref residual-rows 0)) "consistency")))

    (let ((update-rows (problem-update-rows problem)))
      (assert (= (length update-rows) 2))
      (assert (string= (update-row-slot-name (aref update-rows 0)) "p"))
      (assert (update-row-explicit-p (aref update-rows 0)))
      (assert (string= (update-row-slot-name (aref update-rows 1)) "v"))
      (assert (not (update-row-explicit-p (aref update-rows 1))))
      (let ((state (make-array 2 :element-type 'double-float
                                 :initial-contents '(3.0d0 7.0d0))))
        ;; identity update for v evaluates to state[1] = 7.
        (assert (= (funcall (update-row-expression (aref update-rows 1)) state)
                   7.0d0))
        ;; explicit update for p evaluates to state[0] + state[1] = 10.
        (assert (= (funcall (update-row-expression (aref update-rows 0)) state)
                   10.0d0)))))

  ;; Useless-slot rejection: a slot referenced by no expression.
  (let ((slots #("a" "b"))
        (residual (term 1.0d0 0 :name "a")))
    (handler-case
        (progn
          (make-problem :name "should-fail"
                        :slot-names slots
                        :residual-specs (list (cons "only-a" residual))
                        :update-specs nil)
          (assert nil () "useless-slot invariant was not enforced"))
      (error () nil)))

  ;; Name/index mismatch rejection: term claims to be slot "v" at index 0
  ;; but slot 0 is named "p".
  (let ((bad-term (term 1.0d0 0 :name "v")))
    (handler-case
        (progn
          (make-problem :name "should-fail"
                        :slot-names #("p" "v")
                        :residual-specs (list (cons "wrong" bad-term))
                        :update-specs nil)
          (assert nil () "term-name / slot-name mismatch was not detected"))
      (error () nil)))

  ;; Duplicate residual name rejection.
  (let ((leaf (term 1.0d0 0 :name "p")))
    (handler-case
        (progn
          (make-problem :name "should-fail"
                        :slot-names #("p")
                        :residual-specs (list (cons "r" leaf) (cons "r" leaf))
                        :update-specs nil)
          (assert nil () "duplicate residual names were not detected"))
      (error () nil)))

  ;; with-state binds symbols to unit terms at sequential indices.
  (with-state (alpha beta gamma)
    (assert (term-p alpha))
    (assert (= (term-index alpha) 0))
    (assert (= (term-index beta) 1))
    (assert (= (term-index gamma) 2))
    (assert (string= (term-name alpha) "alpha"))
    (assert (string= (term-name gamma) "gamma")))

  ;; define-problem macro: a one-mass / one-spring system, exercised
  ;; against a known state to confirm both residual and update rows
  ;; evaluate as authored.
  (let ((problem (define-problem "one-mass"
                   :state (x v a m k dt)
                   :residuals
                   ((newton (sum (product m a)
                                 (scale 1.0d0 (product k x)))))
                   :updates
                   ((v (sum v (product a dt)))
                    (x (sum x (product v dt)))))))
    (assert (problem-p problem))
    (assert (= (problem-slot-count problem) 6))
    (assert (= (problem-residual-count problem) 1))
    (assert (equalp (problem-slot-names problem)
                    #("x" "v" "a" "m" "k" "dt")))
    (let* ((state (make-array 6 :element-type 'double-float
                                :initial-contents
                                '(2.0d0 3.0d0 -1.0d0 4.0d0 5.0d0 0.1d0)))
           (residual-row (aref (problem-residual-rows problem) 0))
           (update-rows  (problem-update-rows problem)))
      ;; Newton residual: m*a + k*x = 4*-1 + 5*2 = 6.
      (assert (= (funcall (residual-row-expression residual-row) state) 6.0d0))
      ;; Update for v: v + a*dt = 3 + (-1)*0.1 = 2.9.
      (let ((v-row (find "v" update-rows :key #'update-row-slot-name :test #'string=)))
        (assert (update-row-explicit-p v-row))
        (assert (= (funcall (update-row-expression v-row) state) 2.9d0)))
      ;; Identity-default update for parameter slot m yields state[3] = 4.
      (let ((m-row (find "m" update-rows :key #'update-row-slot-name :test #'string=)))
        (assert (not (update-row-explicit-p m-row)))
        (assert (= (funcall (update-row-expression m-row) state) 4.0d0))))))
