import subprocess
import socket
import datetime
import time
from enum import Enum

EMAIL_SUBJECT = "Weather Underground Reader"

# TODO: send email after _min_email_period, requires async

class LogLevel(Enum):
    """ Log levels for Logger.

        - info is for verbose mode only
        - warning is for local logging only
        - critical is for email logging if configured
    """
    INFO = 0
    WARNING = 1
    CRITICAL = 2

class Logger:
    """Class for logging to stdout and to email """
    def __init__(self, verbose=False, email_address=None, min_email_period=None):
        self._verbose = verbose
        self._email_address = email_address
        self._min_email_period = min_email_period

        self._last_email = 0
        self._email_messages = []
    
    def log(self, message, level=LogLevel.WARNING, detail = ""):
        """ Logs the specified message.

            level: the log level, see logger.LogLevel
            detail: optional extra details
        """
        # Ignore INFO level if not verbose
        if level == LogLevel.INFO and not self._verbose:
            return

        # Get the log text
        timestamp = Logger._get_timestamp()
        text = "{} {}: {}".format(timestamp, level.value, message)
        if detail:
            text += " - {}".format(detail)
        
        # Log locally
        print(text)
        
        # Add to email queue if critical
        if level == LogLevel.CRITICAL and self._email_address:
            self._email_messages.append(text)
            self._send_email()
    
    @staticmethod
    def _get_timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _send_email(self):
        if len(self._email_messages == 0):
            return
        
        body = "<ul><li>{}</li></ul>".format("</li><li>".join(self._email_messages))
        proc = subprocess.Popen(["mail", "-s", EMAIL_SUBJECT, "-r", socket.gethostname(), self._email_address], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(body.encode("utf-8"))
        proc.stdin.close()
