from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, root_validator
from loguru import logger
from database.models import UnitType


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    return dt.isoformat(timespec='milliseconds', ).replace('+00:00', 'Z')


class ShopUnitBaseSchema(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID] = Field(alias='parentId')
    price: Optional[int]
    type: UnitType
    date: Optional[datetime]

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
        orm_mode = True
        allow_population_by_field_name = True

        json_encoders = {
            datetime: convert_datetime_to_iso_8601_with_z_suffix
        }


class ShopUnitImport(ShopUnitBaseSchema):

    @root_validator
    def check_price_type(cls, values):
        price = values.get('price')
        type = values.get('type')
        assert (UnitType(type) == UnitType.CATEGORY and price is None) or (
                UnitType(type) == UnitType.OFFER and price >= 0)
        return values


class ShopUnitImportRequest(BaseModel):
    items: List[ShopUnitImport]
    update_date: datetime = Field(alias='updateDate')


class ShopUnitSchema(ShopUnitBaseSchema):
    children: List["ShopUnitSchema"] = None

    @validator("children")
    def replace_empty_list(cls, v):
        return v or None

    def get_child(self, index):
        if len(self.children) > index:
            return self.children[index]
        return None


class ShopUnitStatisticResponse(BaseModel):
    items: List[ShopUnitBaseSchema]

    class Config:
        orm_mode = True


ShopUnitSchema.update_forward_refs()
