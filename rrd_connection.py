#!/usr/bin/python3.2

import socket

class RrdConnection:
    def __init__(self, address, port, db_name, sensors, update_delay):
        self.db_name = db_name
        self.sensors = sensors
        self.update_delay = update_delay
        
        #Create a socket and connect to the rrdtool server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((address, int(port)))
        except socket.error as ex:
            print("Failed to connect to {0}:{1}.".format(address, port))
            print("Stack trace: " + ex)
            self.connected = False
        
        self.connected = True
    
    def __enter__(self):
        return self
    
    def send_command(self, command):
        if self.connected:
            try:
                self.socket.send((command + "\n").encode("utf-8"))
            except socket.error as ex:
                print("Failed to send message to rrdtool.")
        
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