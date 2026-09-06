import numpy as np
import DeviceClass


class DataCapsule:

    def __init__(self):
        self.Ch1Count = []
        self.Ch2Count = []
        self.Matrix = []
        self.Ch1Rate = 0
        self.Ch2Rate = 0
        self.ElapsedTime = 0

    def Build(self, DeviceArray):
        
        self.Ch1Count = []
        self.Ch2Count = []
        for i in range(0,4095):
            # self.Ch1Count.append(i)
            # self.Ch2Count.append(4095 - i)
            self.Ch1Count.append(0)
            self.Ch2Count.append(0)

        for i in range(0,127):
            Row = []
            for j in range(0,127): 
                Row.append(i+j)
            self.Matrix.append(Row)


        self.Ch1Rate = 0
        self.Ch2Rate = 0
        self.ElapsedTime = 0

    def Serialize(self):
        OutData = {
            "Ch1Count": self.Ch1Count,
            "Ch2Count": self.Ch2Count,
            "Matrix": self.Matrix,
            "Ch1Rate": self.Ch1Rate,
            "Ch2Rate": self.Ch2Rate,
            "ElapsedTime": self.ElapsedTime,
        }
        print(OutData)
        return OutData

    def Deserialize(self,InData):
        self.Ch1Count = InData.get("Ch1Count")
        self.Ch2Count = InData.get("Ch2Count")
        self.Matrix = InData.get("Matrix")
        self.Ch1Rate = InData.get("Ch1Rate")
        self.Ch2Rate = InData.get("Ch2Rate")
        self.ElapsedTime = InData.get("ElapsedTime")

    def ExportSpectra(self):
        title = ['bin', 'Ch1', 'Ch2']
        data = []
        data.append(title)
        for i in range(0,len(self.Ch1Count)):
            row = [i , self.Ch1Count[i], self.Ch2Count[i]] 
            data.append(row)
        return data
    
    def ExportMatrix(self):
        return self.Matrix
