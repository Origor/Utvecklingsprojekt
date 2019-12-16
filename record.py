#!/usr/bin/python3
import os
import time
import subprocess
import signal
import gps
from urllib import request
import time

import analyze

f= open("/home/pi/Desktop/cronplsrunthis.txt","w+")

f.write("Recording has been run")

f.close() 


def internet_on():
    reference = 'http://216.58.192.142'
    try:
        request.urlopen(reference, timeout=1)
        return True
    except request.URLError:
        return False

while True:
    boolin = internet_on()
    if boolin is True:
        print("Internet connection established!")
        break
    print("waiting for internet connection")
    time.sleep(1)
    
# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        
while True:    
    while True: 
        try:
            report = session.next()
            # for a 'TPV' report and display the current time
            if report['class'] == 'TPV':
                if hasattr(report, 'time'):
                    your_counter = "{}".format(report.time)
                    noZ = your_counter.strip('Z')
                    split = noZ.partition("T")
                    for var in split:
                        index = split.index(var)
                        if (index == 0):
                            fin = "{}".format(var)
                        if (index == 2):
                            split2 = var.partition(":")
                            for var2 in split2:
                                if (split2.index(var2) == 0):
                                    localtime = "{}".format(int(var2) + 1)
                                elif (split2.index(var2) == 1):
                                    localtime = "{}".format(localtime) + "{}".format(var2)
                                else:
                                    localtime = "{}".format(localtime) + "{}".format(var2)
                    fin = "{}".format(fin) + "_{}".format(localtime)
                    your_counter = fin
                    print(your_counter)
                    break;
        except KeyError:
            pass
        except KeyboardInterrupt:
            quit()
        except StopIteration:
            session = None
            print("GPSD has terminated")

    sound_path = "/home/pi/Desktop/Sensing/s{}.wav".format(your_counter)
    video_path = "/home/pi/Desktop/Sensing/c{}.h264".format(your_counter)
    
    # The directory of the file to be saved in
    soundout = open(sound_path, 'w')

    # Record the sound in a subprocess
    sound_process = subprocess.Popen(['arecord', '--device=hw:1,0', '--format', 'S16_LE', '--rate', '44100', '-c1'], stdout=soundout, shell=False)
    
    # Records a 60 second video and saves it at provided location
    #-w 1640 -h 1232
    # 59990, 10000 
    os.system("raspivid -t 59990 --nopreview -w 640 -h 480 -o {} -fps 10".format(video_path))
    
    #time.sleep(30)
    
    # Get the process id
    sound_pid = sound_process.pid
    #cam_pid = camera_process.pid

    # Stop recording the sound & video
    os.kill(sound_pid, signal.SIGINT)
    
    """
    p1 = Process(target=analyze.video, args=(video_path))
    p2 = Process(target=analyze.sound, args=(sound_path))
    p1.start()
    p2.start()
    #p1.join()
    #p2.join()
    """
    
    analyze.video(video_path)
    middle = time.process_time()
    print("Video done: {}".format(middle - start))
    analyze.sound(sound_path)
    end = time.process_time()
    print("Time done sound: {}".format(end - middle))
    print("Overall proccessing of 10 seconds: {}".format(end - start))
    
    #time.sleep(5)