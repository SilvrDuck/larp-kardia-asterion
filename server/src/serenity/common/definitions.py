from pydantic import BaseModel


class Ship(BaseModel):
    name: str
    hp: int
