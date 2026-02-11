"""Core abstractions for Agent Bridge."""

from .types import AgentRole, ConversionResult, IDEFormat
from .converter import BaseConverter, converter_registry
from .agent_registry import AGENT_ROLES, get_agent_role

__all__ = [
    "AgentRole",
    "ConversionResult",
    "IDEFormat",
    "BaseConverter",
    "converter_registry",
    "AGENT_ROLES",
    "get_agent_role",
]