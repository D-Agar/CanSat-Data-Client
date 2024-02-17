import math
import serial
import ambiance
import pvlib
from serial.serialutil import SerialException
import serial.tools.list_ports
import random
import time

# class for controlling data coming through the port
class port_Control:
    def __init__(self):
        # collect all ports
        self.ports = sorted(serial.tools.list_ports.comports())
        self.portName = ""
        self.ser = serial.Serial()
        self.baudrate = 115200
        self.simulation = False
        self.initialS = 0
        self.initialT = 0
        # implement a stopwatch
        self.startTime = time.time()

        print("Available ports (press enter for simulation):")
        for i in range(0, len(self.ports)):
            print("{0}) {1}".format(i+1, self.ports[i]))
        # try open the serial port
        try:
            self.portName = "/dev/" + str(self.ports[int(input("Select port number: ")) - 1].name)
            self.ser = serial.Serial(self.portName, self.baudrate)
        except Exception:            
            print("Error trying to open port, running simulation...")
            self.simulation = True
        
    # read data coming from the port
    def read(self):
        timeFlag = time.time()
        elapsed = round(timeFlag - self.startTime, 2)
        if self.simulation == True:
            """
                ORDER OF VALUES
            """
            # Time, Air Pressure, Altitude, Temperature, X Acceleration, Y Acceleration, Z Acceleration, Velocity, Humidity, Pitch, Roll, Yaw, Longitude, Lattitude, Signal strength
            data = [elapsed, random.randint(0, 300), random.randint(5, 30), random.randint(0, 30), random.randint(3, 10),  random.randint(3, 10),  random.randint(3, 10), round(3 * random.random(), 2), random.randint(40, 60), random.randint(0, 90), random.randint(0, 90), random.randint(0, 90), (random.randint(53777000, 53778000)/1000000), -(random.randint(1049500, 1050000)/1000000), ["Poor", "Ok", "Good"][random.randint(0, 2)]]
        else:
            # Temperature, Pitch, Roll, Yaw, X Acc, Y Acc, Z Acc, Air Pressure
            incoming = self.ser.readline().decode("utf-8").split()
            # altidude
            altidude = pvlib.atmosphere.pres2alt(float(incoming[18]))
            # velocity
            velocity = float(((altidude - self.initialS) + (0.5 * float(incoming[11]) * ((elapsed - self.initialT) ** 2))) / (elapsed - self.initialT))
            # data order again - time, air pressure, altidude, Temperature,     x acceleration,     y acceleration,         z acceleration,     velocity, humidity, pitch,      roll,           yaw,        Longitude,                  Lattitude
            data = [elapsed, float(incoming[18]), altidude, float(incoming[1]), float(incoming[8]), float(incoming[11]), float(incoming[14]), velocity, float(incoming[21]), float(incoming[3]), float(incoming[5]), 0, float((random.randint(53927000, 53927100)/1000000)), float(-(random.randint(974220, 974250)/1000000)), "Not Yet"]
            self.initialS = altidude
            self.initialT = elapsed
        return data

    # Getters
    def isOpen(self):
        return self.ser.isOpen()
    
    def isSimulated(self):
        return self.simulation

    # restart the timer
    def restartTime(self):
        self.startTime = time.time()

    # Setters
    def setInitalS(self, s):
        self.initialS = s
    
    def setInitialT(self, t):
        self.initialT = t
