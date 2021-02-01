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

#######################################################################################
# DUAL MONITOR 2 x VIDEO PLAYER:
# -No triggers, just plays back 2 separate videos on 2 separate monitors with loops
#######################################################################################

import sys
import os
import subprocess
import psutil
import time
import threading

###############################################################
# file locations for media
###############################################################
movie1 = ("/home/pi/video/video1.mp4")
movie2 = ("/home/pi/video/video2.mp4")

##################################################################
#variables for making sure we only trigger each video player once:
##################################################################
needtostart1 = 1
needtostart2 = 1
mode = 0

################################################################################
#Redirecting console output to null so we don't litter the window with feedback
################################################################################
FNULL = open(os.devnull,'w')

#########################################################################
#Main looping
#########################################################################
try:

	while True:
		###################################################################
		#Base looping video
		###################################################################
		if (mode == 0):
			if (needtostart1 == 1):
				needtostart1 = 0
				#for troubleshooting: uncomment
				print("Starting main holding video")
				m = subprocess.Popen(['omxplayer', '--display', '2', '-b', '--no-osd', movie1], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)

			else:
				#Not needed on base loop, but in case of crash
				#Check for end of video
				if m.poll() is not None:
					#Relaunch the process to start again
					needtostart1 = 1

			if (needtostart2 == 1):
				needtostart2 = 0
				#for troubleshooting
				print("Starting second monitor video")
				n = subprocess.Popen(['omxplayer', '--display', '7', '-b', '--no-osd', movie2], stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)

			else:
				#to sense ending and restart
				if n.poll() is not None:
					#Relaunch the process to start again
					needtostart2 = 1

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
