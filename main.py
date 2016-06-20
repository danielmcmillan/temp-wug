#!/usr/bin/python3

"""Program for reading temperatures from 1-wire serial devices and providing them to rrdtool"""
import sys
import argparse

from sensor_reader import SensorReader
from parse_json import parse_json

# The default config path
DEFAULT_CONFIG = "config.json"

# The default rrd config path
DEFAULT_RRD_CONFIG = "rrd_config.json"

def main():
    """Main function"""
    args = parse_arguments()

    # Load configuration
    try:
        file = args.config or DEFAULT_CONFIG
        config = parse_json(file)
        file = args.rrd_config or DEFAULT_RRD_CONFIG
        rrd_config = parse_json(file)
    except IOError as ex:
        print("Failed to load configuration file: " + ex.filename)
        quit()
    except ValueError as ex:
        print("Invalid configuration in file '{0}': {1}".format(file, ex.args[0]))
        quit()

    # Create list of sensors to be read
    sensors = {}
    for sensor_id in config["sensors"]:
        sensor = rrd_config["sensors"][sensor_id]
        sensors[sensor_id] = {
            "name": sensor["name"],
            "file": sensor["rrd_file"],
            "device": config["device_path"].replace("$", config["sensors"][sensor_id])
        }

    # Create object to read sensor devices
    reader = SensorReader(sensors)

    if (args.database):
        print("TODO: Provide to database.")
    elif (args.newrrd):
        print("TODO: Create new database.")
    else:
        # Read current temperatures and print them
        temps = reader.read_all_temps()
        for sensor in temps:
            print("{0}: {1}\N{DEGREE SIGN}C".format(sensors[sensor]["name"], temps[sensor]))

def parse_arguments():
    """ Parse command line arguments.
        Return the collection of arguments
    """
    parser = argparse.ArgumentParser(description="Read from temperature sensors.")
    parser.add_argument("-c", "--config",
        help="Specify the config file (default: {0})".format(DEFAULT_CONFIG),
        default = DEFAULT_CONFIG)
    parser.add_argument("-r", "--rrd-config",
        help="Specify the rrd config file (default: {0})".format(DEFAULT_RRD_CONFIG),
        default = DEFAULT_RRD_CONFIG)
    parser.add_argument("-d", "--database", help=
        "Connect to the configured rrd to provide temperature data", action="store_true")
    parser.add_argument("-n", "--newrrd", help=
        "Connect to rrdtool and create the database, clearing existing data", action="store_true")
    return parser.parse_args()

if __name__ == '__main__':
    sys.exit(int(main() or 0))