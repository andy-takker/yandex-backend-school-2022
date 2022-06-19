from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import get_settings
from database.engine import create_db
from api.schemas.error import ErrorResult
from api.router import router as api_router
from loguru import logger
settings = get_settings()


def get_application() -> FastAPI:
    """AppFactory"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version=settings.VERSION,
        description='Вступительное задание в Летнюю Школу '
                    'Бэкенд Разработки Яндекса 2022'
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS or ['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    application.include_router(router=api_router, prefix=settings.API_PREFIX)

    @application.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResult(code=exc.status_code,
                                message=exc.detail).dict(),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error(exc)
        return JSONResponse(
            status_code=400,
            content=ErrorResult(code=400,
                                message='Validation Failed').dict(),
        )

    return application


app = get_application()
