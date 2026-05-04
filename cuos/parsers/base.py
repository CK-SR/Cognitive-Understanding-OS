from abc import ABC, abstractmethod
from pathlib import Path

from cuos.schemas.document import ParsedDocument


class ParserAdapter(ABC):
    name: str

    @abstractmethod
    def parse(self, source_path: Path, output_dir: Path) -> ParsedDocument:
        raise NotImplementedError
