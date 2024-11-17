;; Define traits
(define-trait identity-validator-trait
    ((validate-identity (principal) (response bool uint))
     (get-validator-score (principal) (response uint uint)))
)

;; Define the data variables
(define-data-var admin principal tx-sender)
(define-map validators principal bool)
(define-map digital-identities 
    principal 
    {
        reputation-score: uint,
        active: bool,
        registration-time: uint,
        last-login: uint,
        game-specific-data: (optional (string-utf8 50)),
        trust-score: uint,
        achievements: (list 10 uint),
        validator-count: uint,
        recovery-address: (optional principal)
    }
)

;; Define non-fungible token for achievements
(define-non-fungible-token identity-achievement uint)

;; Error codes
(define-constant ERR-NOT-AUTHORIZED (err u100))
(define-constant ERR-ALREADY-REGISTERED (err u101))
(define-constant ERR-NOT-FOUND (err u102))
(define-constant ERR-INVALID-SCORE (err u103))
(define-constant ERR-TOO-MANY-ACHIEVEMENTS (err u104))
(define-constant ERR-RECOVERY-MISMATCH (err u105))

;; Read-only functions
(define-read-only (get-identity (user principal))
    (ok (map-get? digital-identities user))
)

(define-read-only (is-registered (user principal))
    (ok (is-some (map-get? digital-identities user)))
)

(define-read-only (get-trust-score (user principal))
    (match (map-get? digital-identities user)
        identity (ok (get trust-score identity))
        ERR-NOT-FOUND
    )
)

;; Enhanced public functions
(define-public (register-identity (game-data (optional (string-utf8 50))) (recovery-addr (optional principal)))
    (let ((caller tx-sender))
        (asserts! (is-none (map-get? digital-identities caller)) ERR-ALREADY-REGISTERED)
        (ok (map-set digital-identities 
            caller
            {
                reputation-score: u0,
                active: true,
                registration-time: block-height,
                last-login: block-height,
                game-specific-data: game-data,
                trust-score: u0,
                achievements: (list),
                validator-count: u0,
                recovery-address: recovery-addr
            }
        ))
    )
)

(define-public (validate-user (user principal))
    (let ((caller tx-sender)
          (is-validator (default-to false (map-get? validators caller))))
        (asserts! is-validator ERR-NOT-AUTHORIZED)
        (match (map-get? digital-identities user)
            identity 
            (ok (map-set digital-identities 
                user 
                (merge identity { 
                    validator-count: (+ (get validator-count identity) u1),
                    trust-score: (+ (get trust-score identity) u10)
                })))
            ERR-NOT-FOUND
        )
    )
)

(define-public (add-achievement (user principal) (achievement-id uint))
    (let ((caller tx-sender))
        (asserts! (is-eq caller (var-get admin)) ERR-NOT-AUTHORIZED)
        (match (map-get? digital-identities user)
            identity 
            (begin
                (asserts! (< (len (get achievements identity)) u10) ERR-TOO-MANY-ACHIEVEMENTS)
                (try! (nft-mint? identity-achievement achievement-id user))
                (ok (map-set digital-identities 
                    user 
                    (merge identity { 
                        achievements: (unwrap! (as-max-len? 
                            (append (get achievements identity) achievement-id) 
                            u10) 
                            ERR-TOO-MANY-ACHIEVEMENTS)
                    })))
            )
            ERR-NOT-FOUND
        )
    )
)

(define-public (recover-identity (old-address principal))
    (let ((caller tx-sender))
        (match (map-get? digital-identities old-address)
            identity 
            (begin
                (asserts! (is-eq (some caller) (get recovery-address identity)) ERR-RECOVERY-MISMATCH)
                (map-delete digital-identities old-address)
                (ok (map-set digital-identities 
                    caller
                    (merge identity {
                        last-login: block-height,
                        recovery-address: none
                    })))
            )
            ERR-NOT-FOUND
        )
    )
)

;; Admin functions
(define-public (add-validator (validator principal))
    (begin
        (asserts! (is-eq tx-sender (var-get admin)) ERR-NOT-AUTHORIZED)
        (ok (map-set validators validator true))
    )
)