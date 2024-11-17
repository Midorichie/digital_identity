;; Define the data variables
(define-data-var admin principal tx-sender)
(define-map digital-identities 
    principal 
    {
        reputation-score: uint,
        active: bool,
        registration-time: uint,
        last-login: uint,
        game-specific-data: (optional (string-utf8 50))
    }
)

;; Error codes
(define-constant ERR-NOT-AUTHORIZED (err u100))
(define-constant ERR-ALREADY-REGISTERED (err u101))
(define-constant ERR-NOT-FOUND (err u102))

;; Read-only functions
(define-read-only (get-identity (user principal))
    (ok (map-get? digital-identities user))
)

(define-read-only (is-registered (user principal))
    (ok (is-some (map-get? digital-identities user)))
)

;; Public functions
(define-public (register-identity (game-data (optional (string-utf8 50))))
    (let ((caller tx-sender))
        (asserts! (is-none (map-get? digital-identities caller)) ERR-ALREADY-REGISTERED)
        (ok (map-set digital-identities 
            caller
            {
                reputation-score: u0,
                active: true,
                registration-time: block-height,
                last-login: block-height,
                game-specific-data: game-data
            }
        ))
    )
)

(define-public (update-login)
    (let ((caller tx-sender))
        (match (map-get? digital-identities caller)
            identity (ok (map-set digital-identities 
                caller 
                (merge identity { last-login: block-height })))
            ERR-NOT-FOUND
        )
    )
)

(define-public (update-reputation (user principal) (points int))
    (let ((caller tx-sender))
        (asserts! (is-eq caller (var-get admin)) ERR-NOT-AUTHORIZED)
        (match (map-get? digital-identities user)
            identity (ok (map-set digital-identities 
                user 
                (merge identity { 
                    reputation-score: (+ (get reputation-score identity) (to-uint points))
                })))
            ERR-NOT-FOUND
        )
    )
)

(define-public (deactivate-identity)
    (let ((caller tx-sender))
        (match (map-get? digital-identities caller)
            identity (ok (map-set digital-identities 
                caller 
                (merge identity { active: false })))
            ERR-NOT-FOUND
        )
    )
)