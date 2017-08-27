import subprocess
import socket
import datetime

EMAIL_SUBJECT = "Weather Underground Reader"

# TODO: log levels, some only show in verbose, some only in local output, some emailed
# TODO: record time of last email sent, accumulate errors in single email.

class Logger:
    """Class for logging to stdout and to email """
    def __init__(self, email_address, min_email_period):
        self._email_address = email_address
        self._min_email_period = min_email_period
    
    def log(self, message, detail = "", send_email = False):
        """ Logs the specified message
            detail: optional extra details
            send_email: whether to send out an email
        """
        timestamp = Logger.get_timestamp()

        if (detail):
            print("{0}: {1} - {2}".format(timestamp, message, detail))
        else:
            print("{0}: {1}".format(timestamp, message))
        
        if send_email and self._email_address:
            subject = EMAIL_SUBJECT + ": " + message
            if detail:
                text = "Time: {0}\nOrigin: {3}\n{1}\n{2}".format(
                    timestamp, message, detail, socket.gethostname())
            else:
                text = "Time: {0}\nOrigin: {2}\n{1}".format(
                    timestamp, message, socket.gethostname())
            self.email(subject, text)
    
    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def email(self, subject, body):
        if self._email_address is None:
            return
        proc = subprocess.Popen(["mail", "-s", subject, "-r", socket.gethostname(), self._email_address], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(body.encode("utf-8"))
        proc.stdin.close()