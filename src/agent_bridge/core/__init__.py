"""Core abstractions for Agent Bridge."""

from .types import AgentRole, ConversionResult, SourceType
from .converter import BaseConverter, converter_registry
from .agent_registry import AGENT_ROLES, get_agent_role
from .plugins import PluginRunner

__all__ = [
    "AgentRole",
    "ConversionResult",
    "SourceType",
    "BaseConverter",
    "converter_registry",
    "AGENT_ROLES",
    "get_agent_role",
    "PluginRunner",
]