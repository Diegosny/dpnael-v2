from dataclasses import dataclass
from typing import Optional

@dataclass
class ContainerInfo:
    id: str
    short_id: str
    name: str
    status: str
    image: str
    command: str
    ip_address: Optional[str] = None