from pydantic import BaseModel


class ErrorResult(BaseModel):
    code: int
    message: str