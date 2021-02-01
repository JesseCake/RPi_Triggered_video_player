#Copyright Jesse Stevens @ Cake Industries 26/3/18
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


import RPi.GPIO as GPIO
import sys
import os
from subprocess import Popen
import psutil
import time

##############################################################
# GPIO Pin in/out setup
##############################################################
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

###############################################################
# file locations for media
###############################################################
startmovie = ("/home/pi/video/start.mov")
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

#############
#who knows..
#############
FNULL = open(os.devnull,'w')


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


##########################################################
# threaded callbacks for interrupt driven button triggers
# --more work to do here - link over to named triggers--
##########################################################
def pressed17(channel):
    global needtostart
    global mode
    global n
    print("17 triggered")
    mode = 1
    needtostart = 1
    n += 1

def pressed18(channel):
    global needtostart
    global mode
    global n
    print("18 triggered")
    mode = 2
    needtostart = 1
    n += 1

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
# Definition of callback functions to physical button mapping
#########################################################################
GPIO.add_event_detect(17, GPIO.FALLING, callback=pressed17, bouncetime=300)
GPIO.add_event_detect(18, GPIO.FALLING, callback=pressed18, bouncetime=300)

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
            		print("starting main start loop")
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
			    print("beginning trigger 17 sequence")
			    needtostart = 0
                cmd = "omxplayer --no-keys -b --no-osd --layer %d %s "%(n,movie1)
                Popen(cmd, shell=True, stdout=FNULL,stderr=FNULL)
                running = 1
			    hasrun = 0
			    killoldplayers(players)
		else:
			videoendcheck()
			if (needtostart == 1):
				mode = 0

	    ###################################################################
        #Triggered video 2
        ###################################################################
        elif (mode == 2):
                if (needtostart == 1):
                        print("beginning trigger 18 sequence")
                        needtostart = 0
                        cmd = "omxplayer --no-keys -b --no-osd --layer %d %s "%(n,movie2)
                        Popen(cmd, shell=True, stdout=FNULL,stderr=FNULL)
                        running = 1
                        hasrun = 0
                        killoldplayers(players)
                else:
                        videoendcheck()
                        if (needtostart == 1):
                        mode = 0





#when killed, get rid of players and clean up GPIO
finally:
    GPIO.cleanup()
    os.system('killall omxplayer.bin')
