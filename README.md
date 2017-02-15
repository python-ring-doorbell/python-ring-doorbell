This project is a Python 2.7/3.x wrapper to access the Ring.com (http://www.ring.com) doorbell.

## Install
```bash
# Installing from PyPi
$ pip install ring_doorbell  #python 2.7
$ pip3 install ring_doorbell #python 3.x

# Installing latest development
$ pip3 install git+https://github.com/tchellomello/python-ring-doorbell@dev --upgrade
```

## Usage
```python
from ring_doorbell import Ring
myring = Ring('user@email.com', 'secret')

myring.devices
{'chimes': ['Downstairs'], 'doorbells': ['Front Door']}

myring.chimes
['Downstairs']

myring.doorbells
['Front Door']

myring.chime_attributes('Downstairs')
{'address': '123 Example St, New York, NY, USA',
 'alerts': {'connection': 'online'},
 'description': 'Downstairs',
 'device_id': '1234567',
 'do_not_disturb': {'seconds_left': 0},
 'features': {'ringtones_enabled': True},
 'firmware_version': '1.1.31',
 'id': 123456,
 'kind': 'chime',
 'latitude': 00.0000000,
 'longitude': -00.000000,
 'owned': True,
 'owner': {'email': 'owner@email.com',
  'first_name': 'Owner Name',
  'id': 123456,
  'last_name': 'Owner Surname'},
 'settings': {'ding_audio_id': None,
  'ding_audio_user_id': None,
  'motion_audio_id': None,
  'motion_audio_user_id': None,
  'volume': 10},
 'time_zone': 'America/New_York'}

# for battery powered it will show a range 0-100
myring.doorbell_battery_life('Front Door')
'4107

myring.doorbell_attributes('Front Door')
{'address': '123 Example St, New York, NY, USA',
 'alerts': {'connection': 'online'},
 'battery_life': '4107',
 'description': 'Front Door',
 'device_id': '12345678',
 'external_connection': False,
 'features': {'advanced_motion_enabled': False,
  'motions_enabled': True,
  'people_only_enabled': False,
  'shadow_correction_enabled': False,
  'show_recordings': True},
 'firmware_version': '1.3.91',

  '....SNIP....' : '....SNIP....',

  'video_settings': {'ae_level': 32,
   'birton': None,
   'brightness': 16,
   'contrast': 80,
   'saturation': 48}},
 'subscribed': True,
 'subscribed_motions': True,
 'time_zone': 'America/New_York'}

myring.history(limit=2, timezone='America/Sao_Paulo')
[{'answered': False,
  'created_at': datetime.datetime(2017, 2, 14, 19, 51, 31, tzinfo=<DstTzInfo 'America/Sao_Paulo' BRST-1 day, 22:00:00 DST>),
  'doorbot': {'description': 'Front Door', 'id': 12345},
  'events': [],
  'favorite': False,
  'id': 1234,
  'kind': 'motion',
  'recording': {'status': 'ready'},
  'snapshot_url': ''},
 {'answered': False,
  'created_at': datetime.datetime(2017, 2, 14, 18, 26, 6, tzinfo=<DstTzInfo 'America/Sao_Paulo' BRST-1 day, 22:00:00 DST>),
  'doorbot': {'description': 'Front Door', 'id': 12345},
  'events': [],
  'favorite': False,
  'id': 12345,
  'kind': 'motion',
  'recording': {'status': 'ready'},
  'snapshot_url': ''}]

myring.history(name='Front Door', limit=1, timezone='America/Sao_Paulo')
[{'answered': False,
  'created_at': datetime.datetime(2017, 2, 14, 19, 51, 31, tzinfo=<DstTzInfo 'America/Sao_Paulo' BRST-1 day, 22:00:00 DST>),
  'doorbot': {'description': 'Front Door', 'id': 12345},
  'events': [],
  'favorite': False,
  'id': 1234,
  'kind': 'motion',
  'recording': {'status': 'ready'},
  'snapshot_url': ''}]

# download video
myring.doorbell_download_recording(123456, '/home/user/test.mp4')
True

# show video URL
myring.doorbell_recording_url(123456)
'https://ring-transcoded-videos.s3.amazonaws.com/123456.mp4?X-Amz-Expires=3600&X-Amz-Date=20170210T000928Z&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=zzzzzzzzzzzzAAA/20170210/us-east-1/s3/aws4_request&X-Amz-SignedHeaders=host&X-Amz-Signature=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# generate live streaming
myring.live_streaming('Front Door')
[{'audio_jitter_buffer_ms': 0,
  'device_kind': 'lpd_v1',
  'doorbot_description': 'Front Door',
  'doorbot_id': 12345,
  'expires_in': 179,
  'id': 123456,
  'id_str': '12345',
  'kind': 'on_demand',
  'motion': False,
  'now': 1486710809.55569,
  'optimization_level': 3,
  'protocol': 'sip',
  'sip_ding_id': '1234563',
  'sip_endpoints': None,
  'sip_from': 'sip:12345@ring.com',
  'sip_server_ip': '1.2.3.4',
  'sip_server_port': '15063',
  'sip_server_tls': 'false',
  'sip_session_id': '1iaaaaaaaaaq',
  'sip_to': 'sip:1iaaaaaaaaaq@1.2.3.4.5:15063;transport=tcp',
  'sip_token': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab',
  'snapshot_url': '',
  'state': 'ringing',
  'video_jitter_buffer_ms': 0}]

# push notifications (motion or ring)
 while True:
     time.sleep(3)
     print(myring.check_activity)
[]
[]
[{'audio_jitter_buffer_ms': 0,
  'device_kind': 'lpd_v1',
  'doorbot_description': 'Front Door',
  'doorbot_id': 12345,
  'expires_in': 179,
  'id': 123456,
  'id_str': '12345',
  'kind': 'on_demand',
  'motion': False,
  'now': 1486710809.55569,
  'optimization_level': 3,
  'protocol': 'sip',
  'sip_ding_id': '1234563',
  'sip_endpoints': None,
  'sip_from': 'sip:12345@ring.com',
  'sip_server_ip': '1.2.3.4',
  'sip_server_port': '15063',
  'sip_server_tls': 'false',
  'sip_session_id': '1iaaaaaaaaaq',
  'sip_to': 'sip:1iaaaaaaaaaq@1.2.3.4.5:15063;transport=tcp',
  'sip_token': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab',
  'snapshot_url': '',
  'state': 'ringing',
  'video_jitter_buffer_ms': 0}]
[]
[]
```

## Credits
- This project was inspired and based on https://github.com/jeroenmoors/php-ring-api. Many thanks @jeroenmoors.
- A guy named MadBagger at Prism19 for his initial research (http://www.prism19.com/doorbot/second-pass-and-comm-reversing/)
- The creators of mitmproxy (https://mitmproxy.org/) great http and https traffic inspector
- @mfussenegger for his post on mitmproxy and virtualbox https://zignar.net/2015/12/31/sniffing-vbox-traffic-mitmproxy/

