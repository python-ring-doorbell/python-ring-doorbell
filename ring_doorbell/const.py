# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants."""
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

LINKED_CHIMES_ENDPOINT = CHIMES_ENDPOINT + '/linked_doorbots'
LIVE_STREAMING_ENDPOINT = DOORBELLS_ENDPOINT + '/vod'
NEW_SESSION_ENDPOINT = '/clients_api/session'
TESTSOUND_CHIME_ENDPOINT = CHIMES_ENDPOINT + '/play_sound'
URL_DOORBELL_HISTORY = DOORBELLS_ENDPOINT + '/history'
URL_RECORDING = '/clients_api/dings/{0}/recording'

# structure acquired from reverse engineering to create auth token
POST_DATA = {
    'api_version': API_VERSION,
    'device[os]': 'android',
    'device[hardware_id]': '180940d0-aaaa-bbbb-8c64-6ea91491982c',
    'device[app_brand]': 'ring',
    'device[metadata][device_model]': 'KVM',
    'device[metadata][resolution]': '600x800',
    'device[metadata][app_version]': '1.7.29',
    'device[metadata][app_instalation_date]': '',
    'device[metadata][os_version]': '4.4.4',
    'device[metadata][manufacturer]': 'innotek GmbH',
    'device[metadata][is_tablet]': 'true',
    'device[metadata][linphone_initialized]': 'true',
    'device[metadata][language]': 'en'}


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
