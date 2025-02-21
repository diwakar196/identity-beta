from fastapi import APIRouter, Request
from utils.logger import logger
from http import HTTPStatus
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.controller import Controller
import traceback
import app.models as models

router = APIRouter()

@router.post(path="/user", response_model=models.DTOResponse)
async def register_user(request: Request) -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = None
    try:
        request_body = await request.json()
        logger.info(f"register_user():: Received request to create the user : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.create_user()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while creating the user : {e=}"
        logger.error(f"register_user():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )


@router.post(path="/token", response_model=models.DTOResponse)
async def generate_token(request: Request)  -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = None
    try:
        request_body = await request.json()
        logger.info(f"generate_token():: Received request to create the token : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.create_token()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while creating the token : {e=}"
        logger.error(f"generate_token():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    

@router.post(path="/token/revoke", response_model=models.DTOResponse)
async def token_revoke(request: Request)  -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = None
    try:
        request_body = await request.json()
        logger.info(f"token_revoke():: Received request to revoke the token : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.revoke_token()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while revoking the token : {e=}"
        logger.error(f"token_revoke():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    

@router.post(path="/token/renew", response_model=models.DTOResponse)
async def token_renewal(request: Request)  -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = None
    try:
        request_body = await request.json()
        logger.info(f"token_renewal():: Received request to renew the token : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.renew_token()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while renewing the token : {e=}"
        logger.error(f"token_renewal():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )

@router.get(path="/token/validate", response_model=models.DTOResponse)
async def get_validity(request: Request)  -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = {}
    try:
        request_body['token'] = request.headers.get('authorization')
        logger.info(f"get_validity():: Received request to validate the token : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.validate_token()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while validating the token : {e=}"
        logger.error(f"get_validity():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    
@router.get(path="/ping-pong", response_model=models.DTOResponse)
async def play_ping_pong(request: Request)  -> models.DTOResponse:
    api_response = models.DTOResponse()
    request_body = {}
    try:
        request_body['token'] = request.headers.get('authorization')
        logger.info(f"play_ping_pong():: Received ping-pong request : {request_body=}")
        request_controller = Controller(input_request=request_body)
        api_response = request_controller.process_ping_pong()
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )
    except Exception as e:
        error = f"Error while processing ping-pong : {e=}"
        logger.error(f"play_ping_pong():: {error}, {request_body=}, call_stack={traceback.format_exc()}")
        api_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        api_response.message = error
        return JSONResponse(
            content=jsonable_encoder(api_response.model_dump(exclude_none=True)),
            status_code=api_response.statusCode
        )