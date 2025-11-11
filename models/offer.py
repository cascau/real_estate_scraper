from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Offer:
    url: str
    sursa: str
    active: bool = True

    id: Optional[int] = None

    titlu: Optional[str] = None
    pret: Optional[int] = None

    judet: Optional[str] = None
    oras: Optional[str] = None
    zona: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None

    tip_proprietate: Optional[str] = None
    tip_tranzactie: Optional[str] = None
    tip_vanzator: Optional[str] = None

    descriere: Optional[str] = None
    data_postarii: Optional[datetime] = None

    suprafata: Optional[str] = None
    numar_camere: Optional[int] = None
    etaj: Optional[str | int] = None
    compartimentare: Optional[str] = None
    an_constructie: Optional[str] = None

    imagini: Optional[list[str]] = None