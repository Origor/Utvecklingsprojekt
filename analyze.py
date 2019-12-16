import glob
import os
import cv2
import time

import json

import soundfile as sof
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt
import numpy as np

from datetime import datetime
    
def sound(sound_path):
    # done with sosfiltfilt
    def beepFilter(block):
        lower = (3990 / (44100 / 2))
        higher = (4010 / (44100 / 2))
        n = 6  # order
        sos = butter(n, [lower, higher], 'bandpass', analog=False, output='sos')
        filteredSos = sosfiltfilt(sos, block)
        return filteredSos

    def knappFilter(block):
        lower = (4790 / (44100 / 2))
        higher = (4810 / (44100 / 2))
        n = 6  # order
        sos = butter(n, [lower, higher], 'bandpass', analog=False, output='sos')
        filteredSos = sosfiltfilt(sos, block)
        return filteredSos

    #print("Sound path:" + sound_path)
    [originalSignal, sampleRate] = sof.read("{}".format(sound_path))

    knappfiltt = knappFilter(originalSignal)
    beepfiltt = beepFilter(originalSignal)

    amplitudArr = []
    bandArr = []
    
    # Counters for beeps, button and amount of blocks
    counter_beep = 0
    counter_knapp = 0
    counter_blocks = 0
    
    # Sensitivity
    filtConst = 0.023  # Lower if to many values i beep counter and knapp counter
    sens_green_red = 7  # Adjust
    
    # status = 0 red light, status = 1 green light
    status = "Green"
    status_mem = "Green"
    
    # JSON-File will be updated if a change of light status is detected
    data = {}
    data['recorded'] = {'microphone': '{}'.format(sound_path)}
    data['zones'] = []
    data['events'] = []
    
    # decides the amount of time you wish to record. 200 with input block time of 0.1
    # would result in 20s of realtime recording.
    # record_time = 200
    for i in range(int(round(len(originalSignal) / 4410))):
        knappfilt = knappfiltt[4410 * i:4410 + 4410 * i]
        filteredSos = beepfiltt[4410 * i:4410 + 4410 * i]

        counter_blocks = counter_blocks + 1

        # To find the desired sounds after filtering depending on amplitude.
        if np.sum(filteredSos > filtConst):
            counter_beep = counter_beep + 1
            if counter_blocks < sens_green_red:
                status = "Green"
            else:
                status = "Red"
            counter_blocks = 0
            prevstate=status

        if np.sum(knappfilt > filtConst):
            counter_knapp = counter_knapp + 1
            
            data['zones'].append({
                'time': '{}'.format(str(i))
            })
            data['events'].append({
                'event': 'Button_pressed'
            })

        # Print to file status_light only when the light changes.
        # Timestamp eller uppdatera hela tiden? Synca med GPS?
        # Med timestamp direkt, så kan man få tiden den varit röd eller grön och
        # när det sker
        # Men att updatera med nytt värde hela tiden till filen så måste
        # man i efterhand bestämma när det blev rött. Pga man vet att det är
        # ett block per 0.1s just nu. Och man vet när man börjar logga data.
        if status != status_mem:            
            if status is "Red":
                event = "Red"
            else:
                event = "Green"
                
            data['zones'].append({
                'time': '{}'.format(str(i))
            })
            data['events'].append({
                'event': '{}'.format(event)
            })
            
            status_mem = status

        amplitudArr.append(knappfilt)
        bandArr.append(filteredSos)
        
    dejt = sound_path.partition('2')
    well = "s2"+dejt[2]
    obv = well.partition('.')
    well = obv[0]
    plswurk = '/home/pi/Desktop/Outdata/' + "{}".format(well)
    plswurk = plswurk + ".json"
    new = ""
    temp=0
    while temp < len(plswurk):
        if(temp is 39 or temp is 42):
            new = new +"-"
        else:
            new = new + plswurk[temp]    
        temp = temp+1

    
    with open(new, 'w') as outfile:
        json.dump(data, outfile)
    os.system("bash /home/pi/Desktop/upload_data.sh")
   
def video(video_path):
    capture = cv2.VideoCapture(video_path)
    
    frame = 0
    
    if (capture.isOpened() == False): 
      print("Error opening file")
      
    faceFront_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faceSide_cascade = cv2.CascadeClassifier("haarcascade_profileface.xml")

    # JSON-File will be updated if a change of light status is detected
    data = {}
    data['recorded'] = {'camera': '{}'.format(video_path)}
    data['freq'] = {'Hz': '{}'.format(10)}
    data['frames'] = []
    #data['positionsX'] = []
    #data['positionsY'] = []
    data['X'] = []
    data['Y'] = []
    #data['XW'] = []
    #data['YH'] = []
    data['W'] = []
    data['H'] = []
    data['colours'] = []
    
    while(capture.isOpened()):
        frame = frame + 1
        ret, vid = capture.read()
        
        if (ret):
            gray = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)

        facesFront = faceFront_cascade.detectMultiScale(gray, 1.05, 5)
        facesSide = faceSide_cascade.detectMultiScale(gray, 1.05, 5)

        """
        colour = []
        #positionsX = []
        #positionsY = []
        X = []
        Y = []
        #XW = []
        #YH = []
        W = []
        H = []
        """
        for (x, y, w, h) in facesFront:   
            data['frames'].append({
                'frame': '{}'.format(frame)
            })
            data['X'].append({
                'X': '{}'.format(x)
            })
            data['Y'].append({
                'Y': '{}'.format(y)
            })
            data['W'].append({
                'W': '{}'.format(w)
            })
            data['H'].append({
                'H': '{}'.format(h)
            })
            data['colours'].append({
                'colour': 'Green'
            })
            """
            X.append(x)
            Y.append(y)
            #XW.append(x+w)
            #YH.append(y+h)
            W.append(w)
            H.append(h)
            #positionsX.append((x+w)/2)
            #positionsY.append((y+h)/2)
            colour.append("Greeen")
            """

        for (x, y, w, h) in facesSide:
            data['frames'].append({
                'frame': '{}'.format(frame)
            })
            data['X'].append({
                'X': '{}'.format(x)
            })
            data['Y'].append({
                'Y': '{}'.format(y)
            })
            data['W'].append({
                'W': '{}'.format(w)
            })
            data['H'].append({
                'H': '{}'.format(h)
            })
            data['colours'].append({
                'colour': 'Red'
            })
            """
            X.append(x)
            Y.append(y)
            #XW.append(x+w)
            #YH.append(y+h)
            W.append(w)
            H.append(h)
            #positionsX.append((x+w)/2)
            #positionsY.append((y+h)/2)
            colour.append("Red")
            """

        #green square for face front
        for(x, y, w, h) in facesFront:
          cv2.rectangle(vid, (x, y), (x+w, y+h), (0, 255, 0), 2)

        #red square for face in profile
        for(x, y, w, h) in facesSide:
          cv2.rectangle(vid, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        if ret == False:
            break

    capture.release()
    dejt = video_path.partition('c')
    well = dejt[2]
    obv = well.partition('.')
    well = obv[0]
    plswurk = '/home/pi/Desktop/Outdata/' + "c{}".format(well)
    plswurk = plswurk + ".json"
    new = ""
    temp=0
    while temp < len(plswurk):
        if(temp is 39 or temp is 42):
            new = new +"-"
        else:
            new = new + plswurk[temp]    
        temp = temp+1

    with open(new, 'w') as outfile:
        json.dump(data, outfile)
        #os.system("bash /home/pi/Desktop/upload_data.sh")
    print("nununununnunun")
    #time.sleep(10)