# IdentityBeta by Diwakar Singh

## Warning
.env is not supposed to be pushed but it's there for your sake

## Steps to validate the API's

```
1. Make sure you've installed docker on your system
2. Run command ```docker-compose up --build```
3. Double check if the port 8000 is occupied and runs error free through the terminal
4. Open postman and import the collection given by me to you or hit the below cURL's inorder.
5. Create the user
6. Create the token for the user
7. Validate the token validity (Either access or refresh) by passing the token in headers
8. Revoke the access token
9. Renew the access token by passing the refresh token
10. Hit the ping-pong api and pass the token in the headers.
```

## Future scope
```
1. Different secret keys or algorithms for access and refresh tokens to identify which one's being passed
2. Policies can be assigned to the users according to their authority
3. DB can be used to actually store the values and even use them after reinstantiating the app
... ... ... ... etc
```

## cURLS

User Creation : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/user' \
--header 'Content-Type: application/json' \
--data '{
    "traceId": "TEST1234",
    "data": {
        "username": "diwakar",
        "password": "diwakar"
    }
}'
```

Token Creation : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/token' \
--header 'Content-Type: application/json' \
--data '{
    "traceId": "TEST1234",
    "data": {
        "username": "diwakar",
        "password": "diwakar"
    }
}'
```

Ping-Pong along token : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/ping-pong' \
--header 'Content-Type: application/json' \
--header 'Authorization;'
```

Token Validation : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/token/validate' \
--header 'Content-Type: application/json' \
--header 'Authorization;' \
--data ''
```

Token Renewal : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/token/renew' \
--header 'Content-Type: application/json' \
--data '{
    "traceId": "TEST1234",
    "data": {
        "token" : ""
    }
}'
```

Token Revoke : 
```
curl --location 'http://localhost:8000/advait-assignment/v1/token/revoke' \
--header 'Content-Type: application/json' \
--data '{
    "traceId": "TEST1234",
    "data": {
        "token" : ""
    }
}'
```
