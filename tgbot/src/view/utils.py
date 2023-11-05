from models import SourceModel
from view.texts import Texts, get_text


def get_selecting_db_text(databases: list[SourceModel], prefix: str = "/db"):
    message_text_parts = [
        f"{prefix}{i} {db.name}" for i, db in enumerate(databases, start=1)
    ]
    return (
        get_text("ru", Texts.SELECT_DB) + "\n" + "\n".join(message_text_parts)
    )
