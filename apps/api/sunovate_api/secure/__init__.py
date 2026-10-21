"""Secure handling for RAHASIA documents: envelope encryption and the view-only page renderer.

PROPOSED (ADR-020). Development uses an ephemeral local key; a TPM-backed key provider is
required before any real document is stored. Only SIMULATED_DATA is handled here.
"""
