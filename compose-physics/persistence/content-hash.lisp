;;; Content addressing via MD5 over the canonical sexp string.
;;;
;;; The content hash is the authoritative identity of a problem.
;;; Two problems whose canonical sexp strings are byte-identical
;;; share a hash, hence share a registry directory; two problems
;;; that differ in any way the canonical form preserves (slot
;;; names, residual structure, update structure, problem name)
;;; produce distinct hashes.
;;;
;;; MD5 was chosen for the registry because: (i) the registry's
;;; threat model is collision avoidance under honest construction,
;;; not adversarial collisions; (ii) MD5 is a 128-bit fingerprint,
;;; comfortably collision-free at the scale of any single
;;; lab's problem catalog; (iii) sb-md5 ships with SBCL with no
;;; external dependency. If a future stronger hash is desired, the
;;; one place that needs to change is content-hash-string.

(in-package #:compose-physics)


(defun %md5-hex-string (octet-vector)
  "Return the lowercase 32-character hex digest of OCTET-VECTOR."
  (let ((digest (sb-md5:md5sum-sequence octet-vector)))
    (with-output-to-string (stream)
      (loop for byte across digest
            do (format stream "~(~2,'0x~)" byte)))))


(defun content-hash-string (canonical-string)
  "Return the hex MD5 digest of CANONICAL-STRING. Inputs are
   encoded as UTF-8 octets so identical canonical strings hash
   identically across host configurations."
  (check-type canonical-string string)
  (%md5-hex-string
   (sb-ext:string-to-octets canonical-string :external-format :utf-8)))


(defun problem-content-hash (problem)
  "Return the hex MD5 digest of PROBLEM's canonical sexp string.
   The hash is the registry's directory name for the problem."
  (check-type problem problem)
  (content-hash-string
   (canonical-sexp-string (canonicalize-problem problem))))


(eval-when (:load-toplevel :execute)

  (let ((digest (content-hash-string "")))
    (assert (= 32 (length digest)) ()
            "expected a 32-character hex digest, got ~D characters"
            (length digest))
    (assert (every (lambda (c) (or (digit-char-p c)
                                   (find c "abcdef"))) digest) ()
            "expected lowercase hex digits, got ~S" digest))


  (let* ((problem-1
          (with-state (x y)
            (make-problem
             :name "hash-determinism"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum x y)))
             :update-specs nil)))
         (problem-2
          (with-state (x y)
            (make-problem
             :name "hash-determinism"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum y x)))
             :update-specs nil))))
    (assert (string= (problem-content-hash problem-1)
                     (problem-content-hash problem-2)) ()
            "equivalent problems must hash to the same digest"))


  (let* ((problem-a
          (with-state (x y)
            (make-problem
             :name "hash-distinct-a"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum x y)))
             :update-specs nil)))
         (problem-b
          (with-state (x y)
            (make-problem
             :name "hash-distinct-b"
             :slot-names (list "x" "y")
             :residual-specs (list (cons "r" (sum x y)))
             :update-specs nil))))
    (assert (not (string= (problem-content-hash problem-a)
                          (problem-content-hash problem-b))) ()
            "different problem names must hash distinctly")))
