import json
from pathlib import Path

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError


cache_file = Path('test_token.cache')


def token_updated(token):
    cache_file.write_text(json.dumps(token))


def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code


def main():
    if cache_file.is_file():
        auth = Auth(json.loads(cache_file.read_text()), token_updated)
    else:
        username = input("Username: ")
        password = input("Password: ")
        auth = Auth(None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    print(ring.devices)


if __name__ == '__main__':
    main()
