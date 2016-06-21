import socket
import time
from logger import Logger

# The default number of seconds between connection attempts
DEFAULT_RETRY_DELAY = 30

class RrdConnection:
    """ Class for connecting and sending commands to rrdtool to create a database
        of temperatures and update it with current values"""

    def __init__(self, rrd_config, rrd_file):
        """Create a new instance ready to connect with the specified config"""
        self.rrd_config = rrd_config
        self.rrd_file = rrd_file
        self.socket = None
        
    def connect(self, retry_attempts = 0, retry_delay = DEFAULT_RETRY_DELAY):
        """ Attempt to connect to rrdtool. On failure, socket.error is raised.
            retry_attempts: specify to enable automatic retry on failure
            retry_delay: set the delay in seconds between connection attempts
        """
        if (self.socket is not None):
            # Already connected
            return
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        retries = 0
        
        while True:
            try:
                self.socket.connect((self.rrd_config["rrd_address"], int(self.rrd_config["rrd_port"])))
                break
            except socket.error:
                # Try again until set number of retries
                if retries >= retry_attempts:
                    raise
                else:
                    retries += 1
                    time.sleep(retry_delay)
    
    def __enter__(self):
        return self
    
    def send_command(self, command):
        """ Send the specified command string to rrdtool.
            If there is no connection or a socket error occurs, socket.error is raised
        """
        if (self.socket is None):
            raise socket.error("socket not created")
        try:
            self.socket.sendall((command + "\n").encode("utf-8"))
        except socket.error:
            self.socket.close()
            self.socket = None
            raise
    
    def update_command(self, temps):
        """ Gets the command to send to rrdtool to update with the given temperatures.
            temps: dictionary of temperatures indexed by the sensor id
        """
        cmd_string = "update {0} -t ".format(self.rrd_file)
        values = ""
        for sensor_id in temps:
            cmd_string += sensor_id + ":"
            
            temp = temps[sensor_id]
            if temp == temp:
                values += ":" + str(temp)
            else:
                # Temp is NaN, set to unknown
                values += ":" + "U"
        
        # Remove the extra colon
        cmd_string = cmd_string[:-1]
        # Add the values
        cmd_string += " N" + values
        
        return cmd_string
        
    def create_command(self):
        """ Gets the command to send to rrdtool to create the database file based on
            the current configuration.
        """
        cmd_string = "create {0} --step {1} ".format(self.rrd_file, self.rrd_config["rrd_step"])
        # Add each data source
        for sensor_id in self.rrd_config["sensors"]:
            # Check whether this sensor is part of the file being created
            if (self.rrd_config["sensors"][sensor_id]["rrd_file"] != self.rrd_file):
                continue
            cmd_string += "DS:{0}:GAUGE:{1}:{2}:{3} ".format(sensor_id,
                2 * self.rrd_config["rrd_step"], self.rrd_config["min_temp"],
                self.rrd_config["max_temp"])
                
        # Add the archives
        for archive in self.rrd_config["archives"]:
            cmd_string += "RRA:{0}:{1}:{2}:{3} ".format(archive["cf"], archive["xff"],
                archive["steps"], archive["rows"])
        
        return cmd_string
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    def __del__(self):
        self.close()
    
    def close(self):
        if (self.socket is not None):
            self.socket.close()