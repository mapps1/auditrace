from pathlib import Path

from auditrace.core.signer import PRIVATE_KEY_FILE, PUBLIC_KEY_FILE, Signer


def test_signer_generate_sign_verify(tmp_path: Path) -> None:
    signer = Signer(key_dir=tmp_path)
    signer.generate_keypair()

    assert (tmp_path / PRIVATE_KEY_FILE).exists()
    assert (tmp_path / PUBLIC_KEY_FILE).exists()

    payload = "abc123"
    sig = signer.sign(payload)
    assert signer.verify(payload, sig)
    assert not signer.verify("wrong", sig)
    assert "BEGIN PUBLIC KEY" in signer.public_key_pem()
