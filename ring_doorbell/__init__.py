# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import os
import logging
import requests
from urllib.parse import urlencode

from ring_doorbell.const import (
    API_VERSION, API_URI, DEVICES_ENDPOINT, DINGS_ENDPOINT,
    FILE_EXISTS, GENERIC_FAIL, HEADERS, LINKED_CHIMES_ENDPOINT,
    LIVE_STREAMING_ENDPOINT, NEW_SESSION_ENDPOINT, NOT_FOUND,
    URL_HISTORY, URL_RECORDING, POST_DATA, RETRY_TOKEN)

_LOGGER = logging.getLogger(__name__)


class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, username, password, debug=False):
        """Initialize the Ring object."""
        self.features = None
        self.is_connected = None
        self.id = None
        self.token = None
        self._params = None

        self.debug = debug
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

        self._authenticate

    @property
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
                self.id = data.get('id')
                self.is_connected = True
                self.token = data.get('authentication_token')
                self._params = {'api_version': API_VERSION,
                                'auth_token': self.token}
                return

        self.is_connected = False
        req.raise_for_status()

    def _query(self, url, attempts=RETRY_TOKEN,
               raw=False, params=None):
        """Query data from Ring API."""
        # allow to override params
        if params is None:
            params = self._params

        if self.debug:
            _LOGGER.debug("Querying %s", url)

        if self.debug and not self.is_connected:
            _LOGGER.debug("Not connected. Refreshing token...")
            self._authenticate

        response = None
        loop = 0
        while loop <= attempts:
            loop += 1
            try:
                req = self.session.get((url), params=urlencode(params))
            except:
                raise

            # if token is expired, refresh credentials and try again
            if req.status_code == 401:
                self.is_connected = False
                self._authenticate
                continue

            if req.status_code == 200:
                # if raw, return session object otherwise return JSON
                if raw:
                    response = req
                else:
                    response = req.json()

                break

        if response is None:
            _LOGGER.error(GENERIC_FAIL)
        return response

    def _locator(self, lst, key, value):
        """Return the position of a match item in list."""
        try:
            return next(index for (index, d) in enumerate(lst)
                        if d[key] == value)
        except StopIteration:
            return NOT_FOUND

    @property
    def devices(self):
        """Return all devices."""
        d = {}
        d['chimes'] = self.chimes
        d['doorbells'] = self.doorbells
        return d

    @property
    def __devices(self):
        """Private method to query devices."""
        url = API_URI + DEVICES_ENDPOINT
        return self._query(url)

    @property
    def chimes(self):
        """Return list of chimes by name."""
        req = self.__devices.get('chimes')
        return list((obj['description'] for obj in req))

    def chime_id(self, name):
        """Return chime ID."""
        return self.chime_attributes(name).get('id')

    def chime_attributes(self, name):
        """Return chime attributes."""
        lst = self.__devices.get('chimes')
        index = self._locator(lst, 'description', name)
        if index == NOT_FOUND:
            return None
        return lst[index]

    def chime_tree(self, name):
        """Return doorbell data linked to chime."""
        chime_id = self.chime_id(name)
        url = API_URI + LINKED_CHIMES_ENDPOINT.format(chime_id)
        return self._query(url)

    @property
    def doorbells(self):
        """Return list of doorbells by name."""
        req = self.__devices.get('doorbots')
        return list((obj['description'] for obj in req))

    def doorbell_attributes(self, name):
        """Return doorbell attributes."""
        lst = self.__devices.get('doorbots')
        index = self._locator(lst, 'description', name)
        if index == NOT_FOUND:
            return None
        return lst[index]

    def doorbell_id(self, name):
        """Return doorbell ID."""
        return self.doorbell_attributes(name).get('id')

    def doorbell_battery_life(self, name):
        """Return doorbell battery life."""
        return self.doorbell_attributes(name).get('battery_life')

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
        """Return JSON when motion or ring is detected"""
        url = API_URI + DINGS_ENDPOINT
        return self._query(url)

    def history(self, limit=30):
        """Return history."""
        # allow modify the items to return
        params = self._params
        params.update({'limit': str(limit)})

        url = API_URI + URL_HISTORY
        return self._query(url, params=params)

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
                _LOGGER.error(FILE_EXISTS.format(filename))
                return False

            with open(filename, 'wb') as fd:
                mp4 = self.doorbell_recording(recording_id)
                fd.write(mp4)

        except IOError as e:
            _LOGGER.error(e)
            return False
        return True

    def doorbell_recording_url(self, recording_id):
        """Return HTTPS recording URL."""
        url = API_URI + URL_RECORDING.format(recording_id)
        req = self._query(url, raw=True)
        if req.status_code == 200:
            return req.url
        return False
