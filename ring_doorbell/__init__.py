# coding: utf-8
# vim:sw=2:ts=2:et:
import logging
import json
import requests
from urllib.parse import urlencode

from ring_doorbell.const import (
    API_VERSION, API_URI, DEVICES_ENDPOINT, DINGS_ENDPOINT,
    HEADERS, NEW_SESSION_ENDPOINT, URL_HISTORY,
    URL_RECORDING, POST_DATA, RETRY_TOKEN)

_LOGGER = logging.getLogger(__name__)


class Ring(object):
  """A Python Abstraction object to Ring Door Bell"""

  def __init__(self, username, password, debug=False):
    """Initialize the Ring object"""
    self.features = None
    self.is_connected = None
    self.id = None
    self.token = None
    self.params = None

    self.debug = debug
    self.username = username
    self.password = password
    self.session = requests.Session()
    self.session.auth = (self.username, self.password)

    self._authenticate

  @property
  def _authenticate(self, attempts=RETRY_TOKEN):
    """Authenticate user against Ring API"""
    url = API_URI + NEW_SESSION_ENDPOINT

    loop = 0
    while loop <= attempts:
      loop += 1
      #req = session.post((url), data=urlencode(POST_DATA), headers=HEADERS)
      req = self.session.post((url), data=POST_DATA, headers=HEADERS)

      # if token is expired, refresh credentials and try again
      if req.status_code == 201:
        data = req.json().get('profile')
        self.features = data.get('features')
        self.id = data.get('id')
        self.is_connected = True
        self.token = data.get('authentication_token')
        self.params = {'api_version': API_VERSION, 'auth_token': self.token}
        break

    self.is_connected = False
    req.raise_for_status()

  def _query(self, url, attempts=RETRY_TOKEN):
    """Query data from Ring API"""
    if self.debug:
      _LOGGER.debug("Querying %s", url)

    if not self.is_connected:
      _LOGGER.info("Not connected. Refreshing token...")
      self._authenticate

    response = None
    loop = 0
    while loop <= attempts:
      loop += 1
      req = self.session.get((url), params=urlencode(self.params))

      # if token is expired, refresh credentials and try again
      if req.status_code == 401:
        self.is_connected = False
        self._authenticate
        continue

      if req.status_code == 200:
        if req.json():
          response = req.json()
          break

    if response is None:
      _LOGGER.error("Error!!")
    return response

  @property
  def poll(self):
    """Check current activity"""
    url = API_URI + DINGS_ENDPOINT
    return self._query(url)

  @property
  def get_devices(self):
    """Get devices"""
    url = API_URI + DEVICES_ENDPOINT
    return self._query(url)

  def get_recording(self, recording_id):
    """Download recording in MP4 format"""
    url = API_URI + URL_RECORDING.format(recording_id)
    req = self.session.get((url), params=urlencode(self.params))
    if req.status_code == 200:
      return req.content
    return None

  @property
  def get_history(self):
    """Get history"""
    url = API_URI + URL_HISTORY
    return self._query(url)

  @property
  def get_chimes_quantity(self):
    """Get number of chimes"""
    res = self.get_devices
    return len(res.get('chimes'))

  @property
  def get_doorbells_quantity(self):
    """Get number of doorbells"""
    res = self.get_devices
    return len(res.get('doorbots'))
