import datetime
import os
import csv

# class writing the data automatically in the datasaves directory
class data_writer():
    def __init__(self):
        # create file - default is to not send data initially
        self.saveData = False
        self.date = str(datetime.date.today())
        self.time = datetime.datetime.now().time().isoformat(timespec="minutes")
        self.file = str("Data_" + self.date + "_" + self.time + ".csv")
        self.dirPath = os.getcwd() + "/DataSaves"
        self.filePath = os.path.join(self.dirPath, self.file)
        # open file
        f = open(self.filePath, 'w')
        f.write("Time, Air Pressure, Altitide, Temperature, X Acceleration, Y Acceleration, Z Acceleration, Velocity, Humidity, Pitch, Roll, Yaw, Longitude, Lattitude, Signal Strength\n")
        f.close()

    def save(self, data):
        # uses the class variable savedata controlling if it saves or not
        if self.saveData:
            with open(self.filePath, 'a') as dataFile:
                writer = csv.writer(dataFile, delimiter=",")
                writer.writerow(data)

    def start(self):
        self.saveData = True
        print("Storing data.")
    
    def stop(self):
        self.saveData = False
        print("Stopping storing data.")
