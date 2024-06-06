"""Connector configuration"""

from dataclasses import dataclass, field


@dataclass
class Configuration:
    """Configuration settings"""

    custom_topic: str = "custom/signal"


@dataclass
class Tedge:
    """Tedge settings"""

    host: str = "localhost"
    port: int = 1883
    api: str = "http://localhost:8000"


@dataclass
class Config:
    """Configuration class to load the connector's config"""

    device_id: str = None
    tedge: Tedge = field(default_factory=Tedge)
    configuration: Configuration = field(default_factory=Configuration)
