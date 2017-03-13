How To Use It
=============

Initializing your Ring object
-----------------------------

.. code-block:: python

    from ring_doorbell import Ring
    myring = Ring('foo@bar', 'secret')

    myring.is_connected
    True

    myring.has_subscription
    True

    Chimes
    ------

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

Getting/setting attributes
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
