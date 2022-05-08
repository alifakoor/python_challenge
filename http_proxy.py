import os
import logging
import aiohttp
from aiohttp import web
from authlib.jose import jwt
import time
import secrets
import time
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()


class Proxy:
    HEADERS = [
        "Connection",
        "Transfer-Encoding",
        "Keep-Alive",
        "Proxy-Authorization",
        "Proxy-Authentication",
        "Trailer",
        "Upgrade",
        "Content-Encoding"]

    def __init__(self):
        self.request_counter = 0
        self.token = Token(os.getenv('JWT_SECRET'))
        self.uptime = time.gmtime()

    def strip_headers(self, headers):
        striped_headers = {}
        for key in headers.keys():
            if key not in self.HEADERS:
                striped_headers[key] = headers[key]
        return striped_headers

    async def status(self, request):
        uptime = time.strftime(os.getenv('DATE_FORMAT'), self.uptime)
        data = {'counter': self.request_counter, 'Uptime': uptime}
        return web.json_response(data)

    async def post(self, request):
        body = await request.text()
        request_headers = self.strip_headers(request.headers)
        payload = {"user": "username", "date": "todays date"}
        request_headers[os.getenv('TOKEN_NAME')] = self.token.generate(payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(os.getenv('UPSTREAM_REQ'), data=body) as resp:
                self.request_counter += 1
                body = await resp.text()
                headers = self.strip_headers(resp.headers)
                return web.Response(body=body, status=resp.status, headers=headers)


class Token:

    def __init__(self, key):
        self.key = key

    def generate(self, payload):
        header = {'alg': os.getenv('HASH_ALG')}
        claims = {
            'iat': round(time.time()),
            'jti': secrets.token_urlsafe(),
            'payload': payload
        }
        return jwt.encode(header, claims, self.key).decode("utf-8")


def main():
    app = web.Application()
    proxy = Proxy()
    logging.basicConfig(level=logging.DEBUG)

    app.add_routes([web.post('', proxy.post),
                   web.get('/status', proxy.status)])

    web.run_app(app, port=3000)


if __name__ == '__main__':
    main()
