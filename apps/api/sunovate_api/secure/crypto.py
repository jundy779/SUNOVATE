"""Envelope encryption for RAHASIA documents (ADR-020).

Each document gets its own random 256-bit data key (DEK). Content is sealed with AES-256-GCM,
bound to the document id through associated data, and the DEK is wrapped by a key-encryption
key (KEK) held by a `KeyProvider`. Moving from the development provider to a TPM or HSM only
re-wraps DEKs; sealed content is not re-encrypted. Deleting a wrapped DEK destroys the content
permanently (crypto-shredding).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from typing import Protocol

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_KEY_BYTES = 32
_NONCE_BYTES = 12


class DecryptionError(Exception):
    """Raised for any failure to open sealed content; the cause is never exposed to clients."""


class KeyProvider(Protocol):
    """Holds the KEK. Implementations must never expose the KEK itself."""

    @property
    def key_id(self) -> str: ...

    def wrap(self, data_key: bytes) -> bytes: ...

    def unwrap(self, wrapped_key: bytes) -> bytes: ...


class LocalDevelopmentKeyProvider:
    """Ephemeral in-memory KEK for development and tests only.

    The KEK is generated per process and never persisted, so anything sealed with it becomes
    unreadable after a restart. That is acceptable only because the vault holds SIMULATED_DATA.
    """

    def __init__(self, kek: bytes | None = None) -> None:
        self._kek = kek if kek is not None else AESGCM.generate_key(bit_length=256)
        if len(self._kek) != _KEY_BYTES:
            raise ValueError("KEK harus 256 bit")
        self._aead = AESGCM(self._kek)

    @property
    def key_id(self) -> str:
        return "local-development"

    def wrap(self, data_key: bytes) -> bytes:
        nonce = os.urandom(_NONCE_BYTES)
        return nonce + self._aead.encrypt(nonce, data_key, b"sunovate-dek")

    def unwrap(self, wrapped_key: bytes) -> bytes:
        try:
            nonce, sealed_key = wrapped_key[:_NONCE_BYTES], wrapped_key[_NONCE_BYTES:]
            return self._aead.decrypt(nonce, sealed_key, b"sunovate-dek")
        except (InvalidTag, ValueError) as exc:
            raise DecryptionError("Kunci dokumen tidak valid") from exc


@dataclass(frozen=True)
class SealedContent:
    key_id: str
    wrapped_key: bytes | None  # None after crypto-shredding
    nonce: bytes
    ciphertext: bytes


def seal(plaintext: bytes, provider: KeyProvider, *, associated_data: bytes) -> SealedContent:
    data_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(_NONCE_BYTES)
    ciphertext = AESGCM(data_key).encrypt(nonce, plaintext, associated_data)
    return SealedContent(
        key_id=provider.key_id,
        wrapped_key=provider.wrap(data_key),
        nonce=nonce,
        ciphertext=ciphertext,
    )


def open_sealed(sealed: SealedContent, provider: KeyProvider, *, associated_data: bytes) -> bytes:
    if sealed.wrapped_key is None:
        raise DecryptionError("Dokumen telah dimusnahkan")
    if sealed.key_id != provider.key_id:
        raise DecryptionError("Penyedia kunci tidak sesuai")
    data_key = provider.unwrap(sealed.wrapped_key)
    try:
        return AESGCM(data_key).decrypt(sealed.nonce, sealed.ciphertext, associated_data)
    except InvalidTag as exc:
        raise DecryptionError("Isi dokumen tidak dapat dibuka") from exc


def shred(sealed: SealedContent) -> SealedContent:
    """Crypto-shredding: drop the wrapped DEK so the ciphertext can never be opened again."""
    return replace(sealed, wrapped_key=None)
