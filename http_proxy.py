import os
import logging
import aiohttp
from aiohttp import web
from authlib.jose import jwt
import time
import string
import secrets
import time
from dotenv import load_dotenv
from aiohttp import web
from aiohttp_prometheus import MetricsMiddleware

load_dotenv()


class AuthToken:
    ALGORITHM = 'HS512'
    NONCE_ALLOWED_CHARS = string.ascii_letters + string.digits
    TIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, key):
        self.key = key

    def random_string(self, len, chars):
        return ''.join(secrets.choice(chars) for i in range(len))

    # Taken from OpenId python library
    def nonce(self, when=None):
        salt = self.random_string(6, self.NONCE_ALLOWED_CHARS)
        if when is None:
            t = time.gmtime()
        else:
            t = time.gmtime(when)

        time_str = time.strftime(self.TIME_FMT, t)
        return time_str + salt

    def generate(self, payload):
        header = {'alg': self.ALGORITHM}
        claims = {
            'iat': round(time.time()),
            'jti': self.nonce(),
            'payload': payload
        }
        return jwt.encode(header, claims, self.key).decode("utf-8")


class ProxyHandler:
    TIME_FMT = '%Y-%m-%dT%H:%M:%SZ'
    HOP_BY_HOP_HEADERS = [
        "Connection",
        "Transfer-Encoding",
        "Keep-Alive",
        "Proxy-Authorization",
        "Proxy-Authentication",
        "Trailer",
        "Upgrade",  # Remove bellow
        "Content-Encoding"]

    AUTH_TOKEN_HEADER_NAME = 'x-my-jwt'

    def __init__(self):
        self.proxyed_request_counter = 0
        self.auth_token_generator = AuthToken(os.getenv('JWT_SECRET'))
        self.startup_time = time.gmtime()

    def strip_hop_by_hop_headers(self, headers):
        striped_headers = {}
        for key in headers.keys():
            if key not in self.HOP_BY_HOP_HEADERS:
                striped_headers[key] = headers[key]
        return striped_headers

    async def status(self, request):
        server_startup_time = time.strftime(self.TIME_FMT, self.startup_time)
        data = {'startupTime': server_startup_time,
                'totalProxyedRequests': self.proxyed_request_counter}
        return web.json_response(data)

    async def post_proxy(self, request):
        body = await request.text()
        request_headers = self.strip_hop_by_hop_headers(request.headers)
        auth_payload = {"user": "username", "date": "todays date"}
        request_headers[self.AUTH_TOKEN_HEADER_NAME] = self.auth_token_generator.generate(
            auth_payload)

        async with aiohttp.ClientSession() as session:
            async with session.post(os.getenv('UPSTREAM_REQ'), data=body) as resp:
                self.proxyed_request_counter += 1
                body = await resp.text()
                headers = self.strip_hop_by_hop_headers(resp.headers)
                return web.Response(body=body, status=resp.status, headers=headers)


def main():
    app = web.Application()
    proxy_handler = ProxyHandler()
    logging.basicConfig(level=logging.DEBUG)

    app.middlewares.append(MetricsMiddleware())
    app.add_routes([web.post('', proxy_handler.post_proxy),
                    web.get('/status', proxy_handler.status)])

    web.run_app(app)


if __name__ == '__main__':
    main()
