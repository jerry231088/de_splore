from dataclasses import dataclass
from datetime import datetime

@dataclass
class ImageStructure:
    id: str
    title: str
    batch_name: str
    url: str
    downloaded_at: datetime
    image: bytes
