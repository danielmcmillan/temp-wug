#!/usr/bin/python3.2

import socket
import time
from logger import Logger

class RrdConnection:
    retry_delay = 5
    retry_count = 5
    value_error_log_delay = 300

    def __init__(self, address, port, db_name, sensors, update_delay, logger):
        self.db_name = db_name
        self.sensors = sensors
        self.update_delay = update_delay
        self.log = logger
        self.last_value_warning = 0
        
        #Create a socket and connect to the rrdtool server
        self.log.log("INFORMATION", "Starting RRDTOOL connection.", False)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retries = 0
        while True:
            try:
                self.socket.connect((address, int(port)))
                self.log.log("INFORMATION", "Successfully connected to RRDTOOL.", False)
                break
            except socket.error as ex:
                self.log.log("ERROR", "Failed to connect to {0}:{1}.".format(address, port), False)
                #Try again until set number of retries
                if retries >= RrdConnection.retry_count:
                    self.log.log("ERROR", "RRDTOOL not available, aborting.", True)
                    quit()
                else:
                    retries += 1
                    time.sleep(RrdConnection.retry_delay)
    
    def __enter__(self):
        return self
    
    def send_command(self, command):
        try:
            self.socket.send((command + "\n").encode("utf-8"))
        except socket.error as ex:
            self.log.log("ERROR", "Failed to communicate with RRDTOOL, aborting.", True)
            quit()
    
    def update(self, temps):
        sensors_with_error = []
        #Create the rrdtool command to update the database with the temperatures
        cmd_string = "update {0} -t ".format(self.db_name)
        values = ""
        for sensor in temps:
            cmd_string += sensor + ":"
            
            temp = temps[sensor]
            if temp == temp:
                values += ":" + str(temps[sensor])
            else:
                #Temp is NaN
                sensors_with_error.append(sensor)
                values += ":" + "U"
            
        cmd_string = cmd_string[:-1]
        cmd_string += " N" + values
        
        if len(sensors_with_error) > 0 :
            now = time.time()
            if now >= self.last_value_warning + RrdConnection.value_error_log_delay:
                self.last_value_warning = now
                warning = "There was a problem reading the value from the following sensors:\n"
                for sensor in sensors_with_error:
                    warning += sensor + "\n" 
                self.log.log("WARNING", warning, True)
            
        self.send_command(cmd_string)
        
    def create(self):
        #Create the rrdtool command to create the database file
        cmd_string = "create {0} --step {1} ".format(self.db_name, self.update_delay)
        for sensor_id in self.sensors:
            cmd_string += "DS:{0}:GAUGE:20:-55:125 ".format(sensor_id)
        cmd_string += "RRA:AVERAGE:0.5:6:1440 RRA:MAX:0.5:360:438000 RRA:MIN:0.5:360:438000 RRA:AVERAGE:0.5:360:438000"
        
        print("Creating rrd file with {0}".format(cmd_string))
        self.send_command(cmd_string)
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.socket.close()
        
    def __del__(self):
        self.socket.close()