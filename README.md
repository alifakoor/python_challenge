# Castlab Challenge Python HTTP Proxy

This was the assignement i got from Castlabs.

Your task is to build an HTTP proxy (see definition in [RFC2616](https://www.ietf.org/rfc/rfc2616.txt)) that takes a `POST` request and appends a `JSON Web Token` with the following claims:
- `iat` - Timestamp of the request as specified by the specification
- `jti`- A cryptographic nonce that should be unique
- `payload` - A json payload of the structure: `{"user": "username", "date": "todays date"}`

The JWT should be signed with the following hex string secret using the `HS512` alogrithm as in the JWT spec:

```a9ddbcaba8c0ac1a0a812dc0c2f08514b23f2db0a68343cb8199ebb38a6d91e4ebfb378e22ad39c2d01 d0b4ec9c34aa91056862ddace3fbbd6852ee60c36acbf```

Append the JWT as the `x-my-jwt` header to the upstream post request.

The upstream post endpoint can be any dummy endpoint. For example you can write your own or use something like https://reqres.in or https://postman-echo.com

## Requirements:
- Use Python3.6+
- Please use whatever libraries are necessary
- Use Docker and provide a docker-compose.yml file in at least `version '2'`
- Provide a `Makefile` with following targets:
  - `build` to build the application
  - `run` to execute what's needed to run the server. You can use `HTTP_PORT` variable to specify on which port the proxy binds
- Deliver the project via a public GitHub repository

## Bonus Points:
- Provide `/status` page with
  - time from start
  - number of requests processed
- Use asyncronous programming
- Provide tests covering the functionality
- Extend `Makefile` with a `test` target executing the tests covering the functionality