  # -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 08:25:23 2022

@author: melab15
reference voltage = 0.7V
"""

# define Driver class that is used to create motor objects for each of the
# two stepper motors used for the project
class Driver:
    
    def __init__(self, V_MIN, V_MAX, pulse_div, ramp_div, A_MAX, EN, CS, SPI, CLK):
        
        #self.SCALE = (360*16/1.8)   #Converts rev to microsteps
        self.V_MIN = V_MIN
        self.V_MAX = V_MAX
        self.pulse_div = pulse_div
        self.ramp_div = ramp_div
        self.A_MAX = A_MAX
        self.X_TARGET = 0
        self.V_TARGET = 0
        self.V_ACTUAL = 0
        self.X_ACTUAL = 0
        self.p = 0
        self.PMUL = 128
        self.PDIV = 6
        
        self.EN = EN
        self.CS = CS
        self.SPI = SPI
        self.CLK = CLK
        
        #Register Addresses 
        #Stepper Motor Register Set (SMDA=00)
        self.ADDR_X_TARGET           = 0b00000000
        self.ADDR_X_ACTUAL           = 0b00000010
        self.ADDR_V_MIN              = 0b00000100
        self.ADDR_V_MAX              = 0b00000110
        self.ADDR_V_TARGET           = 0b00001000
        self.ADDR_V_ACTUAL           = 0b00001010
        self.ADDR_A_MAX              = 0b00001100
        self.ADDR_A_ACTUAL           = 0b00001110
        self.ADDR_PMUL_PDIV          = 0b00010010
        self.ADDR_REF_CONF           = 0b00010100
        self.ADDR_INTERRUPT_MASK     = 0b00010110
        self.ADDR_PULSE_RAMP_DIV     = 0b00011000
        self.ADDR_DX_REF_TOLERANCE   = 0b00011010
        self.ADDR_X_LATCHED          = 0b00011100
        self.ADDR_USTEP_COUNT        = 0b00011110
        
        #Global Parameter Registers (SMDA=11)
        self.ADDR_IF_CONFIG          = 0b01101000
        self.ADDR_POS_COMP           = 0b01101010
        self.ADDR_POS_COMP_INT       = 0b01101100
        self.ADDR_POWER_DOWN         = 0b01110000
        self.ADDR_TYPE_VERSION       = 0b01110010
        self.ADDR_R_LR               = 0b01111100
        self.ADDR_MOT1R              = 0b01111110
        
        
        # calculates a valid pair of PMUL and PDIV based through iteration
        self.p = self.A_MAX/(128*2**(self.ramp_div - self.pulse_div))
        for self.PDIV in range(0,13):
            self.PMUL = int(0.99*self.p*(2**3)*(2**self.PDIV))
            if self.PMUL >= 128 and self.PMUL <= 255:
                break

    # writes datagram to TMC4210
    def write_datagram(self, addr, value):
        datagram = bytearray(4)
        datagram[0] = addr
        datagram[1]=(value>>16)
        datagram[2]=(value>>8)&0xff
        datagram[3]=value&0xff
        self.CS.low()
        self.SPI.send(datagram)
        self.CS.high()
        return datagram
    
    # reads datagram from TMC4210
    def read_datagram(self, addr):
        datagram = bytearray(4)
        datagram[0] = (addr|1)
        datagram[1]= 0x00
        datagram[2]= 0x00
        datagram[3]= 0x00
        self.CS.low()
        self.SPI.send_recv(datagram, datagram)
        self.CS.high()
        return datagram
    
    # sets EN pin low to enable TMC2208    
    def ENN(self):
        self.EN.low()
        return self.write_datagram(self.ADDR_IF_CONFIG, 0b00100000)
    
    def INTERRUPT_MASK(self):
        return self.write_datagram(self.ADDR_INTERRUPT_MASK, 0b00001001<<8)
    
    # determines if motors have reached target position
    def READ_POS_END_INT(self, reset=False):
        databytes = self.read_datagram(self.ADDR_INTERRUPT_MASK)
        datagram = (databytes[0]<<24)|(databytes[1]<<16)|(databytes[2]<<8)|databytes[3]
        # Returns 1 if position has been reached and 0 if not
        if reset == True:
            self.write_datagram(self.ADDR_INTERRUPT_MASK, datagram|1)
        if (datagram & 1): return 1
        else: return 0
        
        
    def READ_STOP_INT(self):
        databytes = self.read_datagram(self.ADDR_INTERRUPT_MASK)
        print(databytes)
        datagram = (databytes[0]<<24)|(databytes[1]<<16)|(databytes[2]<<8)|databytes[3]
        
        # Returns 1 if position has been reached and 0 if not
        if (datagram & 1<<3):
            self.write_datagram(self.ADDR_INTERRUPT_MASK, datagram|(1<<3))
            return 1
        else: return 0
         

    # sets ramp mode
    def RAMP_MODE(self):
        return self.write_datagram(self.ADDR_REF_CONF, 0b110<<8)
        
        
    def SET_X_TARGET(self, X_TARGET):
        return self.write_datagram(self.ADDR_X_TARGET, X_TARGET)

    def GET_X_TARGET(self):
        datagram = self.read_datagram(self.ADDR_X_TARGET)
        xval = (datagram[1]<<16)|(datagram[2]<<8)|(datagram[3])
        if (xval & 1<<23):
            xval |= (0xFF<<24)
        #Returns value in revolutions
        return int(xval)
        
    def GET_X_ACTUAL(self):
        datagram = self.read_datagram(self.ADDR_X_ACTUAL)
        xval = (datagram[1]<<16)|(datagram[2]<<8)|(datagram[3])
        if (xval & 1<<23):
            xval |= (0xFF<<24)
        #Returns value in revolutions
        return int(xval)


    def ZERO(self, X_ACTUAL=0):
        #Writing a value to X_ACTUAL will set a nonzero reference position
        #Writing to X_ACTUAL register will overwrite value, used with reference switches
        return self.write_datagram(self.ADDR_X_ACTUAL, X_ACTUAL)
    
    # sets velocity mode
    def VEL_MODE(self):
        return self.write_datagram(self.ADDR_REF_CONF, 0b11000000010)
    
    
    def SET_V_TARGET(self, V_TARGET):
        # Argument in revs, converted to microsteps
        self.V_TARGET = V_TARGET
        return self.write_datagram(self.ADDR_V_TARGET, V_TARGET)
    
    
    def SET_V_MAX(self, V_MAX):
        self.V_MAX = V_MAX
        return self.write_datagram(self.ADDR_V_MAX, V_MAX)
    
    
    def SET_V_MIN(self, V_MIN):
        self.V_MIN = V_MIN
        return self.write_datagram(self.ADDR_V_MIN, V_MIN)
    
    
    def SET_A_MAX(self, A_MAX):
        self.A_MAX = A_MAX
        return self.write_datagram(self.ADDR_A_MAX, self.A_MAX)
   
    
    def SET_PMUL_PDIV(self):   
        datagram = ((self.PMUL<<8)|1<<15)|(self.PDIV)
        return self.write_datagram(self.ADDR_PMUL_PDIV, datagram)
        
    
    def SET_PULSE_RAMP_DIV(self):
        return self.write_datagram(self.ADDR_PULSE_RAMP_DIV, 0b0110011000000000)
    
    def GET_TYPE_VERSION(self):
        return self.read_datagram(self.ADDR_TYPE_VERSION)
    
    def print_datagram(self, datagram):
        for idx,byte in enumerate(datagram):
            print(f"b{3-idx}: {byte:#010b} {byte:#04x}")