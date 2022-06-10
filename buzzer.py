# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 14:18:32 2022

@author: melab15
"""
import pyb, time
buzzPin = pyb.Pin(pyb.Pin.cpu.B7, mode=pyb.Pin.AF_PP, alt=pyb.Pin.AF2_TIM4)

buzzTim = pyb.Timer(4)
buzzTim.init(freq=261.63)
buzzer = buzzTim.channel(2, pyb.Timer.PWM, pin=buzzPin, pulse_width_percent=0)

C4      = 261.63 #Middle C
CS4     = 277.18
D4      = 293
DS4     = 311.13
E4      = 329.63
F4      = 349.23
FS4     = 371
G4      = 391.99
GS4     = 415
A4      = 440
AS4     = 466.16
B4      = 493.88

C5      = 523
CS5     = 554
D5      = 587
DS5     = 622
E5      = 659
F5      = 698
FS5     = 739
G5      = 783
GS5     = 831
A5      = 879
AS5     = 933
B5      = 988

E       = 0.125
Q       = 0.25
H       = 0.5
W       = 1

# Take on me
# FS4, FS4, 

# Take On Me, by A-ha
notelist        = [FS5, FS5, D5, B4, B4, E5, E5, E5, GS5, GS5, A5, B5, A5, A5, A5, E5, D5, FS5, FS5, FS5, E5, E5, FS5, E5]
durationlist    = [Q,    Q,   Q,  H,  H,  H,  H,  Q,  Q,   Q,   Q,  Q,  Q,  Q,  Q,  H,  H,  H,   H,   Q,   Q,  Q,  Q,   Q]

def play(repeats, speedScale=1):
    for i in range(0, repeats):
        for i in range(0, len(notelist)):
            buzzer.pulse_width_percent(50)
            buzzTim.freq(notelist[i])
            time.sleep(durationlist[i]/speedScale)
            buzzer.pulse_width_percent(0)
            time.sleep(0.01)
    buzzer.pulse_width_percent(0)

