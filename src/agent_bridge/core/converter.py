"""
Converter base class and auto-discovery registry.
Adding a new IDE = implement BaseConverter + register.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Type

from .types import ConversionResult, IDEFormat


class BaseConverter(ABC):
    @property
    @abstractmethod
    def format_info(self) -> IDEFormat: ...

    @abstractmethod
    def convert(self, source_root: Path, dest_root: Path, verbose: bool = True, force: bool = False) -> ConversionResult: ...

    @abstractmethod
    def install_mcp(self, source_root: Path, dest_root: Path, force: bool = False) -> bool: ...

    @abstractmethod
    def clean(self, project_path: Path) -> bool: ...

    @property
    def name(self) -> str:
        return self.format_info.name

    @property
    def display_name(self) -> str:
        return self.format_info.display_name

    @property
    def checkbox_label(self) -> str:
        return self.format_info.checkbox_label or f"{self.display_name} ({self.format_info.output_dir}/)"


class ConverterRegistry:
    def __init__(self):
        self._converters: Dict[str, BaseConverter] = {}

    def register(self, converter_class: Type[BaseConverter]) -> None:
        instance = converter_class()
        self._converters[instance.name] = instance

    def get(self, name: str) -> Optional[BaseConverter]:
        return self._converters.get(name.lower())

    def all(self) -> List[BaseConverter]:
        return list(self._converters.values())

    def names(self) -> List[str]:
        return list(self._converters.keys())


converter_registry = ConverterRegistry()