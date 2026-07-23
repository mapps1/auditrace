"""Ed25519 key generation, signing, and verification."""

from __future__ import annotations

import base64
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

PRIVATE_KEY_FILE = "signing_key.pem"
PUBLIC_KEY_FILE = "verify_key.pem"


class Signer:
    """Handle local Ed25519 signing keys and signature operations."""

    def __init__(self, key_dir: Path | None = None) -> None:
        self.key_dir = key_dir or (Path.home() / ".auditrace")
        self._private_key: Ed25519PrivateKey | None = None
        self._public_key: Ed25519PublicKey | None = None

    def generate_keypair(self) -> None:
        """Generate and persist a new private/public Ed25519 keypair."""
        self.key_dir.mkdir(parents=True, exist_ok=True)
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        private_path = self.key_dir / PRIVATE_KEY_FILE
        private_path.write_bytes(private_pem)
        private_path.chmod(0o600)

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        (self.key_dir / PUBLIC_KEY_FILE).write_bytes(public_pem)

        self._private_key = private_key
        self._public_key = public_key

    def _load_private_key(self) -> Ed25519PrivateKey:
        if self._private_key is None:
            pem = (self.key_dir / PRIVATE_KEY_FILE).read_bytes()
            key = serialization.load_pem_private_key(pem, password=None)
            if not isinstance(key, Ed25519PrivateKey):
                msg = "Loaded private key is not Ed25519"
                raise TypeError(msg)
            self._private_key = key
        return self._private_key

    def _load_public_key(self) -> Ed25519PublicKey:
        if self._public_key is None:
            pem = (self.key_dir / PUBLIC_KEY_FILE).read_bytes()
            key = serialization.load_pem_public_key(pem)
            if not isinstance(key, Ed25519PublicKey):
                msg = "Loaded public key is not Ed25519"
                raise TypeError(msg)
            self._public_key = key
        return self._public_key

    def sign(self, data: str) -> str:
        """Sign a string payload and return a base64-encoded signature."""
        sig_bytes = self._load_private_key().sign(data.encode("utf-8"))
        return base64.b64encode(sig_bytes).decode("utf-8")

    def verify(self, data: str, signature: str) -> bool:
        """Verify a base64-encoded signature against a string payload."""
        try:
            sig_bytes = base64.b64decode(signature)
            self._load_public_key().verify(sig_bytes, data.encode("utf-8"))
            return True
        except Exception:
            return False

    def public_key_pem(self) -> str:
        """Return the current public key as PEM text."""
        return (
            self._load_public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )
