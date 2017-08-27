#!/usr/bin/python3

"""Program for reading temperatures from sensor devices and providing them to Weather Underground"""
import sys
import argparse
import socket
import time

from logger import Logger
from parse_json import parse_json
from wug_pws import WugPws
import w1_temp_reader

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
    log = Logger(config["log_email"])

    # Create WUG PWS for uploading data
    pws = WugPws(config["weather_underground"], log)

    read_sensors(config, logger, pws)
        
    # args.verbose: log more
    # args.noupload: stale

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
    """ Loop while reading sensor values and providing to PWS"""

    update_delay = int(config["update_delay"])
    upload_delay = int(config["upload_delay"])

    # The time when the data was last uploaded
    last_upload = time.time()

    while True:
        # Read every configured sensor and provide value to pws
        # If required time has passed, upload values
        pass

if __name__ == '__main__':
    sys.exit(int(main() or 0))