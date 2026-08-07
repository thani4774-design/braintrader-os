from dataclasses import dataclass


@dataclass
class SwingPoint:
    index: int
    date: str
    type: str
    price: float
    strength: int
    confirmed: bool = True