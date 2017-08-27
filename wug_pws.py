"""Module for uploading sensor data to Weather Underground PWS"""

class WugPws:
    """ Accumulates sensor readings and uploads them when requested."""

    def __init__(self, config, log):
        """Initialise with given configuration."""
        self._config = config
        self._log = log
    
    def record_value(self, type, value):
        """ Accumulates a value ready to upload.
        
            type: the wug_type for the sensor, determines the field to upload data to.
            value: a floating point value.
        """
    
    def upload_values(self):
        """Provide accumulated values to Weather Underground"""
