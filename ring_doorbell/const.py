# coding: utf-8
# vim:sw=2:ts=2:et:

## Constants
HEADERS = { 'Content-Type': 'application/x-www-form-urlencoded; charset: UTF-8',
            'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.4; Build/KTU84Q)',
            'Accept-Encoding': 'gzip, deflate'}

# number of attempts to refresh token
RETRY_TOKEN = 3

API_VERSION = '9'
API_URI = 'https://api.ring.com'
DEVICES_ENDPOINT = '/clients_api/ring_devices'
DINGS_ENDPOINT = '/clients_api/dings/active'
NEW_SESSION_ENDPOINT = '/clients_api/session'
URL_HISTORY = '/clients_api/doorbots/history'
URL_RECORDING = '/clients_api/dings/{0}/recording'

POST_DATA = {
      'api_version': API_VERSION,
      'device': [{
        'os': 'android',
        'hardware_id': '180940d0-7285-3366-8c64-6ea91491982c',
        'app_brand': 'ring',
        'metadata': [{
          'device_model': 'VirtualBox',
          'resolution': '600x800',
          'app_version': '1.7.29',
          'app_instalation_date' : '',
          'os_version' : '4.4.4',
          'manufacturer': 'innotek GmbH',
          'is_tablet': 'true',
          'linphone_initialized': 'true',
          'language': 'en'
        }],
      }]}

POST_DATA = u'device%5Bos%5D=android&device%5Bhardware_id%5D=180940d0-7285-3366-8c64-6ea91491982c&device%5Bapp_brand%5D=ring&device%5Bmetadata%5D%5Bdevice_model%5D=VirtualBox&device%5Bmetadata%5D%5Bresolution%5D=600x800&device%5Bmetadata%5D%5Bapp_version%5D=1.7.29&device%5Bmetadata%5D%5Bapp_instalation_date%5D=&device%5Bmetadata%5D%5Bos_version%5D=4.4.4&device%5Bmetadata%5D%5Bmanufacturer%5D=innotek+GmbH&device%5Bmetadata%5D%5Bis_tablet%5D=true&device%5Bmetadata%5D%5Blinphone_initialized%5D=true&device%5Bmetadata%5D%5Blanguage%5D=en&api_version=9'
