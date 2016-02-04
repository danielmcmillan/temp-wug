#!/usr/bin/python3.2

class SensorReader:

    def __init__(self, device_paths, sensors):
        self.device_paths = device_paths
        self.sensors = sensors

    #Read the temperature for the sensor specified
    def readTemp(self, sensor_id):
        if not sensor_id in self.sensors:
            #Specified sensor does not exist
            return float("NaN")
        sensor = self.sensors[sensor_id]
        #Get the path for this device
        device = sensor["device"]
        device_path = self.device_paths.replace("$", device)
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
    
    #Read all sensor temperatures
    def readAllTemps(self):
        temps = {}
        for sensor_id in self.sensors:
            temp = self.readTemp(sensor_id)
            temps[sensor_id] = temp
        return temps