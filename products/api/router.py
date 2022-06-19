import datetime
from math import floor
from typing import Dict, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND

from api.schemas.responses import HTTP_400_RESPONSE, HTTP_404_RESPONSE
from api.schemas.shop_unit import ShopUnitImportRequest, ShopUnitSchema, \
    ShopUnitStatisticResponse
from database.engine import get_session
from database.models import ShopUnit, UnitType

router = APIRouter()


@router.get('/test', name='test',tags=['Тестовый роут'])
def get_test() -> Dict[str, str]:
    """Тестовый метод для проверки запуска приложения"""
    return {'status': 'ok'}


@router.post('/imports', name='Добавляет новые товары или категории',
             status_code=200, tags=['Базовые задачи'])
def import_units(items: ShopUnitImportRequest,
                 session: Session = Depends(get_session)) -> \
        Response:
    for shopunit in items.items:
        shopunit.date = items.update_date
        shop_unit_model = session.query(ShopUnit).filter(
            ShopUnit.id == shopunit.id).one_or_none()
        if shop_unit_model is not None:
            logger.warning('find shopunit in base')
            if shop_unit_model.type != shopunit.type:
                raise HTTPException(status_code=400, detail='Validation Failed')
            for var, value in vars(shopunit).items():
                setattr(shop_unit_model, var, value) if value else None
            session.add(shop_unit_model)
        else:
            session.add(ShopUnit(**shopunit.dict()))
        session.commit()
    return Response(status_code=200)


@router.get('/nodes/{id}/',
            name='Получает информацию об элементе по идентификатору',
            response_model=ShopUnitSchema, response_model_by_alias=True,
            tags=['Базовые задачи'])
def get_unit(id: Union[UUID, str], session: Session = Depends(get_session)):
    """
    Получить информацию об элементе по идентификатору.
    При получении информации о категории также предоставляется информация о её
     дочерних элементах

    - цена категории - это средняя цена всех её товаров, включая товары дочерних
    категорий. Если категория не содержит товаров цена равна null. При
    обновлении цены товара, средняя цена категории, которая содержит этот товар,
     тоже обновляется

    """
    shopunit = session.query(ShopUnit).filter_by(id=id).one_or_none()
    if shopunit is None:
        raise HTTPException(status_code=404, detail='Item not found')
    su: ShopUnitSchema = ShopUnitSchema.from_orm(shopunit)
    if su.type == UnitType.CATEGORY:
        stack = [[su, 0, 0, 0]]
        while len(stack):
            last, index = stack[-1][0], stack[-1][1]
            child = last.get_child(index)
            if child is None:
                last.price = int(floor(stack[-1][3] / stack[-1][2]))
                if len(stack) > 1:
                    stack[-2][3] += stack[-1][3]
                    stack[-2][2] += stack[-1][2]
                stack.pop()
            else:
                stack[-1][1] += 1
                if child.type == UnitType.OFFER:
                    stack[-1][2] += 1
                    stack[-1][3] += child.price
                else:
                    stack.append([child, 0, 0, 0])
    return su


@router.delete(
    '/delete/{id}',
    name='Удаляет элемент по идентификатору',
    status_code=200,
    responses={
        200: {
            'description': 'Удаление прошло успешно',
            'model': None,
        },
        HTTP_400_BAD_REQUEST: HTTP_400_RESPONSE,
        HTTP_404_NOT_FOUND: HTTP_404_RESPONSE,
    },
    tags=['Базовые задачи']
)
def delete_unit(id: UUID,
                session: Session = Depends(get_session)) -> Response:
    """
    При удалении категории удаляются все дочерние элементы.
    Доступ к статистике (истории обновлений) удаленного элемента невозможен.
    """
    shopunit = session.query(ShopUnit).filter_by(id=id).one_or_none()
    if shopunit is None:
        raise HTTPException(status_code=404, detail='Item not found')
    try:
        session.delete(shopunit)
        session.commit()
        return Response(status_code=HTTP_200_OK)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=400, detail='Validation Failed')


@router.get('/sales', status_code=200, tags=['Дополнительные задачи'],
            response_model=ShopUnitStatisticResponse)
def get_sales(date: datetime.datetime, session: Session = Depends(get_session)) -> ShopUnitStatisticResponse:
    """
    Получение списка товаров, цена которых была обновлена за последние 24 часа
    от времени переданном в запросе. Обновление цены не означает её изменение.
    Обновления цен удаленных товаров недоступны. При обновлении цены товара,
    средняя цена категории, которая содержит этот товар, тоже обновляется.
    """
    logger.info(date)
    items = session.query(ShopUnit).filter(
        ShopUnit.type == UnitType.OFFER,
        ShopUnit.date <= date,
        ShopUnit.date >= date - datetime.timedelta(days=1),
    ).all()
    return ShopUnitStatisticResponse(items=items)