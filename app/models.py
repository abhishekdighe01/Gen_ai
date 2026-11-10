
from dataclasses import dataclass
from typing import List


@dataclass
class SolarRecord:
    record_id: int
    topic: str
    key_rule: str
    source: str
    source_section: str
    source_pages: List[int]
