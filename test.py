# ignore this, I am a dumb dumb and learning python, was testing with this.
from ring_doorbell import Ring
# from ring_doorbell.auth import Auth


def callback():
    auth_code = input('2FA code:')
    return auth_code


username = input('Username:')
password = input('Password:')
ring = Ring(username, password, callback)
print(ring.devices)
print(ring.devices)
print(ring.devices)
print(ring.devices)
print(ring.devices)
