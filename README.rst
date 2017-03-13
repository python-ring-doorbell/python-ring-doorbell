=================================================
Python Ring Door Bell's documentation
=================================================

.. image:: https://badge.fury.io/py/ring-doorbell.svg
    :target: https://badge.fury.io/py/ring-doorbell

.. image:: https://travis-ci.org/tchellomello/python-ring-doorbell.svg?branch=master
    :target: https://travis-ci.org/tchellomello/python-ring-doorbell

.. image:: https://coveralls.io/repos/github/tchellomello/python-ring-doorbell/badge.svg
    :target: https://coveralls.io/github/tchellomello/python-ring-doorbell


Python Ring Door Bell is a library written in Python 2.7/3x
that exposes the Ring.com devices as Python objects.


Initializing your Ring object
-----------------------------

.. code-block:: python

    from ring_doorbell import Ring
    myring = Ring('foo@bar', 'secret')

    myring.is_connected
    True

    myring.has_subscription
    True


Listing devices linked to your account
------------------------------------------

.. code-block:: python

    # All devices
    myring.devices
    {'chimes': [<RingChime: Downstairs>],
    'doorbells': [<RingDoorBell: Front Door>]}

    # All chimes
    myring.chimes
    [<RingChime: Downstairs>]

    # All door bells
    myring.doorbells
    [<RingDoorBell: Front Door>]

Playing with the attributes
--------------------------------
.. code-block:: python

    for dev in list(myring.chimes + myring.doorbells):

        # refresh data
        dev.update()

        print('Account ID: %s' % dev.account_id)
        print('Address:    %s' % dev.address)
        print('Family:     %s' % dev.family)
        print('ID:         %s' % dev.id)
        print('Name:       %s' % dev.name)
        print('Timezone:   %s' % dev.timezone)

        # setting dev volume
        print('Volume:     %s' % dev.volume)
        dev.volume = 5
        print('Volume:     %s' % dev.volume)

        # play dev test shound
        if dev.family == 'chimes'
            dev.test_sound


Showing door bell events
------------------------
.. code-block:: python

    for doorbell in myring.doorbells:

        # listing the last 15 events of any kind
        for event in doorbell.history(limit=15):
            print('ID:       %s' % event['id'])
            print('Kind:     %s' % event['kind'])
            print('Answered: %s' % event['answered'])
            print('When:     %s' % event['created_at'])
            print('--' * 50)

        # get a event list only the triggered by motion
        events = doorbell.history(kind='motion')


Download the last video triggerd by ding
----------------------------------------
.. code-block:: python

    doorbell = myring.doorbells[0]
    doorbell.recording_download(
        doorbell.history(limit=100, kind='ding')[0]['id'],
                         filename='/home/user/last_ding.mp4',
                         override=True)

*Ring.com does not provide an official API. The results of this project are merely from reverse engineering.*


Credits && Thanks
-----------------

* This project was inspired and based on https://github.com/jeroenmoors/php-ring-api. Many thanks @jeroenmoors.
* A guy named MadBagger at Prism19 for his initial research (http://www.prism19.com/doorbot/second-pass-and-comm-reversing/)
* The creators of mitmproxy (https://mitmproxy.org/) great http and https traffic inspector
* @mfussenegger for his post on mitmproxy and virtualbox https://zignar.net/2015/12/31/sniffing-vbox-traffic-mitmproxy/
* To the project http://www.android-x86.org/ which allowed me to install Android on KVM.


.. _Python Ring DoorBell: https://github.com/tchellomello/python-ring-doorbell
