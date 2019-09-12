#This is a simple tester to trigger the video script. Run this on your own machine to trigger the RPi.
#Make sure you adjust the IP address to suit the address of your RPi

import socket

UDP_IP = "192.168.20.32"
UDP_PORT = 5005
MESSAGE = "A"

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)

data = MESSAGE.encode("UTF-8")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(data, (UDP_IP, UDP_PORT))
