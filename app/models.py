
from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class Record:
    record_id: int
    document_title: str
    issuing_body: str
    date_issued: str
    topic: str
    key_rule: str
    source_url: str
    source_section: str = ""
    source_pages: List[int] = field(default_factory=list)

    @property
    def source(self) -> str:
        """Alias for source_url — keeps legacy code using record.source working."""
        return self.source_url

    def to_dict(self) -> dict:
        return asdict(self)


# Backward-compatibility alias: existing imports of SolarRecord still work
SolarRecord = Record
