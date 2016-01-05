#!/usr/bin/python

import json
import argparse
import sensor_reader

default_config = "config.json"

#Parse the command line arguments
parser = argparse.ArgumentParser(description="Read from temperature sensors.")
parser.add_argument("-c", "--config", help="Specify the config file (default: " + default_config + ")", default=default_config)
rrdarg = parser.add_argument_group(title="Round Robin Database", description="Options for providing data to an rrdtool server")
#rrdarg.add_argument("-d", "--database", help="Connect to the configured rrdtool server and add temperature data to the specified rrd file")
#rrdarg.add_argument("-n", "--newrrd", help="Specifies that a new rrd file should be created instead of updating an existing database",
#    action="store_true")
args = parser.parse_args()

#Try to load the config
try:
    config = json.load(open(args.config))
    if not "device_path" in config:
        config["device_path"] = default_device
except (IOError, ValueError):
    print("Failed to load config file \"" + args.config + "\"")
    quit()
    
sensors = config["sensors"]
reader = sensor_reader.SensorReader(config["device_path"], sensors)

if (args.database == None):
    if (args.newrrd):
        print("Cannot create rrd file without connecting to rrdtool")
    else:
        #Print all of the sensor values
        temps = reader.readAllTemps()
        for sensor_id in temps:
            sensor = sensors[sensor_id]
            temp = temps[sensor_id]
            if temp == temp:
                print(sensor["name"] + ": " + str(temp) + u"\N{DEGREE SIGN}C")
            else:
                #temp is NaN
                print(sensor["name"] + ": Unknown")
else:
    print("Connect to rrdtool server")
    #Tell it to connect, get an object for the connection
    #Tell it to create a new database if required
    #Tell it to start updating
