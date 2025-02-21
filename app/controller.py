from fastapi import HTTPException
from utils.logger import logger
from datetime import datetime, timezone, timedelta
from http import HTTPStatus
import utils.config as env_vars

import app.models as models
import logging
import traceback
import jwt
import redis

# Initialize Redis client
redis_client = redis.Redis(
    host = env_vars.REDIS_HOST,
    port = env_vars.REDIS_PORT,
    db = 0,
    decode_responses=True
)

class Controller:
    def __init__(self, input_request: models.DTORequest):
        self._input_request = input_request
        self._trace_id = input_request.get('traceId')
        self._data = input_request.get('data')
        self._controller_response = models.DTOResponse()

    
    def _check_token_validity_time(self, token):
        try:
            decoded_token = jwt.decode(token, env_vars.SECRET_KEY, algorithms=[env_vars.ALGORITHM])
            exp = decoded_token.get("exp")
            remaining_time = exp - datetime.now(timezone.utc).timestamp()
            return remaining_time
        except jwt.ExpiredSignatureError:
            return 0
        except Exception as e:
            error = f"Error while checking token validity : {e=}"
            logger.error(f"Controller:validate_token():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            return -1
            
        

    def create_user(self) -> models.DTOResponse:
        try:

            # request format validation on python
            user_auth_request : models.UserAuthRequest = None
            try:
                user_auth_request : models.UserAuthRequest = models.UserAuthRequest(**self._data)
            except Exception as e:
                error = f"Invalid data field received. Error while creating the user {e}"
                logger.error(
                    f"Controller:create_user():: {error=} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response

            username = user_auth_request.username
            password = user_auth_request.password

            # User exists check
            if redis_client.exists(username):
                error = f"User already exists"
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response
            
            redis_client.set(username, password)
            message = f"User {username} stored successfully"
            logger.info(f"Controller:create_user():: {message}")
            
            self._controller_response.statusCode = HTTPStatus.CREATED
            self._controller_response.message = message
        except Exception as e:
            error = f"Error while creating the user : {e=}"
            logger.error(f"Controller:create_user():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        
        return self._controller_response

    def create_token(self) -> models.DTOResponse:
        try:

            # request format validation on python
            user_auth_request : models.UserAuthRequest = None
            try:
                user_auth_request : models.UserAuthRequest = models.UserAuthRequest(**self._data)
            except Exception as e:
                error = f"Invalid data field received. Error while creating the user {e}"
                logger.error(
                    f"Controller:create_token():: {error=} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response


            username = user_auth_request.username
            password = user_auth_request.password

            stored_password = redis_client.get(username)
            if not stored_password or stored_password != password:
                error = f"Invalid credentials received. Error while creating the token"
                logger.error(
                    f"Controller:create_token():: {error=} traceId={self._trace_id} request={self._input_request}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response
            
            # Generate JWT token
            access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=int(env_vars.ACCESS_TOKEN_EXPIRE_MINUTES))
            access_token = jwt.encode({"sub": username, "exp": access_token_expires}, env_vars.SECRET_KEY, algorithm=env_vars.ALGORITHM)
            
            # Generate Refresh Token
            refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=int(env_vars.REFRESH_TOKEN_EXPIRE_DAYS))
            refresh_token = jwt.encode({"sub": username, "exp": refresh_token_expires}, env_vars.SECRET_KEY, algorithm=env_vars.ALGORITHM)
            
            message = f"Token created successfully for {username}"
            logger.info(f"Controller:create_user():: {message}")
            self._controller_response.message = message
            self._controller_response.statusCode = HTTPStatus.CREATED
            self._controller_response.data = [{"access_token": access_token, "refresh_token": refresh_token}]

        except Exception as e:
            error = f"Error while creating the token : {e=}"
            logger.error(f"create_token():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        
        return self._controller_response
    
    def revoke_token(self) -> models.DTOResponse:
        try:

            token_revoke_request : models.TokenRequest = None
            try:
                token_revoke_request : models.TokenRequest = models.TokenRequest(**self._data)
            except Exception as e:
                error = f"Invalid data field received. Error while revoking the token {e}"
                logger.error(
                    f"Controller:revoke_token():: {error=} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response
            
            token = token_revoke_request.token
            decoded_token = jwt.decode(token, env_vars.SECRET_KEY, algorithms=[env_vars.ALGORITHM])
            exp = decoded_token.get("exp")
            redis_client.setex(token, int(exp - datetime.now(timezone.utc).timestamp()), "revoked")
            self._controller_response.message = "Token revoked successfully"
            self._controller_response.statusCode = HTTPStatus.OK
        except jwt.ExpiredSignatureError:
            self._controller_response.message = "Token already expired"
            self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
        except Exception as e:
            error = f"Error while revoking the token : {e=}"
            logger.error(f"Controller:revoke_token():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        return self._controller_response

    def renew_token(self) -> models.DTOResponse:
        try:
            token_renew_request : models.TokenRequest = None
            try:
                token_renew_request : models.TokenRequest = models.TokenRequest(**self._data)
            except Exception as e:
                error = f"Invalid data field received. Error while renewing the token {e}"
                logger.error(
                    f"Controller:renew_token():: {error=} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response
            
            refresh_token = token_renew_request.token
            decoded_token = jwt.decode(refresh_token, env_vars.SECRET_KEY, algorithms=[env_vars.ALGORITHM])
            username = decoded_token.get("sub")
            new_access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=int(env_vars.ACCESS_TOKEN_EXPIRE_MINUTES))
            new_access_token = jwt.encode({"sub": username, "exp": new_access_token_expires}, env_vars.SECRET_KEY, algorithm=env_vars.ALGORITHM)
            message = f"New access token generated successfully"
            logger.info(f"Controller:renew_token():: {message}")

            self._controller_response.message = message
            self._controller_response.statusCode = HTTPStatus.OK
            self._controller_response.data = [{"access_token": new_access_token}]
        except jwt.ExpiredSignatureError:
            self._controller_response.message = "Refresh token expired"
            self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
        except Exception as e:
            error = f"Error while renewing the token : {e=}"
            logger.error(f"Controller:renew_token():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        return self._controller_response
    

    def validate_token(self) -> models.DTOResponse:
        try:
            if not self._input_request.get('token'):
                error = f"Invalid request, token is required."
                logger.error(
                    f"Controller:validate_token():: {error=} request={self._input_request}"
                )
                self._controller_response.statusCode = HTTPStatus.BAD_REQUEST
                self._controller_response.message = error
                return self._controller_response
            
            token = self._input_request.get('token')

            if redis_client.exists(token):
                self._controller_response.message = "Token has been revoked"
                self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
                return self._controller_response

            token_validity_time = self._check_token_validity_time(token)
            if token_validity_time > 0:
                self._controller_response.message = "Token validity checked successfully"
                self._controller_response.statusCode = HTTPStatus.OK
                self._controller_response.data = [{"remaining_validity_seconds": token_validity_time}]
            elif token_validity_time == 0:
                self._controller_response.message = "Token has expired"
                self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
            else:
                self._controller_response.message = "Error while validating"
                self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            error = f"Error while checking token validity : {e=}"
            logger.error(f"Controller:validate_token():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        return self._controller_response
    
    def process_ping_pong(self) -> models.DTOResponse:
        try:
            if not self._input_request.get('token'):
                error = f"Invalid request, token is required."
                logger.error(
                    f"Controller:validate_token():: {error=} request={self._input_request}"
                )
                self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
                self._controller_response.message = error
                return self._controller_response
            
            token = self._input_request.get('token')

            if redis_client.exists(token):
                self._controller_response.message = "Token has been revoked"
                self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
                return self._controller_response

            token_validity_time = self._check_token_validity_time(token)
            if token_validity_time > 0:
                self._controller_response.message = "Succesfully played ping-pong with diwakar .... Good night"
                self._controller_response.statusCode = HTTPStatus.OK
                self._controller_response.data = [{"ping": "pong"}]
            elif token_validity_time == 0:
                self._controller_response.message = "Token has expired"
                self._controller_response.statusCode = HTTPStatus.UNAUTHORIZED
            else:
                self._controller_response.message = "Error while processing ping-pong"
                self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
        except Exception as e:
            error = f"Error while processing ping-pong : {e=}"
            logger.error(f"Controller:process_ping_pong():: {error} traceId={self._trace_id} request={self._input_request} call_stack={traceback.format_exc()}")
            self._controller_response.statusCode = HTTPStatus.INTERNAL_SERVER_ERROR
            self._controller_response.message = error
        return self._controller_response