#!/bin/sh

#wait 10 seconds for console messages to stop popping up
sleep 10
#disable console blinking cursor
setterm -cursor off > /dev/tty1
#wipe out the screen (cleared, black), redirect output to null
dd if=/dev/zero of=/dev/fb0 > /dev/null 2>&1
#start main python script in background and redirect output to null
python3 /home/pi/TriggeredVideoPlayer_NetworkUDPTrigger_v5.py > /dev/null 2>&1 &
