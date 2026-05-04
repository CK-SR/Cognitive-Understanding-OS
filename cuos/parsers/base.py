from abc import ABC, abstractmethod
from pathlib import Path

from cuos.schemas.document import ParsedDocument


class ParserAdapter(ABC):
    @abstractmethod
    def parse(self, file_path: Path, output_dir: Path) -> ParsedDocument:
        raise NotImplementedError
