#!/usr/bin/python3

"""Program for reading temperatures from 1-wire serial devices and providing them to rrdtool"""
import sys
import argparse
import socket
import time

from parse_json import parse_json
from sensor_reader import SensorReader
from rrd_connection import RrdConnection
from logger import Logger 

# The default config path
DEFAULT_CONFIG = "config.json"

# The default rrd config path
DEFAULT_RRD_CONFIG = "rrd_config.json"

# The delay between logging subsequent sensor read errors in seconds
READ_ERROR_LOG_DELAY = 60

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
        return 1
    except ValueError as ex:
        print("Invalid configuration in file '{0}': {1}".format(file, ex.args[0]))
        return 1

    # Create list of sensors to be read
    sensors = {}
    rrd_file = None
    for sensor_id in config["sensors"]:
        sensor = rrd_config["sensors"][sensor_id]
        if (rrd_file is None):
            rrd_file = sensor["rrd_file"]
        elif (sensor["rrd_file"] != rrd_file):
            print("Providing data to multiple rrd files is not supported")
            return 1
        sensors[sensor_id] = {
            "name": sensor["name"],
            "device": config["device_path"].replace("$", config["sensors"][sensor_id])
        }

    rrd = RrdConnection(rrd_config)

    if (args.newrrd):
        # Create database
        create_database(rrd, rrd_file)
    elif (args.database):
        # Start updating database
        log = Logger(config["email"])
        while True:
            # Connect to rrdtool
            try:
                rrd.connect(retry_attempts = config["connection_attempts"],
                    retry_delay = config["retry_delay"])
            except socket.error:
                log.log("rrdtool connection failure", send_email = True)
                break

            log.log("rrdtool connection success", send_email = True)

            try:
                provide_temps(rrd, log, config, sensors)
            except socket.error:
                if (not config["retry_after_drop"]):
                    break
    else:
        # Print current temperatures
        reader = SensorReader(sensors)
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

def create_database(rrd, rrd_file):
    """ Tell rrdtool to create the specified rrd file"""
    # Get the database creation string
    cmd_string = rrd.create_command(rrd_file)
    print("Sending command '{0}'".format(cmd_string))
    # Confirm database creation with user
    ans = input("""Are you sure you wish to continue?
        Any existing data will be permanently replaced. (y/n) """)
    if ans.lower() != "y":
        print("Aborting")
        return

    # Connect and send the command
    try:
        rrd.connect()
        rrd.send_command(cmd_string)
    except socket.error:
        print("Failed to send command")

def provide_temps(rrd, log, config, sensors):
    """ Read temperatures and provide them to the given rrdtool connection.
        On connection failure socket.error is raised.
    """
    delay = int(config["update_delay"])
    reader = SensorReader(sensors)
    # The time when the next update should occur (now)
    nextupdate = time.time()
    
    while True:
        # Read temperatures from sensors
        temps = reader.read_all_temps()
        # Log read failures
        check_readings(temps, log)
        # Send the values to rrdtool
        cmd_string = rrd.update_command(temps)
        rrd.send_command(cmd_string) # May raise socket.error
        # Set the next update time
        nextupdate += delay
        # Sleep until another update is required
        sleeptime = nextupdate - time.time()
        # Reset time and don't sleep if dropping behind
        if (sleeptime < 0):
            log.log("temp updates behind", "", send_email = True)
            nextupdate = time.time()
        else:
            time.sleep(sleeptime)

def check_readings(temps, log):
    """ Checks for failed temperature readings and logs them"""
    if (time.time() < check_readings.last_log + READ_ERROR_LOG_DELAY):
        # Already logged errors recently
        return
    error_sensors = []
    for sensor_id in temps:
        temp = temps[sensor_id]
        if (temp != temp):
            error_sensors.append(sensor_id)
    if (len(error_sensors) > 0):
        check_readings.last_log = time.time()
        error_list = ", ".join(error_sensors)
        log.log("error reading {0}".format(error_list), send_email = True)
check_readings.last_log = 0

if __name__ == '__main__':
    sys.exit(int(main() or 0))