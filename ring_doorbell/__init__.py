# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
from urllib.parse import urlencode
from datetime import datetime

import os
import logging
import requests
import pytz

from ring_doorbell.const import (
    API_VERSION, API_URI, DEVICES_ENDPOINT, DINGS_ENDPOINT,
    FILE_EXISTS, GENERIC_FAIL, HEADERS, LINKED_CHIMES_ENDPOINT,
    LIVE_STREAMING_ENDPOINT, NEW_SESSION_ENDPOINT, NOT_FOUND,
    URL_HISTORY, URL_RECORDING, POST_DATA, RETRY_TOKEN)
from ring_doorbell.utils import _locator

_LOGGER = logging.getLogger(__name__)


class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, username, password, debug=False):
        """Initialize the Ring object."""
        self.features = None
        self.is_connected = None
        self._id = None
        self.token = None
        self._params = None

        self.debug = debug
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

        self._authenticate()

    def _authenticate(self, attempts=RETRY_TOKEN):
        """Authenticate user against Ring API."""
        url = API_URI + NEW_SESSION_ENDPOINT

        loop = 0
        while loop <= attempts:
            loop += 1
            try:
                req = self.session.post((url), data=POST_DATA, headers=HEADERS)
            except:
                raise

            # if token is expired, refresh credentials and try again
            if req.status_code == 201:
                data = req.json().get('profile')
                self.features = data.get('features')
                self._id = data.get('id')
                self.is_connected = True
                self.token = data.get('authentication_token')
                self._params = {'api_version': API_VERSION,
                                'auth_token': self.token}
                return True

        self.is_connected = False
        req.raise_for_status()

    def _query(self, url, attempts=RETRY_TOKEN,
               raw=False, extra_params=None):
        """Query data from Ring API."""
        if self.debug:
            _LOGGER.debug("Querying %s", url)

        if self.debug and not self.is_connected:
            _LOGGER.debug("Not connected. Refreshing token...")
            self._authenticate()

        response = None
        loop = 0
        while loop <= attempts:

            # allow to override params when necessary
            # and update self._params globally for the next connection
            if extra_params:
                params = self._params
                params.update(extra_params)
            else:
                params = self._params

            loop += 1
            try:
                req = self.session.get((url), params=urlencode(params))
            except:
                raise

            # if token is expired, refresh credentials and try again
            if req.status_code == 401:
                self.is_connected = False
                self._authenticate()
                continue

            if req.status_code == 200:
                # if raw, return session object otherwise return JSON
                if raw:
                    response = req
                else:
                    response = req.json()

                break

        if response is None and self.debug:
            _LOGGER.debug(GENERIC_FAIL)
        return response

    @property
    def has_subscription(self):
        """Return if account has subscription."""
        try:
            return self.features.get('subscriptions_enabled')
        except AttributeError:
            return NOT_FOUND

    @property
    def devices(self):
        """Return all devices."""
        devs = {}
        devs['chimes'] = self.chimes
        devs['doorbells'] = self.doorbells
        return devs

    @property
    def __devices(self):
        """Private method to query devices."""
        url = API_URI + DEVICES_ENDPOINT
        return self._query(url)

    @property
    def chimes(self):
        """Return list of chimes by name."""
        try:
            req = self.__devices.get('chimes')
            return list((obj['description'] for obj in req))
        except AttributeError:
            return NOT_FOUND

    def chime_id(self, name):
        """Return chime ID."""
        try:
            return self.chime_attributes(name).get('id')
        except AttributeError:
            return NOT_FOUND

    def chime_attributes(self, name):
        """Return chime attributes."""
        try:
            lst = self.__devices.get('chimes')
            index = _locator(lst, 'description', name)
            if index == NOT_FOUND:
                return NOT_FOUND
            return lst[index]
        except AttributeError:
            return NOT_FOUND

    def chime_get_volume(self, name):
        """Return if chime volume."""
        try:
            return self.chime_attributes(name).get('settings').get('volume')
        except AttributeError:
            return NOT_FOUND

    def chime_firmware(self, name):
        """Return firmware."""
        try:
            return self.chime_attributes(name).get('firmware_version')
        except AttributeError:
            return NOT_FOUND

    def is_chime_online(self, name):
        """Return if chime is online."""
        try:
            result = self.chime_attributes(name).get('subscribed')
            if result is None:
                return False
        except AttributeError:
            return NOT_FOUND
        return True

    def is_chime_subscribed_motions(self, name):
        """Return if chime is subscribed_motions."""
        try:
            result = self.chime_attributes(name).get('subscribed_motions')
            if result is None:
                return False
        except AttributeError:
            return NOT_FOUND
        return True

    def chime_tree(self, name):
        """Return doorbell data linked to chime."""
        chime_id = self.chime_id(name)
        url = API_URI + LINKED_CHIMES_ENDPOINT.format(chime_id)
        return self._query(url)

    @property
    def doorbells(self):
        """Return list of doorbells by name."""
        try:
            req = self.__devices.get('doorbots')
            return list((obj['description'] for obj in req))
        except AttributeError:
            return NOT_FOUND

    def doorbell_attributes(self, name):
        """Return doorbell attributes."""
        try:
            lst = self.__devices.get('doorbots')
            index = _locator(lst, 'description', name)
            if index == NOT_FOUND:
                return NOT_FOUND
            return lst[index]
        except AttributeError:
            return NOT_FOUND

    def doorbell_id(self, name):
        """Return doorbell ID."""
        try:
            return self.doorbell_attributes(name).get('id')
        except AttributeError:
            return NOT_FOUND

    def doorbell_get_volume(self, name):
        """Return volume."""
        try:
            return self.doorbell_attributes(name). \
                   get('settings').get('doorbell_volume')
        except AttributeError:
            return NOT_FOUND

    def is_doorbell_online(self, name):
        """Return state for doorbell is online."""
        try:
            result = self.doorbell_attributes(name).get('subscribed')
            if result is None:
                return False
        except AttributeError:
            return NOT_FOUND
        return True

    def is_doorbell_subscribed_motions(self, name):
        """Return if doorbell is subscribed."""
        try:
            result = self.doorbell_attributes(name).get('subscribed_motions')
            if result is None:
                return False
        except AttributeError:
            return NOT_FOUND
        return True

    def doorbell_battery_life(self, name):
        """Return doorbell battery life."""
        try:
            value = int(self.doorbell_attributes(name).get('battery_life'))
            if value > 100:
                value = 100
            return value
        except AttributeError:
            return NOT_FOUND

    def doorbell_firmware(self, name):
        """Return doorbell firmware."""
        try:
            return self.doorbell_attributes(name).get('firmware_version')
        except AttributeError:
            return NOT_FOUND

    def doorbell_timezone(self, name):
        """Return doorbell timezone."""
        try:
            return self.doorbell_attributes(name).get('time_zone')
        except AttributeError:
            return NOT_FOUND

    def __live_streaming_create_session(self, name):
        """Initiate session live streaming URL."""
        door_id = self.doorbell_id(name)
        url = API_URI + LIVE_STREAMING_ENDPOINT.format(door_id)
        req = self.session.post((url), params=urlencode(self._params))
        if req.status_code == 204:
            return True
        return False

    def live_streaming(self, name):
        """Return JSON for live streaming."""
        ret = self.__live_streaming_create_session(name)
        if ret:
            url = API_URI + DINGS_ENDPOINT
            return self._query(url)
        return False

    @property
    def check_activity(self):
        """Return JSON when motion or ring is detected."""
        url = API_URI + DINGS_ENDPOINT
        return self._query(url)

    def history(self, limit=30, timezone=None):
        """Return history with datetime objects."""
        # allow modify the items to return
        params = {'limit': str(limit)}
        url = API_URI + URL_HISTORY

        response = self._query(url, extra_params=params)

        # convert for specific timezone
        utc = pytz.utc
        if timezone:
            mytz = pytz.timezone(timezone)

        for entry in response:
            dt_at = datetime.strptime(entry['created_at'],
                                      '%Y-%m-%dT%H:%M:%S.000Z')
            utc_dt = datetime(dt_at.year, dt_at.month, dt_at.day, dt_at.hour,
                              dt_at.minute, dt_at.second, tzinfo=utc)
            if timezone:
                tz_dt = utc_dt.astimezone(mytz)
                entry['created_at'] = tz_dt
            else:
                entry['created_at'] = utc_dt
        return response

    def doorbell_recording(self, recording_id):
        """Return recording in MP4 format."""
        url = API_URI + URL_RECORDING.format(recording_id)
        req = self._query(url, raw=True)
        if req.status_code == 200:
            return req.content
        return None

    def doorbell_download_recording(self, recording_id,
                                    filename, override=False):
        """Download and save recording in MP4 format to a file."""
        try:
            if os.path.isfile(filename) and not override:
                _LOGGER.error("%s", FILE_EXISTS.format(filename))
                return False

            with open(filename, 'wb') as recording:
                mp4 = self.doorbell_recording(recording_id)
                recording.write(mp4)

        except IOError as error:
            _LOGGER.error("%s", error)
            return False
        return True

    def doorbell_recording_url(self, recording_id):
        """Return HTTPS recording URL."""
        url = API_URI + URL_RECORDING.format(recording_id)
        req = self._query(url, raw=True)
        if req.status_code == 200:
            return req.url
        return False
