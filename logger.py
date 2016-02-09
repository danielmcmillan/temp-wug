#!/usr/bin/python3
import subprocess
import socket

class Logger:
    
    def __init__(self, email_address):
        self.email_address = email_address
    
    def log(self, level, text, send_email):
        print("{0}: {1}".format(level, text))
        
        if send_email and self.email_address is not None:
            subject = "{0} from {1}".format(level, socket.gethostname())
            self.email(subject, text)
        
    def email(self, subject, body):
        if self.email_address is None:
            return
        proc = subprocess.Popen(["mail", "-s", subject, "-r", socket.gethostname(), self.email_address], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(body.encode("utf-8"))
        proc.stdin.close()