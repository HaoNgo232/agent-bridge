"""Vault management — multi-source agent knowledge."""
from .manager import VaultManager, Vault, VAULTS_CACHE_DIR, VAULTS_CONFIG_DIR

__all__ = ["VaultManager", "Vault", "VAULTS_CACHE_DIR", "VAULTS_CONFIG_DIR"]