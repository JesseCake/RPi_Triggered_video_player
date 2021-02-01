#Copyright Jesse Stevens @ Cake Industries 12/9/19
#icing@cake.net.au www.cake.net.au
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#####################################################################
# BRAND NEW UDP PACKET TRIGGERED VIDEO PLAYER:
# -Removed console clearing from here, better to run on external shell script
# -Listens for A or B to trigger video 1 or 2 in order
# -Plays holding video whilst waiting to be triggered
# -Returns to main holding video after playing triggered videos
# -Listens on all interfaces on UDP port 5005
# -Ensure the packets you send are encoded to byte in utf-8 encoding
#####################################################################

import sys
import os
import subprocess
import psutil
import time
import threading
import socket

###############################################################
# file locations for media
###############################################################
startmovie = ("/home/pi/video/start.mp4")
movie1 = ("/home/pi/video/video1.mp4")
movie2 = ("/home/pi/video/video2.mp4")

##################################################################
#variables for making sure we only trigger each video player once:
##################################################################
needtostart = 1
running = 0
mode = 0

################################################################################
#Redirecting console output to null so we don't litter the window with feedback
################################################################################
FNULL = open(os.devnull,'w')

#########################################################################################################
# Set up UDP listening thread, always running (no return). Listening on UDP port 5005 on all interfaces
# If a UDP packet comes in, it will listen for a byte decoded using utf-8 to ASCII "A" or "B" to trigger
# It will also dump what it receives for troubleshooting purposes.
#########################################################################################################

def rec_UDP():
	global needtostart
	global mode
	while True:
		#UDP commands for listening
		UDP_PORT = 5005
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', UDP_PORT))
		data, addr = sock.recvfrom(1024)
		#Print to the console what data we got (for troubleshooting: uncomment)
		#print ("received message:", data)
		#These are the matching messages, change to suit your needs
		TRIGGER1TEXT = 'A'
		TRIGGER2TEXT = 'B'
		SHUTDOWNTEXT = 'S'
		#Decode the received byte into ASCII
		RCVTEXT = data.decode("UTF-8")
		if (RCVTEXT == TRIGGER1TEXT):
			#for troubleshooting: uncomment
			#print ("received correct data! Let's trigger video 1")
			mode = 1
			needtostart = 1
		elif (RCVTEXT == TRIGGER2TEXT):
			#for troubleshooting: uncomment
			#print ("received correct data! Let's trigger video 2")
			mode = 2
			needtostart = 1
		elif (RCVTEXT == SHUTDOWNTEXT):
			#requires that we allow this sudo command without password
			os.system('sudo halt')

######################################################################################
#load the threads for network receiving packets as thread in background (no blocking)
######################################################################################

listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()

#########################################################################
#Main looping
#########################################################################
try:

	while True:
		###################################################################
		#Base looping video
		###################################################################
		if (mode == 0):
			if (needtostart == 1):
				needtostart = 0
				#for troubleshooting: uncomment
				print("Starting main holding video")
				m = subprocess.Popen(['omxplayer', '--loop', '-b', '--no-osd', startmovie], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)
				#Set the current running to start video (for killing logic)
				running = 0

			else:
				#Not needed on base loop, but in case of crash
				#Check for end of video
				if m.poll() is not None:
					#Relaunch the process to start again
					needtostart = 1

		###################################################################
		#Triggered video 1
		###################################################################
		elif (mode == 1):
			if (needtostart == 1):
				#kill off other videos first
				if (running == 0):
					print("Killing start video")
					m.stdin.write(b'q')
					m.stdin.flush()
					#Let's sink the boot in
					m.kill()
				elif (running == 1):
					print("Killing video 1 (restarting it)")
					a.stdin.write(b'q')
					a.stdin.flush()
					#Let's sink the boot in
					a.kill()
				elif (running == 2):
					print("Killing video 2")
					b.stdin.write(b'q')
					b.stdin.flush()
					#Let's sink the boot in
					b.kill()

				#for troubleshooting: uncomment
				print("Starting first triggered video")
				needtostart = 0
				a = subprocess.Popen(['omxplayer', '-b', '--no-osd', movie1], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)
				#Set the current running to video 1 (for killing logic)
				running = 1
			else:
				#End checking:
				#if process has quit
				if a.poll() is not None:
					#go back to start video/holding frame
					mode = 0
					needtostart = 1
				#return back to start
				if (needtostart == 1):
					mode = 0
					a.kill()
		###################################################################
		#Triggered video 2
		###################################################################
		elif (mode == 2):
			if (needtostart == 1):
				#kill off other videos first
				if (running == 0):
					print("Killing start video")
					m.stdin.write(b'q')
					m.stdin.flush()
					#Let's sink the boot in
					m.kill()
				elif (running == 1):
					print("Killing video 1")
					a.stdin.write(b'q')
					a.stdin.flush()
					#Let's sink the boot in
					a.kill()
				elif (running == 2):
					print("Killing video 2 (Restarting it)")
					b.stdin.write(b'q')
					b.stdin.flush()
					#Let's sink the boot in
					b.kill()

				#for troubleshooting: uncomment
				print("Starting first triggered video")
				needtostart = 0
				b = subprocess.Popen(['omxplayer', '-b', '--no-osd', movie2], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)
				#Set the current running to video 2 (for killing logic)
				running = 2
			else:
				#End checking:
				#if process has quit
				if b.poll() is not None:
					#go back to start video/holding frame
					mode = 0
					needtostart = 1
				#return back to start
				if (needtostart == 1):
					mode = 0
					b.kill()

		#give the loop some breathing space (eases up on resources, but delays response by 100ms)
		time.sleep(0.1)

#when killed, get rid of players and any other stuff that needs doing
finally:
	#make sure all players are killed fully off
	os.system('killall omxplayer.bin')
	os.system('killall omxplayer')
	#turn the blinking cursor back on in the terminal
	#os.system("setterm -cursor on > /dev/tty1")
	print("Quitting, Goodbye!")
