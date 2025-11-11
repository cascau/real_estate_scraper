from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    judet: Optional[str]
    zona: Optional[str]
    lat: Optional[float]
    lng: Optional[float]

    id: Optional[int] = None