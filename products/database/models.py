import datetime
import enum
import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, event, \
    select, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Connection
from sqlalchemy.orm import relationship, backref
from sqlalchemy_utils import ChoiceType

from database.base import Base
from database.engine import Session

logger = logging.getLogger('uvicorn')


class UnitType(str, enum.Enum):
    CATEGORY = 'CATEGORY'
    OFFER = 'OFFER'


class ShopUnit(Base):
    name = Column(String, nullable=False)
    date = Column(DateTime(timezone=datetime.timezone.utc), nullable=False)
    type = Column(ChoiceType(UnitType, impl=String()), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('shop_unit.id'),
                       index=True, default=None,
                       nullable=True)
    price = Column(Integer, nullable=True)

    children: List["ShopUnit"] = relationship(
        "ShopUnit",
        backref=backref('parent', remote_side='ShopUnit.id'),
        uselist=True, cascade="all, delete"
    )

    def get_child(self, index: int = 0) -> Optional["ShopUnit"]:
        if len(self.children) > index:
            return self.children[index]
        return None

    def __str__(self):
        return f'{self.name} {self.type}'

    def __repr__(self):
        return f'<ShopUnit {self.name}>'


@event.listens_for(ShopUnit, 'after_insert')
def do_something(mapper, connection: Connection, target):
    if target.parent_id is not None:
        session = Session()
        parent = session.query(ShopUnit).filter_by(id=target.parent_id).one()
        parent.date = target.date
        session.add(parent)
        session.commit()


@event.listens_for(ShopUnit, 'after_update')
def do_something(mapper, connection: Connection, target: ShopUnit):
    if target.parent_id is not None:
        session = Session()
        parent = session.query(ShopUnit).filter_by(id=target.parent_id).one()
        parent.date = target.date
        session.add(parent)
        session.commit()


def calculate_category_price(category: ShopUnit) -> \
        Optional[int]:
    """Рассчитывает среднюю стоимость товаров в категории"""
    k, s = 0, 0
    stack = [[category, 0]]
    logger.info(stack)
    logger.warning('START CALCULATING')
    while len(stack):
        logger.info(stack)
        last, index = stack[-1]
        stack[-1][1] += 1
        child = last.get_child(index)
        if child and child.type == UnitType.OFFER:
            k += 1
            s += child.price
        elif child:
            stack.append([child, 0])
        else:
            stack.pop()
    if k:
        return int(round(s / k))
    return None
