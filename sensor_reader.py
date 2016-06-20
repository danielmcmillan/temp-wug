"""Module for reading 1 wire serial temperature devices"""

class SensorReader:
    """Class for reading 1 wire serial temperature devices"""
    def __init__(self, sensors):
        self.sensors = sensors

    # Read the temperature from the specified device
    @staticmethod
    def read_from_device(device_path):
        """Read the temperature from the device at the specified path"""
        try:
            #Read from the file
            file = open(device_path, "r")
            lines = file.readlines()
            file.close()
        except IOError:
            #Device not found
            return float("NaN")
        if lines[0].strip()[-3:] != "YES":
            #Data transfer was unsuccessful
            return float("NaN")
        #Find the temperature value
        equals_index = lines[1].find("t=")
        if equals_index == -1:
            #No value was found in the output
            return float("NaN")
        #Extract the temperature value (given in thousandths of degrees Celsius)
        tmp_str = lines[1][equals_index + 2:]
        return float(tmp_str) / 1000.0

    def read_temp(self, sensor_id):
        """ Read the temperature from the sensor with the specified id.
            Returns the temperature as a floating point value, or NaN if an error occurs.
        """
        if not sensor_id in self.sensors:
            #Specified sensor does not exist
            return float("NaN")
        
        return SensorReader.read_from_device(self.sensors[sensor_id]["device"])
    
    def read_all_temps(self):
        """ Reads all sensor temperatures.
            Returns temperatures in a dictinonary indexed by sensor id.
        """
        temps = {}
        for sensor_id in self.sensors:
            temp = SensorReader.read_from_device(self.sensors[sensor_id]["device"])
            temps[sensor_id] = temp
        return temps
