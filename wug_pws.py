"""Module for uploading sensor data to Weather Underground PWS"""

from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError
from logger import LogLevel

class WugPws:
    """ Accumulates sensor readings and uploads them when requested."""

    def __init__(self, config, log, stale=False):
        """Initialise with given configuration.

            stale: if True, no data will actually be uploaded.
        """
        self._config = config
        self._log = log
        self._stale = stale

        # Map wug_type to [total, count]
        self._data = dict()
    
    def record_value(self, wug_type, value):
        """ Accumulates a value ready to upload.
        
            type: the wug_type for the sensor, determines the field to upload data to.
            value: a floating point value.
        """
        if wug_type in self._data:
            self._data[wug_type][0] += value
            self._data[wug_type][1] += 1
        else:
            self._data[wug_type] = [value, 1]
    
    def upload_values(self):
        """Provide accumulated values to Weather Underground"""

        # Compute averages for recorded values
        fields = dict()
        for wug_type, values in self._data.items():
            if values[1] >= self._config["min_readings"]:
                fields[wug_type] = values[0] / values[1]
            else:
                self._log.log("Not enough readings to upload value for {}".format(wug_type), LogLevel.WARNING,
                    "Got {} but require at least {}".format(values[1], self._config["min_readings"]))
            
        self._log.log("Uploading values to WUG", LogLevel.INFO, str(fields))
        self._upload_data(fields)
        
        self._data.clear()

    def _upload_data(self, data):
        """ Uploads the specified data fields to WUG

            data: a dict mapping sensor fields (wug_type) to values
        """
        if self._stale or len(data) == 0: return

        # Required configuration parameters
        get_params = {
            "action": "updateraw",
            "ID": self._config["pws_id"],
            "PASSWORD": self._config["pws_key"],
            "dateutc": datetime.utcnow().isoformat(sep=" ")
        }
        # Add the data to the parameters
        get_params.update(data)
        success = False

        # Send the request
        url = "{}?{}".format(self._config["wug_url"], urlencode(get_params))
        try:
            response = urlopen(url)
            body = response.read().decode('utf-8')
            success = "success" in body
            if success:
                self._log.log("Successfully uploaded data to WUG", LogLevel.INFO, body)
            else:
                self._log.log("Uploading to WUG was unsuccessful", LogLevel.CRITICAL, body)
        except URLError as err:
            self._log.log("Error uploading to WUG", LogLevel.CRITICAL, str(err))
        
        # TODO: back up failed uploads
        if not success:
            pass
