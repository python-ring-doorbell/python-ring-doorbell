# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
from datetime import datetime

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import os
import logging
import requests
import pytz

from ring_doorbell.utils import (
    _locator, _exists_cache, _save_cache, _read_cache)
from ring_doorbell.const import (
    API_VERSION, API_URI, CACHE_ATTRS, CACHE_FILE, CHIMES_ENDPOINT,
    CHIME_VOL_MIN, CHIME_VOL_MAX,
    DEVICES_ENDPOINT, DOORBELLS_ENDPOINT, DOORBELL_VOL_MIN, DOORBELL_VOL_MAX,
    DOORBELL_EXISTING_TYPE, DINGS_ENDPOINT, FILE_EXISTS,
    HEADERS, LINKED_CHIMES_ENDPOINT, LIVE_STREAMING_ENDPOINT,
    NEW_SESSION_ENDPOINT, MSG_BOOLEAN_REQUIRED, MSG_EXISTING_TYPE,
    MSG_GENERIC_FAIL, MSG_VOL_OUTBOUND,
    NOT_FOUND, URL_DOORBELL_HISTORY, URL_RECORDING,
    POST_DATA, PERSIST_TOKEN_ENDPOINT, PERSIST_TOKEN_DATA,
    RETRY_TOKEN, TESTSOUND_CHIME_ENDPOINT)

_LOGGER = logging.getLogger(__name__)


class Ring(object):
    """A Python Abstraction object to Ring Door Bell."""

    def __init__(self, username, password, debug=False, persist_token=False,
                 push_token_notify_url="http://localhost/", reuse_session=True,
                 cache_file=CACHE_FILE):
        """Initialize the Ring object."""
        self.is_connected = None
        self.token = None
        self.params = None
        self._persist_token = persist_token
        self._push_token_notify_url = push_token_notify_url

        self.debug = debug
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

        self.cache = CACHE_ATTRS
        self.cache['account'] = self.username
        self.cache_file = cache_file
        self._reuse_session = reuse_session

        # tries to re-use old session
        if self._reuse_session:
            self.cache['token'] = self.token
            self._process_cached_session()
        else:
            self._authenticate()

    def _process_cached_session(self):
        """Process cache_file to reuse token instead."""
        if _exists_cache(self.cache_file):
            self.cache = _read_cache(self.cache_file)

            # if self.cache['token'] is None, the cache file was corrupted.
            # of if self.cache['account'] does not match with self.username
            # In both cases, a new auth token is required.
            if (self.cache['token'] is None) or \
               (self.cache['account'] is None) or \
               (self.cache['account'] != self.username):
                self._authenticate()
            else:
                # we need to set the self.token and self.params
                # to make use of the self.query() method
                self.token = self.cache['token']
                self.params = {'api_version': API_VERSION,
                               'auth_token': self.token}

                # test if token from cache_file is still valid and functional
                # if not, it should continue to get a new auth token
                url = API_URI + DEVICES_ENDPOINT
                req = self.query(url, raw=True)
                if req.status_code == 200:
                    self._authenticate(session=req)
                else:
                    self._authenticate()
        else:
            # first time executing, so we have to create a cache file
            self._authenticate()

    def _authenticate(self, attempts=RETRY_TOKEN, session=None):
        """Authenticate user against Ring API."""
        url = API_URI + NEW_SESSION_ENDPOINT

        loop = 0
        while loop <= attempts:
            loop += 1
            try:
                if session is None:
                    req = self.session.post((url),
                                            data=POST_DATA,
                                            headers=HEADERS)
                else:
                    req = session
            except:
                raise

            # if token is expired, refresh credentials and try again
            if req.status_code == 200 or req.status_code == 201:

                # the only way to get a JSON with token is via POST,
                # so we need a special conditional for 201 code
                if req.status_code == 201:
                    data = req.json().get('profile')
                    self.token = data.get('authentication_token')

                self.is_connected = True
                self.params = {'api_version': API_VERSION,
                               'auth_token': self.token}

                if self._persist_token and self._push_token_notify_url:
                    url = API_URI + PERSIST_TOKEN_ENDPOINT
                    PERSIST_TOKEN_DATA['auth_token'] = self.token
                    PERSIST_TOKEN_DATA['device[push_notification_token]'] = \
                        self._push_token_notify_url
                    req = self.session.put((url), headers=HEADERS,
                                           data=PERSIST_TOKEN_DATA)

                # update token if reuse_session is True
                if self._reuse_session:
                    self.cache['account'] = self.username
                    self.cache['token'] = self.token

                _save_cache(self.cache, self.cache_file)
                return True

        self.is_connected = False
        req.raise_for_status()

    def query(self,
              url,
              attempts=RETRY_TOKEN,
              method='GET',
              raw=False,
              extra_params=None):
        """Query data from Ring API."""
        if self.debug:
            _LOGGER.debug("Querying %s", url)

        if self.debug and not self.is_connected:
            _LOGGER.debug("Not connected. Refreshing token...")
            self._authenticate()

        response = None
        loop = 0
        while loop <= attempts:
            if self.debug:
                _LOGGER.debug("running query loop %s", loop)

            # allow to override params when necessary
            # and update self.params globally for the next connection
            if extra_params:
                params = self.params
                params.update(extra_params)
            else:
                params = self.params

            loop += 1
            try:
                if method == 'GET':
                    req = self.session.get((url), params=urlencode(params))
                elif method == 'PUT':
                    req = self.session.put((url), params=urlencode(params))
                elif method == 'POST':
                    req = self.session.post((url), params=urlencode(params))

                if self.debug:
                    _LOGGER.debug("_query %s ret %s", loop, req.status_code)
            except:
                raise

            # if token is expired, refresh credentials and try again
            if req.status_code == 401:
                self.is_connected = False
                self._authenticate()
                continue

            if req.status_code == 200 or req.status_code == 204:
                # if raw, return session object otherwise return JSON
                if raw:
                    response = req
                else:
                    if method == 'GET':
                        response = req.json()
                break

        if self.debug:
            _LOGGER.debug("%s", MSG_GENERIC_FAIL)
        return response

    @property
    def devices(self):
        """Return all devices."""
        devs = {}
        devs['chimes'] = self.chimes
        devs['doorbells'] = self.doorbells
        return devs

    def __devices(self, device_type):
        """Private method to query devices."""
        lst = []
        url = API_URI + DEVICES_ENDPOINT
        try:
            if device_type == 'chime':
                req = self.query(url).get('chimes')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingChime(self, member))

            if device_type == 'doorbell':
                req = self.query(url).get('doorbots')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingDoorBell(self, member))

                # get shared doorbells, however device is read-only
                req = self.query(url).get('authorized_doorbots')
                for member in list((obj['description'] for obj in req)):
                    lst.append(RingDoorBell(self, member, shared=True))

        except AttributeError:
            pass
        return lst

    @property
    def chimes(self):
        """Return a list of RingDoorChime objects."""
        return self.__devices('chime')

    @property
    def doorbells(self):
        """Return a list of RingDoorBell objects."""
        return self.__devices('doorbell')


class RingGeneric(object):
    """Generic Implementation for Ring Chime/Doorbell."""

    def __init__(self):
        """Initialize Ring Generic."""
        self._attrs = None
        self._ring = None
        self.debug = None
        self.family = None
        self.name = None

        # alerts notifications
        self.alert_expires_at = None

    def __repr__(self):
        """Return __repr__."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    def update(self):
        """Refresh attributes."""
        self._get_attrs()
        self._update_alert()

    @property
    def alert(self):
        """Return alert attribute."""
        return self._ring.cache['alerts']

    @alert.setter
    def alert(self, value):
        """Set attribute to alert."""
        self._ring.cache['alerts'] = value
        _save_cache(self._ring.cache, self._ring.cache_file)
        return True

    def _update_alert(self):
        """Verify if alert received is still valid."""
        # alert is no longer valid
        if self.alert and self.alert_expires_at:
            if datetime.now() >= self.alert_expires_at:
                self.alert = None
                self.alert_expires_at = None
                _save_cache(self._ring.cache, self._ring.cache_file)

    def _get_attrs(self):
        """Return attributes."""
        url = API_URI + DEVICES_ENDPOINT
        try:
            if self.family == 'doorbots' and self.shared:
                lst = self._ring.query(url).get('authorized_doorbots')
            else:
                lst = self._ring.query(url).get(self.family)
            index = _locator(lst, 'description', self.name)
            if index == NOT_FOUND:
                return None
        except AttributeError:
            return None

        self._attrs = lst[index]
        return True

    @property
    def account_id(self):
        """Return account ID."""
        return self._attrs.get('id')

    @property
    def address(self):
        """Return address."""
        return self._attrs.get('address')

    @property
    def firmware(self):
        """Return firmware."""
        return self._attrs.get('firmware_version')

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return ID."""
        return self._attrs.get('device_id')

    @property
    def latitude(self):
        """Return latitude attr."""
        return self._attrs.get('latitude')

    @property
    def longitude(self):
        """Return longitude attr."""
        return self._attrs.get('longitude')

    @property
    def kind(self):
        """Return kind attr."""
        return self._attrs.get('kind')

    @property
    def timezone(self):
        """Return timezone."""
        return self._attrs.get('time_zone')


class RingChime(RingGeneric):
    """Implementation for Ring Chime."""

    def __init__(self, ring, name):
        """Initilize Ring chime object."""
        super(RingChime, self).__init__()
        self._attrs = None
        self._ring = ring
        self.debug = self._ring.debug
        self.family = 'chimes'
        self.name = name
        self.update()

    @property
    def volume(self):
        """Return if chime volume."""
        return self._attrs.get('settings').get('volume')

    @volume.setter
    def volume(self, value):
        if not ((isinstance(value, int)) and
                (value >= CHIME_VOL_MIN and value <= CHIME_VOL_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(CHIME_VOL_MIN,
                                                        CHIME_VOL_MAX))
            return False

        params = {
            'chime[description]': self.name,
            'chime[settings][volume]': str(value)}
        url = API_URI + CHIMES_ENDPOINT.format(self.account_id)
        self._ring.query(url, extra_params=params, method='PUT')
        self.update()
        return True

    @property
    def linked_tree(self):
        """Return doorbell data linked to chime."""
        url = API_URI + LINKED_CHIMES_ENDPOINT.format(self.account_id)
        return self._ring.query(url)

    @property
    def test_sound(self):
        """Play chime to test sound."""
        url = API_URI + TESTSOUND_CHIME_ENDPOINT.format(self.account_id)
        self._ring.query(url, method='POST')
        return True


class RingDoorBell(RingGeneric):
    """Implementation for Ring Doorbell."""

    def __init__(self, ring, name, shared=False):
        """Initilize Ring doorbell object."""
        super(RingDoorBell, self).__init__()
        self._attrs = None
        self._ring = ring
        self.shared = shared
        self.debug = self._ring.debug
        self.family = 'doorbots'
        self.name = name
        self.update()

    @property
    def battery_life(self):
        """Return battery life."""
        value = int(self._attrs.get('battery_life'))
        if value > 100:
            value = 100
        return value

    def check_alerts(self):
        """Return JSON when motion or ring is detected."""
        url = API_URI + DINGS_ENDPOINT
        self.update()

        try:
            resp = self._ring.query(url)[0]
        except (IndexError, TypeError):
            return None

        if resp:
            timestamp = resp.get('now') + resp.get('expires_in')
            self.alert = resp
            self.alert_expires_at = datetime.fromtimestamp(timestamp)

            # save to a pickle data
            if self.alert:
                _save_cache(self._ring.cache, self._ring.cache_file)
            return True
        return None

    @property
    def existing_doorbell_type(self):
        """
        Return existing doorbell type.

        0: Mechanical
        1: Digital
        2: Not Present
        """
        try:
            return DOORBELL_EXISTING_TYPE[
                self._attrs.get('settings').get('chime_settings').get('type')]
        except AttributeError:
            return None

    @existing_doorbell_type.setter
    def existing_doorbell_type(self, value):
        """
        Return existing doorbell type.

        0: Mechanical
        1: Digital
        2: Not Present
        """
        if value not in DOORBELL_EXISTING_TYPE.keys():
            _LOGGER.error("%s", MSG_EXISTING_TYPE)
            return False
        params = {
            'doorbot[description]': self.name,
            'doorbot[settings][chime_settings][type]': value}
        if self.existing_doorbell_type:
            url = API_URI + DOORBELLS_ENDPOINT.format(self.account_id)
            self._ring.query(url, extra_params=params, method='PUT')
            self.update()
            return True
        return None

    @property
    def existing_doorbell_type_enabled(self):
        """Return if existing doorbell type is enabled."""
        if self.existing_doorbell_type:
            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[2]:
                return None
            return \
                self._attrs.get('settings').get('chime_settings').get('enable')
        return False

    @existing_doorbell_type_enabled.setter
    def existing_doorbell_type_enabled(self, value):
        """Enable/disable the existing doorbell if Digital/Mechanical."""
        if self.existing_doorbell_type:

            if not isinstance(value, bool):
                _LOGGER.error("%s", MSG_BOOLEAN_REQUIRED)
                return None

            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[2]:
                return None

            params = {
                'doorbot[description]': self.name,
                'doorbot[settings][chime_settings][enable]': value}
            url = API_URI + DOORBELLS_ENDPOINT.format(self.account_id)
            self._ring.query(url, extra_params=params, method='PUT')
            self.update()
            return True
        return False

    @property
    def existing_doorbell_type_duration(self):
        """Return duration for Digital chime."""
        if self.existing_doorbell_type:
            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]:
                return self._attrs.get('settings').\
                       get('chime_settings').get('duration')
        return None

    @existing_doorbell_type_duration.setter
    def existing_doorbell_type_duration(self, value):
        """Set duration for Digital chime."""
        if self.existing_doorbell_type:

            if not ((isinstance(value, int)) and
                    (value >= DOORBELL_VOL_MIN and value <= DOORBELL_VOL_MAX)):
                _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN,
                                                            DOORBELL_VOL_MAX))
                return False

            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]:
                params = {
                    'doorbot[description]': self.name,
                    'doorbot[settings][chime_settings][duration]': value}
                url = API_URI + DOORBELLS_ENDPOINT.format(self.account_id)
                self._ring.query(url, extra_params=params, method='PUT')
                self.update()
                return True
        return None

    def history(self, limit=30, timezone=None, kind=None):
        """Return history with datetime objects."""
        # allow modify the items to return
        params = {'limit': str(limit)}

        url = API_URI + URL_DOORBELL_HISTORY.format(self.account_id)
        response = self._ring.query(url, extra_params=params)

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

        if kind:
            return list(filter(lambda array: array['kind'] == kind, response))

        return response

    @property
    def last_recording_id(self):
        """Return the last recording ID."""
        try:
            return self.history(limit=1)[0]['id']
        except (IndexError, TypeError):
            return None

    @property
    def live_streaming_json(self):
        """Return JSON for live streaming."""
        url = API_URI + LIVE_STREAMING_ENDPOINT.format(self.account_id)
        req = self._ring.query((url), method='POST', raw=True)
        if req.status_code == 204:
            url = API_URI + DINGS_ENDPOINT
            try:
                return self._ring.query(url)[0]
            except (IndexError, TypeError):
                pass
        return None

    def recording_download(self, recording_id, filename=None, override=False):
        """Save a recording in MP4 format to a file or return raw."""
        url = API_URI + URL_RECORDING.format(recording_id)
        try:
            req = self._ring.query(url, raw=True)
            if req.status_code == 200:

                if filename:
                    if os.path.isfile(filename) and not override:
                        _LOGGER.error("%s", FILE_EXISTS.format(filename))
                        return False

                    with open(filename, 'wb') as recording:
                        recording.write(req.content)
                        return True
                else:
                    return req.content
        except IOError as error:
            _LOGGER.error("%s", error)
            raise

    def recording_url(self, recording_id):
        """Return HTTPS recording URL."""
        url = API_URI + URL_RECORDING.format(recording_id)
        req = self._ring.query(url, raw=True)
        if req.status_code == 200:
            return req.url
        return False

    @property
    def subscribed(self):
        """Return if is online."""
        result = self._attrs.get('subscribed')
        if result is None:
            return False
        return True

    @property
    def subscribed_motion(self):
        """Return if is subscribed_motion."""
        result = self._attrs.get('subscribed_motions')
        if result is None:
            return False
        return True

    @property
    def volume(self):
        """Return volume."""
        return self._attrs.get('settings').get('doorbell_volume')

    @volume.setter
    def volume(self, value):
        if not ((isinstance(value, int)) and
                (value >= DOORBELL_VOL_MIN and value <= DOORBELL_VOL_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN,
                                                        DOORBELL_VOL_MAX))
            return False

        params = {
            'doorbot[description]': self.name,
            'doorbot[settings][doorbell_volume]': str(value)}
        url = API_URI + DOORBELLS_ENDPOINT.format(self.account_id)
        self._ring.query(url, extra_params=params, method='PUT')
        self.update()
        return True
