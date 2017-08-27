"""Module for reading 1 wire serial temperature devices"""

# The path for sensor devices, with $ being a placeholder for device id
_DEVICE_PATH = "/sys/bus/w1/devices/$/w1_slave"

def read_sensor(sensor):
    """ Read the temperature from the w1-temp sensor given.
    
        Returns the temperature in degrees Farenheit as a floating point value,
        or None if an error occurs.
    """
    return _read_from_device(_DEVICE_PATH.replace("$", sensor["device_id"]))

def _read_from_device(device_path):
    """Read the temperature from the device at the specified path in degrees Farenheit"""
    try:
        # Read from the file
        file = open(device_path, "r")
        lines = file.readlines()
        file.close()
    except IOError:
        # Device not found
        return None
    if lines[0].strip()[-3:] != "YES":
        # Data transfer was unsuccessful
        return None
    # Find the temperature value
    equals_index = lines[1].find("t=")
    if equals_index == -1:
        # No value was found in the output
        return None
    # Extract the temperature value in thousandths of degrees Celsius
    tmp_str = lines[1][equals_index + 2:]
    try: tmp = float(tmp_str)
    except (ValueError): return None
    # Filter out erroneous values (85000 is default before reading has been made)
    if tmp > 60000: return None
    # Return the value in degrees Farenheit
    return tmp*0.0018 + 32
