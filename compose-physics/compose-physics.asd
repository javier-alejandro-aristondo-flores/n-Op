;;; ASDF system definition for compose-physics.
;;;
;;; Files are listed in dependency order. Each file is independently
;;; self-checking via inline assertions evaluated when the file loads.

(defsystem "compose-physics"
  :description "Closed-form physics problems compiled to chunked C kernels."
  :serial t
  :depends-on (#:sb-md5)
  :components
  ((:file "packages")
   (:module "algebra"
    :serial t
    :components
    ((:file "expression-trees")
     (:module "vocabulary"
      :serial t
      :components
      ((:file "function-record")
       (:file "standard-entries")))
     (:file "problem")
     (:module "solve"
      :serial t
      :components
      ((:file "failures")
       (:file "linear-rearrangement")
       (:file "apply-inversion")))))
   (:module "emission"
    :serial t
    :components
    ((:file "expression-emission")
     (:file "chunking")
     (:file "dispatch")
     (:file "makefile")))
   (:module "persistence"
    :serial t
    :components
    ((:module "sexp"
      :serial t
      :components
      ((:file "canonicalize")
       (:file "serialize")
       (:file "deserialize")))
     (:file "content-hash")
     (:module "registry"
      :serial t
      :components
      ((:file "source-handling")
       (:file "manifest")
       (:file "register-problem")))))))
