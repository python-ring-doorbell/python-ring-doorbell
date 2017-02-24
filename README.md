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
In [1]: from ring_doorbell import Ring
In [2]: myring = Ring('user@email.com', 'password')

In [3]: myring.devices
Out[3]:
{'chimes': [<RingChime: Downstairs>],
 'doorbells': [<RingDoorBell: Front Door>]}

In [4]: myring.chimes
Out[4]: [<RingChime: Downstairs>]

In [5]: myring.doorbells
Out[5]: [<RingDoorBell: Front Door>]

In [6]: mychime = myring.chimes[0]

In [7]: mychime.
         mychime.account_id         mychime.firmware           mychime.linked_tree        mychime.subscribed_motions
         mychime.address            mychime.id                 mychime.longitude          mychime.timezone
         mychime.debug              mychime.kind               mychime.name               mychime.update
         mychime.family             mychime.latitude           mychime.subscribed         mychime.volume
                                                                                          mychime.test_sound

In [7]: mychime.volume
Out[7]: 5

#updating volume
In [8]: mychime.volume = 200
Must be within the 0-10.

In [9]: mychime.volume = 4

In [10]: mychime.volume
Out[10]: 4

# DoorBells
In [11]: mydoorbell = myring.doorbells[0]

In [12]: mydoorbell.
                     mydoorbell.account_id                      mydoorbell.kind
                     mydoorbell.address                         mydoorbell.last_recording_id
                     mydoorbell.battery_life                    mydoorbell.latitude
                     mydoorbell.check_activity                  mydoorbell.live_streaming_json
                     mydoorbell.debug                           mydoorbell.longitude
                     mydoorbell.existing_doorbell_type          mydoorbell.name
                     mydoorbell.existing_doorbell_type_duration mydoorbell.recording_download
                     mydoorbell.existing_doorbell_type_enabled  mydoorbell.recording_url
                     mydoorbell.family                          mydoorbell.timezone
                     mydoorbell.firmware                        mydoorbell.update
                     mydoorbell.history                         mydoorbell.volume
                     mydoorbell.id

In [12]: mydoorbell.last_recording_id
Out[12]: 2222222221

In [14]: mydoorbell.existing_doorbell_type
Out[14]: 'Mechanical'

In [15]: mydoorbell.existing_doorbell_type_enabled
Out[15]: True

In [16]: mydoorbell.existing_doorbell_type_enabled = False

In [17]: mydoorbell.existing_doorbell_type_enabled
Out[17]: False
```

## Credits
- This project was inspired and based on https://github.com/jeroenmoors/php-ring-api. Many thanks @jeroenmoors.
- A guy named MadBagger at Prism19 for his initial research (http://www.prism19.com/doorbot/second-pass-and-comm-reversing/)
- The creators of mitmproxy (https://mitmproxy.org/) great http and https traffic inspector
- @mfussenegger for his post on mitmproxy and virtualbox https://zignar.net/2015/12/31/sniffing-vbox-traffic-mitmproxy/

