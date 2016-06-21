import subprocess
import socket
import datetime

class Logger:
    """Class for logging to stdout and to email """
    def __init__(self, email_address):
        self.email_address = email_address
    
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
        
        if send_email and self.email_address is not None:
            subject = "TempReader: " + message
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
        if self.email_address is None:
            return
        proc = subprocess.Popen(["mail", "-s", subject, "-r", socket.gethostname(), self.email_address], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(body.encode("utf-8"))
        proc.stdin.close()