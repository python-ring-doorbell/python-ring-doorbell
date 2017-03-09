# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants."""
from uuid import uuid4 as uuid

HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset: UTF-8',
           'User-Agent': 'Dalvik/1.6.0 (Linux; Android 4.4.4; Build/KTU84Q)',
           'Accept-Encoding': 'gzip, deflate'}

# number of attempts to refresh token
RETRY_TOKEN = 3

# code when item was not found
NOT_FOUND = -1

# API endpoints
API_VERSION = '9'
API_URI = 'https://api.ring.com'
CHIMES_ENDPOINT = '/clients_api/chimes/{0}'
DEVICES_ENDPOINT = '/clients_api/ring_devices'
DINGS_ENDPOINT = '/clients_api/dings/active'
DOORBELLS_ENDPOINT = '/clients_api/doorbots/{0}'
PERSIST_TOKEN_ENDPOINT = '/clients_api/device'

LINKED_CHIMES_ENDPOINT = CHIMES_ENDPOINT + '/linked_doorbots'
LIVE_STREAMING_ENDPOINT = DOORBELLS_ENDPOINT + '/vod'
NEW_SESSION_ENDPOINT = '/clients_api/session'
TESTSOUND_CHIME_ENDPOINT = CHIMES_ENDPOINT + '/play_sound'
URL_DOORBELL_HISTORY = DOORBELLS_ENDPOINT + '/history'
URL_RECORDING = '/clients_api/dings/{0}/recording'

# default values
CHIME_VOL_MIN = 0
CHIME_VOL_MAX = 10

DOORBELL_VOL_MIN = 0
DOORBELL_VOL_MAX = 11

DOORBELL_EXISTING_TYPE = {
    0: 'Mechanical',
    1: 'Digital',
    2: 'Not Present'}

# error strings
MSG_BOOLEAN_REQUIRED = "Boolean value is required."
MSG_EXISTING_TYPE = "Integer value where {0}.".format(DOORBELL_EXISTING_TYPE)
MSG_GENERIC_FAIL = 'Sorry.. Something went wrong...'
FILE_EXISTS = 'The file {0} already exists.'
MSG_VOL_OUTBOUND = 'Must be within the {0}-{1}.'

# structure acquired from reverse engineering to create auth token
POST_DATA = {
    'api_version': API_VERSION,
    'device[hardware_id]': str(uuid()),
    'device[os]': 'android',
    'device[app_brand]': 'ring',
    'device[metadata][device_model]': 'KVM',
    'device[metadata][device_name]': 'Python',
    'device[metadata][resolution]': '600x800',
    'device[metadata][app_version]': '1.3.806',
    'device[metadata][app_instalation_date]': '',
    'device[metadata][manufacturer]': 'Qemu',
    'device[metadata][device_type]': 'desktop',
    'device[metadata][architecture]': 'desktop',
    'device[metadata][language]': 'en'}

PERSIST_TOKEN_DATA = {
    'api_version': API_VERSION,
    'device[metadata][device_model]': 'KVM',
    'device[metadata][device_name]': 'Python',
    'device[metadata][resolution]': '600x800',
    'device[metadata][app_version]': '1.3.806',
    'device[metadata][app_instalation_date]': '',
    'device[metadata][manufacturer]': 'Qemu',
    'device[metadata][device_type]': 'desktop',
    'device[metadata][architecture]': 'x86',
    'device[metadata][language]': 'en'}
