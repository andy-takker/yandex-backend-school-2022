import re
import uuid

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    __name__: str
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, nullable=False, default=uuid.uuid4)

    @declared_attr
    def __tablename__(cls) -> str:
        name_list = re.findall(r"[A-Z][a-z\d]*", cls.__name__)
        return "_".join(name_list).lower()