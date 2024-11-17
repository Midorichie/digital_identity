use sha2::{Sha256, Digest};
use ed25519_dalek::{Keypair, PublicKey, SecretKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum IdentityError {
    #[error("signature verification failed")]
    SignatureError,
    #[error("invalid key format")]
    KeyFormatError,
    #[error("challenge generation failed")]
    ChallengeError,
}

pub struct IdentityVerifier {
    keypair: Keypair,
}

impl IdentityVerifier {
    pub fn new() -> Self {
        let mut csprng = OsRng{};
        let keypair: Keypair = Keypair::generate(&mut csprng);
        Self { keypair }
    }
    
    pub fn generate_challenge(&self, user_address: &str) -> Result<Vec<u8>, IdentityError> {
        let mut hasher = Sha256::new();
        hasher.update(user_address.as_bytes());
        
        // Add timestamp for uniqueness
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| IdentityError::ChallengeError)?
            .as_secs()
            .to_be_bytes();
        
        hasher.update(&timestamp);
        Ok(hasher.finalize().to_vec())
    }
    
    pub fn sign_challenge(&self, challenge: &[u8]) -> Signature {
        self.keypair.sign(challenge)
    }
    
    pub fn verify_signature(
        &self,
        challenge: &[u8],
        signature: &Signature,
        public_key: &PublicKey
    ) -> Result<bool, IdentityError> {
        public_key
            .verify(challenge, signature)
            .map(|_| true)
            .map_err(|_| IdentityError::SignatureError)
    }
    
    pub fn get_public_key(&self) -> PublicKey {
        self.keypair.public
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_challenge_generation() {
        let verifier = IdentityVerifier::new();
        let user_address = "ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM";
        
        let challenge = verifier.generate_challenge(user_address).unwrap();
        assert_eq!(challenge.len(), 32); // SHA256 output length
    }

    #[test]
    fn test_signature_verification() {
        let verifier = IdentityVerifier::new();
        let user_address = "ST1PQHQKV0RJXZFY1DGX8MNSNYVE3VGZJSRTPGZGM";
        
        let challenge = verifier.generate_challenge(user_address).unwrap();
        let signature = verifier.sign_challenge(&challenge);
        
        let result = verifier.verify_signature(
            &challenge,
            &signature,
            &verifier.get_public_key()
        ).unwrap();
        
        assert!(result);
    }
}