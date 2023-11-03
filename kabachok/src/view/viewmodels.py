from dataclasses import dataclass


@dataclass
class DatabaseViewModel:
    id: str
    name: str

    def to_dict(self):
        return dict(id=self.id, name=self.name)

    @staticmethod
    def from_dict(db_dict: dict) -> "DatabaseViewModel":
        return DatabaseViewModel(id=db_dict["id"], name=db_dict["name"])
