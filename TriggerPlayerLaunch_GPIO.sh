#!/bin/sh

#This script is to be put into /home/pi/
#This will wait 10 seconds for system startup to be completed,
#set permissions of the termainal to allow manipulation, 
#clear the console, disable the blinking cursor, then launch
#the triggered video player as a forked background process with no
#console output to keep the screen clear

#wait 10 seconds for console messages to stop popping up
sleep 10
#ensure permissions allow changing of tty1 console properties
chmod 666 /dev/tty1
#disable console blinking cursor
setterm -cursor off > /dev/tty1
#wipe out the screen (cleared, black), redirect output to null
dd if=/dev/zero of=/dev/fb0 > /dev/null 2>&1
#start main python script in background and redirect output to null
python3 /home/pi/TriggeredVideoPlayer_GPIO_v9.py > /dev/null 2>&1 &
