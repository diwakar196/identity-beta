from pydantic import BaseModel, Field
from typing import Optional, List, Union
from http import HTTPStatus

class UserAuthRequest(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    token: str

class DTORequest(BaseModel):
    traceId: str
    data: Union[UserAuthRequest, TokenRequest]


class DTOResponse(BaseModel):
    message: Optional[str] = Field(default=None)
    statusCode: Optional[HTTPStatus] = Field(default=None)
    data: Optional[List] = Field(default=None)