# -*- coding: utf-8 -*-
"""
Created on Mon May 30 16:14:18 2022

@author: melab15
"""

import pyb
import hpgl
from driver import Driver

import gc, cotask, task_share
# =============================================================================
# 
# def SolenoidOn():
#     solenoidPin.value(0 if solenoidPin.value() else 1)
# 
# =============================================================================

def taskMotorFun():
    # variable = list(variable)
    x = 0 #posQueue.get()
    y = 0 #posQueue.get()
    motor1.SET_X_TARGET(x)
    motor2.SET_X_TARGET(y)
    #x = 0
    #y = 0
    while True:
        #print(motor1.READ_POS_END_INT(), motor2.READ_POS_END_INT())
        #if (motor1.READ_POS_END_INT() & motor2.READ_POS_END_INT()):
        
        #print((motor1.GET_X_ACTUAL()), x, motor1.GET_X_ACTUAL() == x)
        #print((motor2.GET_X_ACTUAL()), y, motor2.GET_X_ACTUAL() == y)
        
        
        if (abs(motor1.GET_X_ACTUAL() - x)<=1) & (abs(motor2.GET_X_ACTUAL()-y)<=1):
            motor1.READ_POS_END_INT(True)
            motor2.READ_POS_END_INT(True)
            
            if not posQueue.empty():
                x = posQueue.get()
                y = posQueue.get()
                z = posQueue.get()
            
                motor1.SET_X_TARGET(int(x))
                motor2.SET_X_TARGET(int(y))
           
                if z == 1:
                    print('Pen Up')
                    solenoidPin.high()
                elif z == 0:
                    print('Pen Down')
                    solenoidPin.low()
        yield True
                



def taskReadFun():
    zval = 0
    x_file = open("theta_positions.txt", "r")
    y_file = open("alpha_positions.txt", "r")
    
    while True:
        if not posQueue.full():
            xval = x_file.readline()
            yval = y_file.readline()
            #zstr = z_file.readline()
            
            try: zstr = pen_list.pop(0)
            except IndexError: zstr='S'
        
            print(xval, yval, zval)
            if zstr == 'U':
                zval = 1
            elif zstr == 'D':
                zval = 0
            elif zstr == 'S':
                zval = 5
                
            if xval == "":
                drawing_complete.put(True)
                x_file.close()
                y_file.close()
                yield False
            else:
                
                posQueue.put(int(float(xval)*360*16/1.8/2)) #extra div/2
                posQueue.put(int(float(yval)*360*16/1.8/2))
                posQueue.put(zval)
                yield True
        yield True





if __name__ == "__main__":
    
    
    
    # Create shares and Queues
    posQueue = task_share.Queue('i', 12, thread_protect=False, overwrite=False, name='posQueue')
    pen_command = task_share.Share('b', name='pen_command')
    drawing_complete = task_share.Share('b', name='drawing_complete')
    
    #UNCOMMENT THIS TO RECALCULATE HPGL FILE
    pen_list = hpgl.run()
    
    
    
    
    
    #need to parse above text file
    
    tim2 = pyb.Timer(4, period=3, prescaler=0)
    clk = tim2.channel(3, pin=pyb.Pin.cpu.B8, mode=pyb.Timer.PWM, pulse_width = 2)
    
    #initialize and enable first TMC2208
    EN1 = pyb.Pin(pyb.Pin.cpu.C2, mode=pyb.Pin.OUT_PP, value=1)
    
    #initialize and enable second TMC2208
    EN2 = pyb.Pin(pyb.Pin.cpu.C3, mode=pyb.Pin.OUT_PP, value=1)

    #initialize chip select pins    
    CS1 = pyb.Pin(pyb.Pin.cpu.C6, mode=pyb.Pin.OUT_PP, value=1)
    CS2 = pyb.Pin(pyb.Pin.cpu.C7, mode=pyb.Pin.OUT_PP, value=1)
    
    #initialize solenoid pin
    solenoidPin = pyb.Pin(pyb.Pin.cpu.C0, mode=pyb.Pin.OUT_PP, value=0)
    
    spi = pyb.SPI(2, mode=pyb.SPI.CONTROLLER, baudrate=115200, phase=1, polarity=1)
    
    motor1 = Driver(1, 100, 0, 0, 512, EN1, CS1, spi, clk)
    motor2 = Driver(1, 100, 0, 0, 512, EN2, CS2, spi, clk)
   
    
   #==============================================
   # Create and initialize motor objects
    motor1.ENN()
    motor1.SET_V_MIN(32)
    motor1.SET_V_MAX(500)
    motor1.SET_PULSE_RAMP_DIV()
    motor1.SET_A_MAX(512)
    motor1.SET_PMUL_PDIV()
    motor1.RAMP_MODE()
    motor1.INTERRUPT_MASK()
    motor1.ZERO()
    
    
    motor2.ENN()
    motor2.SET_V_MIN(32)
    motor2.SET_V_MAX(500)
    motor2.SET_PULSE_RAMP_DIV()
    motor2.SET_A_MAX(512)
    motor2.SET_PMUL_PDIV()
    motor2.RAMP_MODE()
    motor2.INTERRUPT_MASK()
    motor2.ZERO()

    #=============================================
    
    
    #============================================
    # Home motors
    # Set motors to velocity mode, send backwards until reference switch is pressed
    # Then return to ramp mode
#    
#    motor1.VEL_MODE()
#    motor1.SET_V_TARGET(-5)
#    #When stop interrupt is set to 1, 
#    while not motor1.READ_STOP_INT():
#        pass
#    motor1.ZERO()
#    motor1.RAMP_MODE()
#    motor1.SET_X_TARGET(0.2)
    #=============================================
    
    #Create tasks and add to task list
    taskRead    = cotask.Task(taskReadFun, name='taskRead', priority=1, period=20, 
                            profile=None, trace=False)
    taskMotor   = cotask.Task(taskMotorFun, name='taskMotor', priority=1, period=10,
                            profile=None, trace=False)
    
    cotask.task_list.append(taskRead)
    cotask.task_list.append(taskMotor)
    
    
    
    
    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect ()
    
    
    
    
    # Run the scheduler with the chosen scheduling algorithm. Quit if any 
    # character is received through the serial port
    vcp = pyb.USB_VCP ()
    #while True:
    while not drawing_complete.get():
        cotask.task_list.pri_sched()
        
    solenoidPin.low()


    # Empty the comm port buffer of the character(s) just pressed
    vcp.read ()