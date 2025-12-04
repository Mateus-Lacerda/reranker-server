"""
Configuration management for ReServer Client SDK.
"""

import os
from dataclasses import dataclass


@dataclass
class ClientConfig:
    """Configuration for ReServer client."""

    host: str = "localhost"
    port: int = 50051
    timeout: float = 30.0
    max_retries: int = 3
    secure: bool = False

    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("RESERVER_HOST", "localhost"),
            port=int(os.getenv("RESERVER_PORT", "50051")),
            timeout=float(os.getenv("RESERVER_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("RESERVER_MAX_RETRIES", "3")),
            secure=os.getenv("RESERVER_SECURE", "false").lower() == "true",
        )

    @property
    def address(self) -> str:
        """Get server address."""
        return f"{self.host}:{self.port}"


def get_default_config() -> ClientConfig:
    """Get default configuration, preferring environment variables."""
    return ClientConfig.from_env()
