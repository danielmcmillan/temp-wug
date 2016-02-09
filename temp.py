#!/usr/bin/python3

import json
import argparse
import time
from sensor_reader import SensorReader
from rrd_connection import RrdConnection
from logger import Logger

default_config = "config.json"
#todo: add more default values

#Parse the command line arguments
parser = argparse.ArgumentParser(description="Read from temperature sensors.")
parser.add_argument("-c", "--config", help = "Specify the config file (default: " + default_config + ")",
    default=default_config)

rrdarg = parser.add_argument_group(title="Round Robin Database",
    description="Options for providing data to an rrdtool server")
rrdarg.add_argument("-d", "--database", help= "Connect to the configured rrd and provide temperature " +
    "data with the configured interval", action="store_true")
rrdarg.add_argument("-n", "--newrrd", help=
    "Connect to rrdtool and create the database, clearing existing data", action="store_true")
rrdarg.add_argument("-e", "--email", help = "Enable email notifications", default = None)
args = parser.parse_args()

#Try to load the config
try:
    config = json.load(open(args.config))
except (IOError, ValueError) as ex:
    print("Failed to load config file \"" + args.config + "\"")
    print("Stack trace: " + str(ex))
    quit()
    
if not "device_path" in config:
    config["device_path"] = default_device
    
sensors = config["sensors"]
reader = SensorReader(config["device_path"], sensors)

if not (args.database or args.newrrd):
    #Print all of the sensor values
    temps = reader.readAllTemps()
    for sensor_id in temps:
        sensor = sensors[sensor_id]
        temp = temps[sensor_id]
        if temp == temp:
            print(sensor["name"] + ": " + str(temp) + "\N{DEGREE SIGN}C")
        else:
            #temp is NaN
            print(sensor["name"] + ": Unknown")
            print
else:
    #Start the logger
    log = Logger(args.email)
    with RrdConnection(config["rrd_address"], config["rrd_port"], config["database_name"],
            sensors, config["update_delay"], log) as rrd:
        if (args.newrrd):
            #Create the database
            ans = input("Are you sure you want to create database {0}? ".format(config["database_name"]) +
                "Existing data will be permanently removed. (y/n) ")
            if ans.lower() == "y":
                rrd.create()
        else:
            log.log("INFORMATION", "Starting to provide temperature data for " + config["database_name"], True)
            #Start performing updates
            delay = int(config["update_delay"])
            nextupdate = time.time()
            
            while True:
                rrd.update(reader.readAllTemps())
                nextupdate += delay
                
                #Sleep until the next delay second interval
                sleeptime = nextupdate - time.time()
                #Dont sleep and reset if dropping behind
                if (sleeptime < 0):
                    log.log("WARNING", "Dropping behind in temperature updates.", True)
                    nextupdate = time.time()
                else:
                    time.sleep(sleeptime)
                
            