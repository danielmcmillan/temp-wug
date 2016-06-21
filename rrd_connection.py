import socket
import time
from logger import Logger

# The default number of seconds between connection attempts
DEFAULT_RETRY_DELAY = 30

class RrdConnection:
    """ Class for connecting and sending commands to rrdtool to create a database
        of temperatures and update it with current values"""

    def __init__(self, rrd_config):
        """Create a new instance ready to connect with the specified config"""
        self.rrd_config = rrd_config
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
                self.socket.connect((self.rrd_config["rrd_address"], self.rrd_config["rrd_port"]))
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
    
    def update(self, temps):
        """ Send a command to rrdtool to update with the given temperatures.
            temps: dictionary of temperatures indexed by the sensor id
        """
        #TODO
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
        
    def create_command(self, rrd_file):
        """ Gets the command to send to rrdtool to create the specified database file
            based on the current configuration.
        """
        cmd_string = "create {0} --step {1} ".format(rrd_file, self.rrd_config["rrd_step"])
        # Add each data source
        for sensor_id in self.rrd_config["sensors"]:
            # Check whether this sensor is part of the file being created
            if (self.rrd_config["sensors"]["sensor_id"]["rrd_file"] != rrd_file):
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
        self.socket.close()
        
    def __del__(self):
        self.socket.close()