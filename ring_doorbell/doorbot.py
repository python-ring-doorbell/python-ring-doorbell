# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging
from datetime import datetime
import os
import time
import pytz


from ring_doorbell.generic import RingGeneric

from ring_doorbell.const import (
    DOORBELLS_ENDPOINT,
    DOORBELL_VOL_MIN,
    DOORBELL_VOL_MAX,
    DOORBELL_EXISTING_TYPE,
    DINGS_ENDPOINT,
    DOORBELL_KINDS,
    DOORBELL_2_KINDS,
    DOORBELL_3_KINDS,
    DOORBELL_3_PLUS_KINDS,
    DOORBELL_PRO_KINDS,
    DOORBELL_ELITE_KINDS,
    FILE_EXISTS,
    LIVE_STREAMING_ENDPOINT,
    MSG_BOOLEAN_REQUIRED,
    MSG_EXISTING_TYPE,
    MSG_VOL_OUTBOUND,
    PEEPHOLE_CAM_KINDS,
    SNAPSHOT_ENDPOINT,
    SNAPSHOT_TIMESTAMP_ENDPOINT,
    URL_DOORBELL_HISTORY,
    URL_RECORDING,
    URL_RECORDING_SHARE_PLAY,
    DEFAULT_VIDEO_DOWNLOAD_TIMEOUT,
    HEALTH_DOORBELL_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class RingDoorBell(RingGeneric):
    """Implementation for Ring Doorbell."""

    def __init__(self, ring, device_id, shared=False):
        super().__init__(ring, device_id)
        self.shared = shared

    @property
    def family(self):
        """Return Ring device family type."""
        return "authorized_doorbots" if self.shared else "doorbots"

    def update_health_data(self):
        """Update health attrs."""
        self._health_attrs = (
            self._ring.query(HEALTH_DOORBELL_ENDPOINT.format(self.id))
            .json()
            .get("device_health", {})
        )

    @property
    def model(self):
        """Return Ring device model name."""
        if self.kind in DOORBELL_KINDS:
            return "Doorbell"
        if self.kind in DOORBELL_2_KINDS:
            return "Doorbell 2"
        if self.kind in DOORBELL_3_KINDS:
            return "Doorbell 3"
        if self.kind in DOORBELL_3_PLUS_KINDS:
            return "Doorbell 3 Plus"
        if self.kind in DOORBELL_PRO_KINDS:
            return "Doorbell Pro"
        if self.kind in DOORBELL_ELITE_KINDS:
            return "Doorbell Elite"
        if self.kind in PEEPHOLE_CAM_KINDS:
            return "Peephole Cam"
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "battery":
            return self.kind in (
                DOORBELL_KINDS
                + DOORBELL_2_KINDS
                + DOORBELL_3_KINDS
                + DOORBELL_3_PLUS_KINDS
                + PEEPHOLE_CAM_KINDS
            )
        if capability == "knock":
            return self.kind in PEEPHOLE_CAM_KINDS
        if capability == "pre-roll":
            return self.kind in DOORBELL_3_PLUS_KINDS
        if capability == "volume":
            return True
        return False

    @property
    def battery_life(self):
        """Return battery life."""
        if (
            self._attrs.get("battery_life") is None
            and self._attrs.get("battery_life_2") is None
        ):
            return None

        value = 0
        if "battery_life_2" in self._attrs:
            # Camera has two battery bays
            if self._attrs.get("battery_life") is not None:
                # Bay 1
                value += int(self._attrs.get("battery_life"))
            if self._attrs.get("battery_life_2") is not None:
                # Bay 2
                value += int(self._attrs.get("battery_life_2"))
            return value

        # Camera has a single battery bay
        # Latest stickup cam can be externally powered
        value = int(self._attrs.get("battery_life"))
        if value and value > 100:
            value = 100

        return value

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
                self._attrs.get("settings").get("chime_settings").get("type")
            ]
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
            "doorbot[description]": self.name,
            "doorbot[settings][chime_settings][type]": value,
        }
        if self.existing_doorbell_type:
            url = DOORBELLS_ENDPOINT.format(self.id)
            self._ring.query(url, extra_params=params, method="PUT")
            self._ring.update_devices()
            return True
        return None

    @property
    def existing_doorbell_type_enabled(self):
        """Return if existing doorbell type is enabled."""
        if self.existing_doorbell_type:
            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[2]:
                return None
            return self._attrs.get("settings").get("chime_settings").get("enable")
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
                "doorbot[description]": self.name,
                "doorbot[settings][chime_settings][enable]": value,
            }
            url = DOORBELLS_ENDPOINT.format(self.id)
            self._ring.query(url, extra_params=params, method="PUT")
            self._ring.update_devices()
            return True
        return False

    @property
    def existing_doorbell_type_duration(self):
        """Return duration for Digital chime."""
        if self.existing_doorbell_type:
            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]:
                return self._attrs.get("settings").get("chime_settings").get("duration")
        return None

    @existing_doorbell_type_duration.setter
    def existing_doorbell_type_duration(self, value):
        """Set duration for Digital chime."""
        if self.existing_doorbell_type:

            if not (
                (isinstance(value, int))
                and (DOORBELL_VOL_MIN <= value <= DOORBELL_VOL_MAX)
            ):
                _LOGGER.error(
                    "%s", MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN, DOORBELL_VOL_MAX)
                )
                return False

            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]:
                params = {
                    "doorbot[description]": self.name,
                    "doorbot[settings][chime_settings][duration]": value,
                }
                url = DOORBELLS_ENDPOINT.format(self.id)
                self._ring.query(url, extra_params=params, method="PUT")
                self._ring.update_devices()
                return True
        return None

    def history(
        self,
        limit=30,
        timezone=None,
        kind=None,
        enforce_limit=False,
        older_than=None,
        retry=8,
    ):
        """
        Return history with datetime objects.

        :param limit: specify number of objects to be returned
        :param timezone: determine which timezone to convert data objects
        :param kind: filter by kind (ding, motion, on_demand)
        :param enforce_limit: when True, this will enforce the limit and kind
        :param older_than: return older objects than the passed event_id
        :param retry: determine the max number of attempts to archive the limit
        """
        queries = 0
        original_limit = limit

        # set cap for max queries
        if retry > 10:
            retry = 10

        while True:
            params = {"limit": str(limit)}
            if older_than:
                params["older_than"] = older_than

            url = URL_DOORBELL_HISTORY.format(self.id)
            response = self._ring.query(url, extra_params=params).json()

            # cherrypick only the selected kind events
            if kind:
                response = list(filter(lambda array: array["kind"] == kind, response))

            # convert for specific timezone
            utc = pytz.utc
            if timezone:
                mytz = pytz.timezone(timezone)

            for entry in response:
                dt_at = datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%S.000Z")
                utc_dt = datetime(
                    dt_at.year,
                    dt_at.month,
                    dt_at.day,
                    dt_at.hour,
                    dt_at.minute,
                    dt_at.second,
                    tzinfo=utc,
                )
                if timezone:
                    tz_dt = utc_dt.astimezone(mytz)
                    entry["created_at"] = tz_dt
                else:
                    entry["created_at"] = utc_dt

            if enforce_limit:
                # return because already matched the number
                # of events by kind
                if len(response) >= original_limit:
                    return response[:original_limit]

                # ensure the loop will exit after max queries
                queries += 1
                if queries == retry:
                    _LOGGER.debug(
                        "Could not find total of %s of kind %s", original_limit, kind
                    )
                    break

                # ensure the kind objects returned to match limit
                limit = limit * 2

            else:
                break

        return response

    @property
    def last_recording_id(self):
        """Return the last recording ID."""
        try:
            return self.history(limit=1)[0]["id"]
        except (IndexError, TypeError):
            return None

    @property
    def live_streaming_json(self):
        """Return JSON for live streaming."""
        url = LIVE_STREAMING_ENDPOINT.format(self.id)
        req = self._ring.query(url, method="POST")
        if req and req.status_code == 200:
            url = DINGS_ENDPOINT
            try:
                return self._ring.query(url).json()[0]
            except (IndexError, TypeError):
                pass
        return None

    def recording_download(
        self,
        recording_id,
        filename=None,
        override=False,
        timeout=DEFAULT_VIDEO_DOWNLOAD_TIMEOUT,
    ):
        """Save a recording in MP4 format to a file or return raw."""
        if not self.has_subscription:
            msg = "Your Ring account does not have an active subscription."
            _LOGGER.warning(msg)
            return False

        url = URL_RECORDING.format(recording_id)
        try:
            # Video download needs a longer timeout to get the large video file
            req = self._ring.query(url, timeout=timeout)
            if req and req.status_code == 200:

                if filename:
                    if os.path.isfile(filename) and not override:
                        _LOGGER.error("%s", FILE_EXISTS.format(filename))
                        return False

                    with open(filename, "wb") as recording:
                        recording.write(req.content)
                        return True
                else:
                    return req.content
        except IOError as error:
            _LOGGER.error("%s", error)
            raise
        return False

    def recording_url(self, recording_id):
        """Return HTTPS recording URL."""
        if not self.has_subscription:
            msg = "Your Ring account does not have an active subscription."
            _LOGGER.warning(msg)
            return False

        url = URL_RECORDING_SHARE_PLAY.format(recording_id)
        req = self._ring.query(url)
        data = req.json()
        if req and req.status_code == 200 and data is not None:
            return data["url"]
        return False

    @property
    def subscribed(self):
        """Return if is online."""
        result = self._attrs.get("subscribed")
        if result is None:
            return False
        return True

    @property
    def subscribed_motion(self):
        """Return if is subscribed_motion."""
        result = self._attrs.get("subscribed_motions")
        if result is None:
            return False
        return True

    @property
    def has_subscription(self):
        """Return boolean if the account has subscription."""
        return self._attrs.get("features").get("show_recordings")

    @property
    def volume(self):
        """Return volume."""
        return self._attrs.get("settings").get("doorbell_volume")

    @volume.setter
    def volume(self, value):
        if not (
            (isinstance(value, int)) and (DOORBELL_VOL_MIN <= value <= DOORBELL_VOL_MAX)
        ):
            _LOGGER.error(
                "%s", MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN, DOORBELL_VOL_MAX)
            )
            return False

        params = {
            "doorbot[description]": self.name,
            "doorbot[settings][doorbell_volume]": str(value),
        }
        url = DOORBELLS_ENDPOINT.format(self.id)
        self._ring.query(url, extra_params=params, method="PUT")
        self._ring.update_devices()
        return True

    @property
    def connection_status(self):
        """Return connection status."""
        return self._attrs.get("alerts").get("connection")

    def get_snapshot(self, retries=3, delay=1, filename=None):
        """Take a snapshot and download it"""
        url = SNAPSHOT_TIMESTAMP_ENDPOINT
        payload = {"doorbot_ids": [self._attrs.get("id")]}
        self._ring.query(url, method="POST", json=payload)
        request_time = time.time()
        for _ in range(retries):
            time.sleep(delay)
            response = self._ring.query(url, method="POST", json=payload).json()
            if response["timestamps"][0]["timestamp"] / 1000 > request_time:
                snapshot = self._ring.query(
                    SNAPSHOT_ENDPOINT.format(self._attrs.get("id")), raw=True
                ).content
                if filename:
                    with open(filename, "wb") as jpg:
                        jpg.write(snapshot)
                    return True
                return snapshot
        return False
