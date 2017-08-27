#!/usr/bin/python3

"""Program for reading temperatures from sensor devices and providing them to Weather Underground"""
import sys
import argparse
import time

from logger import Logger
from logger import LogLevel
from parse_json import parse_json
from wug_pws import WugPws
import w1_temp_reader

# TODO: detect erroneous readings

# The default config path
DEFAULT_CONFIG = "config.json"

# The module to use for each type of sensor hardware
SENSOR_MODULES = {
    "w1-temp": w1_temp_reader
}

def main():
    """Main function"""
    args = parse_arguments()

    # Load configuration
    try:
        file = args.config or DEFAULT_CONFIG
        config = parse_json(file)
    except IOError as ex:
        print("Failed to load configuration file: " + ex.filename)
        return 1
    except ValueError as ex:
        print("Invalid configuration in file '{0}': {1}".format(file, ex.args[0]))
        return 1
    
    # Create logger
    log = Logger(args.verbose, config["log_email"], config["min_email_period"])

    # Create WUG PWS for uploading data
    pws = WugPws(config["weather_underground"], log, args.noupload)

    read_sensors(config, log, pws)

def parse_arguments():
    """ Parse command line arguments.

        Return the collection of arguments
    """
    parser = argparse.ArgumentParser(description="Provide sensor data to Weather Underground.")
    # Add config option
    parser.add_argument("-c", "--config",
        help="Specify the config file (default: {0})".format(DEFAULT_CONFIG),
        default = DEFAULT_CONFIG)
    # Add verbose option
    parser.add_argument("-v", "--verbose",
        help="Output all sensor readings and averaged values.",
        action="store_true")
    # Add disable upload option
    parser.add_argument("-n", "--noupload",
        help="Run without actually sending any data to WUG.",
        action="store_true")

    return parser.parse_args()

def read_sensors(config, log, pws):
    """Loop while reading sensor values and providing to PWS"""

    update_delay = int(config["update_delay"])
    upload_delay = int(config["upload_delay"])
    
    # The time when the data was last uploaded
    last_upload = time.time()

    while True:
        # Read every configured sensor and provide value to pws
        for sensor in config["sensors"]:
            # Get the module required to read the value
            reader = SENSOR_MODULES.get(sensor["hw_type"])
            if not reader:
                log.log("Unable to read sensors with hw_type {}".format(sensor["hw_type"]))
            # Read the value and log errors
            value = reader.read_sensor(sensor)
            if not value:
                log.log("Error reading {} sensor for {}".format(sensor["hw_type"],
                    sensor["wug_type"]), LogLevel.CRITICAL)
                continue
            log.log("Read value {} from sensor for {}".format(value, sensor["wug_type"]), LogLevel.INFO)

            # Record the value
            pws.record_value(sensor["wug_type"], value)
        
        # If required time has passed, upload values
        if last_upload + upload_delay <= time.time():
            pws.upload_values()
            last_upload = time.time()

        time.sleep(update_delay)

if __name__ == '__main__':
    sys.exit(int(main() or 0))
