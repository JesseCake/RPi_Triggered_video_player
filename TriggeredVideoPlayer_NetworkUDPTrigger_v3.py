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
# -Clears the console and removes the blinking cursor
# -Listens for A or B to trigger video 1 or 2 in order
# -Plays holding video whilst waiting to be triggered
# -Returns to main holding video after playing triggered videos
# -Listens on all interfaces on UDP port 5005
# -Ensure the packets you send are encoded to byte in utf-8 encoding
#####################################################################

import sys
import os
from subprocess import Popen
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
currentplayer = 0
running = 0
hasrun = 0
finishedloop = 0
mode = 0

##################################################################
#layer counter (keeps videos on top of each other) - to look at
##################################################################
n = 0

################################################################################
#Redirecting console output to null so we don't litter the window with feedback
################################################################################
FNULL = open(os.devnull,'w')

###############################################################################
# Let's clear the terminal and cursor so we don't see them between videos
# Comment these out if you want the console to stay there for troubleshooting
###############################################################################
#Let's get those permissions sorted to access the terminal (in case they're not right)
os.system("sudo chmod 666 /dev/tty1")
#Turn off the blinking cursor
os.system("setterm -cursor off > /dev/tty1")
#then send a bunch of zeros to the first screen to clear it out
os.system("sudo dd if=/dev/zero of=/dev/fb0")
#finally let's disable console blanking (screensaver)
#os.system("setterm -blank 0 > /dev/tty1")
#this command doesn't work anymore, right now it's best to
#add "consoleblank=0" to the end of the line at /boot/cmdline.txt

##############################################
##bits for starting and stopping players
##############################################
def getplayers():
	procs = []
	for p in psutil.process_iter():
		if p.name() == 'omxplayer.bin':
			procs.append(p)
	return procs

def killoldplayers(procs):
	for p in procs:
		p.kill()


#########################################################################################################
# Set up UDP listening thread, always running (no return). Listening on UDP port 5005 on all interfaces
# If a UDP packet comes in, it will listen for a byte decoded using utf-8 to ASCII "A" or "B" to trigger
# It will also dump what it receives for troubleshooting purposes.
#########################################################################################################

def rec_UDP():
	global needtostart
	global mode
	global n
	while True:
		#UDP commands for listening
		UDP_PORT = 5005
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(('', UDP_PORT))
		data, addr = sock.recvfrom(1024)
		#Print to the console what data we got (for troubleshooting)
		print ("received message:", data)
		#These are the matching messages, change to suit your needs
		TRIGGER1TEXT = 'A'
		TRIGGER2TEXT = 'B'
		#Decode the received byte into ASCII
		RCVTEXT = data.decode("UTF-8")
		if (RCVTEXT == TRIGGER1TEXT):
			print ("received correct data! Let's trigger video 1")
			mode = 1
			needtostart = 1
			n += 1
		elif (RCVTEXT == TRIGGER2TEXT):
			print ("received correct data! Let's trigger video 2")
			mode = 2
			needtostart = 1
			n += 1

######################################################################################
#load the threads for network receiving packets as thread in background (no blocking)
######################################################################################

listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()

##########################################################
# Video endpoint checker for non looping videos
##########################################################
def videoendcheck():
	global currentplayer
	global finishedloop
	global needtostart
	global hasrun
	global running
	###########################################################################
	#madness for keeping check on finished videos
	#firstly we see if there are processes listed in the players list
	if players:
		for eachProcess in players:
		#print(eachProcess.pid)
	#then we dump the details (should be just one entry) into a variable to 
	#remember the last valid result (list clears when no processes available)
			if (eachProcess.pid > 0):
				currentplayer = eachProcess.pid
	#otherwise if there are no valid results, we check for conditions to kick 
	#a new video into gear (video has finished/quit)
	#also this protects startup problems with a "currentplayer" with the
	#initial zero in it
	else:
		if (currentplayer != 0 and hasrun == 1 and running == 0):
			needtostart = 1
			finishedloop = 1
	###########################################################################
	#check to see if the last successful process store checks out to still exist
	#also store that it's running (takes time to start)
	if psutil.pid_exists(currentplayer):
		#print("player is running")
		hasrun = 1
	#if it has quit, then we set a variable to say it's not running
	#this will then feed into the above "else" for an empty list, and check if 
	#we need to kick a new video in (to not start many processes)
	else:
		print("player has quit")
		running = 0



#########################################################################
#Main looping
#########################################################################
try:

	while True:

		players = getplayers()
		#print(players)
		###################################################################
		#Base looping video
		###################################################################
		if (mode == 0):
			if (needtostart == 1):
				needtostart = 0
				print("Starting main holding video")
				cmd = "omxplayer --no-keys -b --loop --no-osd --layer %d %s "%(n,startmovie)
				Popen(cmd, shell=True, stdout=FNULL,stderr=FNULL)
				running = 1
				hasrun = 0
				killoldplayers(players)
			else:
				#not needed on base loop, but in case of crash
				videoendcheck()

		###################################################################
		#Triggered video 1
		###################################################################
		elif (mode == 1):
			if (needtostart == 1):
				print("Starting first triggered video")
				needtostart = 0
				cmd = "omxplayer --no-keys -b --no-osd --layer %d %s "%(n,movie1)
				Popen(cmd, shell=True, stdout=FNULL,stderr=FNULL)
				running = 1
				hasrun = 0
				killoldplayers(players)
			else:
				videoendcheck()
				#return back to start
				if (needtostart == 1):
					mode = 0

		###################################################################
		#Triggered video 2
		###################################################################
		elif (mode == 2):
			if (needtostart == 1):
				print("Starting second triggered video")
				needtostart = 0
				cmd = "omxplayer --no-keys -b --no-osd --layer %d %s "%(n,movie2)
				Popen(cmd, shell=True, stdout=FNULL,stderr=FNULL)
				running = 1
				hasrun = 0
				killoldplayers(players)
			else:
				videoendcheck()
				#return back to start
				if (needtostart == 1):
					mode = 0

#when killed, get rid of players and any other stuff that needs doing
finally:
	#make sure all players are killed fully off
	os.system('killall omxplayer.bin')
	#turn the blinking cursor back on in the terminal
	os.system("setterm -cursor on > /dev/tty1")
