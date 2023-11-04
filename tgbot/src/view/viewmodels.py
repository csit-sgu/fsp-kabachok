from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class SourceModel:
    id: str
    name: str

    def to_dict(self):
        return dict(id=self.id, name=self.name)

    @staticmethod
    def from_dict(db_dict: dict) -> "DatabaseViewModel":
        return SourceModel(id=db_dict["id"], name=db_dict["name"])


class DatabaseFromFile(BaseModel):
    display_name: str
    db_url: str
