=================================================
Python Ring Door Bell's documentation
=================================================

Python Ring Door Bell is a library written for Python 3.6+
that exposes the Ring.com devices as Python objects.


.. note::
    Ring.com does not provide an official API.
    The results of this project are merely from reverse engineering.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Installation
------------

.. code-block:: bash

    # Installing from PyPi
    $ pip install ring_doorbell

    # Installing latest development
    $ pip install \
        git+https://github.com/tchellomello/python-ring-doorbell@dev


Initializing your Ring object
-----------------------------

.. code-block:: python

    from pprint import pprint
    from ring_doorbell import Ring, Auth

    auth = Auth("YourProject/0.1", None, token_updated)
    auth.fetch_token(username, password)
    ring = Ring(auth)
    ring.update_data()
    devices = ring.devices()

    pprint(ring.session['profile'])

Listing devices linked to your account
--------------------------------------

.. code-block:: python

    # All devices
    devices = ring.devices()
    {'chimes': [<RingChime: Downstairs>],
    'doorbots': [<RingDoorBell: Front Door>]}

    # All doorbells
    doorbells = devices['doorbots']
    [<RingDoorBell: Front Door>]

    # All chimes
    chimes = devices['chimes']
    [<RingChime: Downstairs>]

    # All stickup cams
    stickup_cams = devices['stickup_cams']
    [<RingStickUpCam: Driveway>]


Playing with the attributes
---------------------------
.. code-block:: python

    devices = ring.devices()
    for dev in list(devices['stickup_cams'] + devices['chimes'] + devices['doorbots']):
        dev.update_health_data()
        print('Address:    %s' % dev.address)
        print('Family:     %s' % dev.family)
        print('ID:         %s' % dev.id)
        print('Name:       %s' % dev.name)
        print('Timezone:   %s' % dev.timezone)
        print('Wifi Name:  %s' % dev.wifi_name)
        print('Wifi RSSI:  %s' % dev.wifi_signal_strength)

        # setting dev volume
        print('Volume:     %s' % dev.volume)
        dev.volume = 5
        print('Volume:     %s' % dev.volume)

        # play dev test shound
        if dev.family == 'chimes':
            dev.test_sound(kind = 'ding')
            dev.test_sound(kind = 'motion')

        # turn on lights on floodlight cam
        if dev.family == 'stickup_cams' and dev.lights:
            dev.lights = 'on'


Showing door bell events
------------------------
.. code-block:: python

    devices = ring.devices()
    for doorbell in devices['doorbots']:

        # listing the last 15 events of any kind
        for event in doorbell.history(limit=15):
            print('ID:       %s' % event['id'])
            print('Kind:     %s' % event['kind'])
            print('Answered: %s' % event['answered'])
            print('When:     %s' % event['created_at'])
            print('--' * 50)

        # get a event list only the triggered by motion
        events = doorbell.history(kind='motion')


Downloading the last video triggered by ding
--------------------------------------------
.. code-block:: python

    devices = ring.devices()
    doorbell = devices['doorbots'][0]
    doorbell.recording_download(
        doorbell.history(limit=100, kind='ding')[0]['id'],
                         filename='last_ding.mp4',
                         override=True)


Displaying the last video capture URL
-------------------------------------
.. code-block:: python

    print(doorbell.recording_url(doorbell.last_recording_id))
    'https://ring-transcoded-videos.s3.amazonaws.com/99999999.mp4?X-Amz-Expires=3600&X-Amz-Date=20170313T232537Z&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=TOKEN_SECRET/us-east-1/s3/aws4_request&X-Amz-SignedHeaders=host&X-Amz-Signature=secret'


Developing
==========

.. autoclass:: ring_doorbell.Ring
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: ring_doorbell.generic.RingGeneric
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: ring_doorbell.chime.RingChime
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: ring_doorbell.doorbot.RingDoorBell
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: ring_doorbell.stickup_cam.RingStickUpCam
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: ring_doorbell.Auth
    :members:
    :undoc-members:
    :show-inheritance:

Credits && Thanks
-----------------

* This project was inspired and based on https://github.com/jeroenmoors/php-ring-api. Many thanks @jeroenmoors.
* A guy named MadBagger at Prism19 for his initial research (http://www.prism19.com/doorbot/second-pass-and-comm-reversing/)
* The creators of mitmproxy (https://mitmproxy.org/) great http and https traffic inspector
* @mfussenegger for his post on mitmproxy and virtualbox https://zignar.net/2015/12/31/sniffing-vbox-traffic-mitmproxy/
* To the project http://www.android-x86.org/ which allowed me to install Android on KVM.


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Python Ring DoorBell: https://github.com/tchellomello/python-ring-doorbell
