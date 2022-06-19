from api.schemas.error import ErrorResult

HTTP_400_RESPONSE = {
            'description': 'Невалидная схема документа или входные данные не '
                           'верны',
            'model': ErrorResult,
            'content': {
                'application/json': {
                    'example': {
                        'code': 400,
                        'message': 'Validation Failed',
                    }
                }
            }
        }

HTTP_404_RESPONSE = {
            'description': 'Категория/товар не найден(а)',
            'model': ErrorResult,
            'content': {
                'application/json': {
                    'example': {
                        'code': 404,
                        'message': 'Item not found',
                    }
                }
            }
        }