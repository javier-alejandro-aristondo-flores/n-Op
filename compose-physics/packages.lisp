;;; Single-package single-export-list source of truth for compose-physics.
;;;
;;; The package shadows cl:apply because the IR primitive of the same name
;;; is the keyword for vocabulary-function application; every numerical
;;; consumer of cl:apply inside this system writes cl:apply explicitly.

(defpackage #:compose-physics
  (:use #:cl)
  (:shadow #:apply)
  (:export
   ;; Expression-tree IR — five funcallable node kinds plus the abstract base.
   #:expression
   #:expression-children
   #:term       #:term-coefficient #:term-index #:term-name #:term-p
   #:sum        #:sum-children                                 #:sum-p
   #:product    #:product-children                             #:product-p
   #:scale      #:scale-factor #:scale-child                   #:scale-p
   #:apply      #:apply-name #:apply-forward #:apply-child     #:apply-p
   #:make-apply-node

   ;; Traversal and simplification.
   #:walk-expression #:collect-term-names #:collect-term-indices
   #:simplify-expression

   ;; Vocabulary — function-record struct, registration API, lookup helpers.
   #:function-record #:function-record-p
   #:function-record-forward-function
   #:function-record-inverse-function
   #:function-record-emission-identifier
   #:function-record-inverse-key
   #:register-function
   #:lookup-function-record
   #:lookup-forward-function #:lookup-inverse-function
   #:lookup-emission-identifier #:lookup-inverse-key
   #:vocabulary-keys

   ;; Problem object — slot-name map, residual rows, update rows.
   #:problem #:problem-p
   #:problem-name #:problem-slot-names
   #:problem-residual-rows #:problem-update-rows
   #:problem-slot-count #:problem-residual-count
   #:residual-row #:residual-row-p
   #:residual-row-name #:residual-row-expression
   #:update-row #:update-row-p
   #:update-row-slot-name #:update-row-slot-index
   #:update-row-expression #:update-row-explicit-p
   #:make-problem
   #:with-state #:define-problem

   ;; solve-for failure conditions.
   #:solve-failure
   #:solve-failure-residual-name
   #:solve-failure-target-slot-name
   #:solve-failure-reason
   #:solve-target-not-found
   #:solve-target-has-multiple-occurrences
   #:solve-non-linear-in-target
   #:solve-product-multiple-target-factors
   #:solve-no-registered-inverse
   #:solve-no-registered-inverse-function-name
   #:solve-unsupported-shape
   #:signal-solve-failure

   ;; solve-for — linear rearrangement strategy.
   #:solve-linear-for #:count-target-occurrences

   ;; solve-for — apply-inversion dispatcher.
   #:solve-for

   ;; emission/expression-emission — per-node C string generation.
   #:emit-expression-c #:format-double-literal #:collect-emission-identifiers

   ;; emission/chunking — chunked C source generation.
   #:chunk-source #:chunk-source-p
   #:chunk-source-filename #:chunk-source-function-name
   #:chunk-source-text #:chunk-source-first-row-index
   #:chunk-source-row-count #:chunk-source-emission-identifiers
   #:emit-residual-chunks #:emit-update-chunks
   #:*default-chunk-row-count* #:*reciprocal-emission-identifier*

   ;; emission/dispatch — dispatch.c source generation.
   #:emit-dispatch-c

   ;; emission/makefile — Makefile generation parameterized by toolchain.
   #:emit-makefile #:*default-c-compiler* #:*default-c-flags*
   #:*default-shared-library-extension*

   ;; persistence/sexp/canonicalize — canonical sexp form for content hashing.
   #:canonicalize-expression #:canonicalize-residual-row
   #:canonicalize-update-row #:canonicalize-problem
   #:canonical-sexp-string

   ;; persistence/sexp/serialize — write canonical sexp to streams and files.
   #:serialize-residual-rows-to-stream #:serialize-update-rows-to-stream
   #:serialize-problem-to-stream
   #:serialize-residual-rows-to-file #:serialize-update-rows-to-file
   #:serialize-problem-to-file

   ;; persistence/sexp/deserialize — exact inverse of serialize.
   #:deserialize-expression #:deserialize-residual-row
   #:deserialize-update-row #:deserialize-problem
   #:deserialize-problem-from-string

   ;; persistence/content-hash — MD5 over canonical sexp string.
   #:content-hash-string #:problem-content-hash

   ;; persistence/registry/source-handling — --source-dest semantics.
   #:source-disposition-tag #:*default-source-disposition*
   #:handle-source-file

   ;; persistence/registry/manifest — manifest.sexp and index.sexp.
   #:manifest-toolchain #:make-manifest-toolchain
   #:manifest-toolchain-c-compiler #:manifest-toolchain-c-flags
   #:manifest-toolchain-library-extension
   #:build-manifest-sexp #:write-manifest-to-file
   #:read-index-sexp #:update-index-sexp

   ;; persistence/registry/register-problem — orchestrator.
   #:registration-result #:registration-result-content-hash
   #:registration-result-problem-directory
   #:registration-result-manifest-pathname
   #:registration-result-library-filename
   #:registration-result-chunk-filenames
   #:register-problem))
