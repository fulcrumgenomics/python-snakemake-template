from dataclasses import dataclass
from typing import Callable


@dataclass
class CommonOptions:
    overwrite: bool


@dataclass
class Tool:
    fn: Callable
    display_name: str
    description: str
    short_options: dict[str, str | None] | None = None

    def __str__(self) -> str:
        return self.display_name
