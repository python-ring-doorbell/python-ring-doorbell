This project is a Python wrapper to access the Ring.comd doorbell.

Currently Ring.com does not offer an official API.

## Usage
```python
from ring_doorbell import Ring
myring = Ring('user@me.com', 'secret')

# get features
 myring.features

# get quantity of chimes
myring.get_chimes_quantity

# get quantity of doorbells
myring.get_doorbells_quantity

# get history
myring.get_history

# get devices
myring.get_devices

# download video
video = myring.get_recording(video_id)
```

## Credits
- This project was inspired and based on https://github.com/jeroenmoors/php-ring-api. Many thanks @jeroenmoors.
- A guy named MadBagger at Prism19 for his initial research (http://www.prism19.com/doorbot/second-pass-and-comm-reversing/)
- The creators of mitmproxy (https://mitmproxy.org/) great http and https traffic inspector
- @mfussenegger for his post on mitmproxy and virtualbox https://zignar.net/2015/12/31/sniffing-vbox-traffic-mitmproxy/

