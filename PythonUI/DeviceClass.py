import struct
import serial.tools.list_ports
import serial
import array
from enum import Enum
from DataCapsule import DataCapsule
import numpy as np

class CMD(Enum):
    DO_NOTHING      = 0
    START           = 1
    STOP			= 2
    #  settings
    SET_TRIGLEVEL	= 11
    SET_WINDOW		= 12
    SET_ACQTIME		= 13
    SET_MODE		= 14
    #  get buffer
    GET_Spectrum	= 21
    GET_Matrix		= 22
    GET_Status		= 23
    GET_Report		= 24
    GET_ADCBuffer	= 25
    GET_NoPulses	= 26
    GET_PulseEdges	= 27
    GET_MatrixRow	= 28
	#  get device name
    GET_DEVICE	    = 100 

class STATES(Enum):
    FREE      = 0
    BUSY      = 1
    INIT      = 2

class OperationModes(Enum):
    Independent     = 1
    Coincidence     = 2
    Anticoincidence	= 3
    CH1VSCH2	    = 4

class Responds(Enum):
    OK              = 0
    ERROR           = 1
    UNKNOWN_CODE	= 2
    UNKNOWN_SETTING	= 3 
    BAD_ARGUMENTS   = 4


ADCBufferHalfLength = 4096*2
NAME_LENGTH = 16
SPECTRUM_LENGTH = 4096
MATRIX_ROWS = 127
MATRIX_COLUMNS = 127
MATRIX_LENGTH = MATRIX_ROWS * MATRIX_COLUMNS
REPORT_LENGTH = 3

AcqTime_Min = 1 # seconds
AcqTime_Max = 1e6 # seconds
TimeWindow_Min = 1 # micro-seconds
TimeWindow_Max = 50 # micro-seconds
TrigLevel_Min  = 1  # adc channel
TrigLevel_Max  = 4094 # adc 


DeviceName = "STM32H7_MCA"

class DeviceClass:
    
    def __init__(self, Port):
        self.Name = DeviceName
        self.Port = Port
        self.IsZombie = True
        self.Message = ""
        DeviceClass.checkPort(self)

        print("--------------- check name ---------------")
        DeviceClass.checkName(self)

        # flag = DeviceClass.checkPort(self)
        # if flag == False:
        #     self.Message = "Port is not available"
        #     # return
            
        # flag = DeviceClass.checkName(self)
        # if flag == False:
        #     self.Message = "It is not MCA"
        #     # return
        
        # flag = DeviceClass.checkState(self)
        # if flag == False:
        #     self.Message = "Device is not free"
        #     # return
        
        self.IsZombie = False

    def checkPort(self):
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            if port == self.Port:
                print(f"{port}: {desc} **** [{hwid}]")
                return True
        raise ValueError("Cannot find port (" + self.Port + ") on this PC")
        return False

    def checkName(self):
        SendData = []
        val = CMD.GET_DEVICE.value
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        RecLen = NAME_LENGTH
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        print("---------- return from communicate --------")

        Name = ReceivedData.decode()
        Name = Name.rstrip('\x00')
        if Name == self.Name:
            print("The device (" + self.Name + ") is found on port " + self.Port)
            return True
        else:
            print("The device (" + Name + ") is found on port " + self.Port)
            raise ValueError("Cannot find (" + self.Name + ") on port " + self.Port)
            return False
        
    def Start(self):
        val = CMD.START.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        respond = Responds(ReceivedData[0])
        return respond
    
    def Stop(self):
        val = CMD.STOP.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        respond = Responds(ReceivedData[0])
        return respond


    def SetAcqTime(self,AcqTime):
        if AcqTime > AcqTime_Max or AcqTime < AcqTime_Min:
            return False
        val = CMD.SET_ACQTIME.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(int(AcqTime))
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        respond = Responds(ReceivedData[0])
        return respond 

    def SetTimeWindow(self,TimeWindow):
        if TimeWindow > TimeWindow_Max or TimeWindow < TimeWindow_Min:
            return False
        val = CMD.SET_WINDOW.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(int(TimeWindow))
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        respond = Responds(ReceivedData[0])
        return respond

    def SetTrigLevel(self,TrigLevel):
        if TrigLevel > TrigLevel_Max or TrigLevel < TrigLevel_Min:
            return False
        val = CMD.SET_TRIGLEVEL.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(int(TrigLevel))
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        respond = Responds(ReceivedData[0])
        return respond

    def SetOperationMode(self,Mode):
        val = CMD.SET_MODE.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(int(Mode.value))
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        print(ReceivedData)
        respond = Responds(ReceivedData[0])
        return respond


    def GetMeasurementData(self):
        data = DataCapsule()
        data.Ch1Count = self.GetSpectrum(1)
        data.Ch2Count = self.GetSpectrum(2)
        data.Matrix = self.GetMatrix()
        report = self.GetReport()
        data.ElapsedTime = report[0]
        data.Ch1Rate = report[1]
        data.Ch2Rate = report[2]
        return data

    def GetSpectrum(self,channel):
        val = CMD.GET_Spectrum.value
        RecLen = SPECTRUM_LENGTH * 4
        SendData = []
        cmd = IntToBytes(int(val))
        arg = IntToBytes(channel)
        SendData.extend(cmd)
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        spectrum = ConvertBytes(ReceivedData, 'UInt32')
        return spectrum
    
    def GetMatrix(self):
        # Matrix = []
        # for RowIndex in range(MATRIX_ROWS):
        #     RowData = self.GetMatrixRow(RowIndex)
        #     Matrix.append(RowData)
        # return Matrix
        val = CMD.GET_Matrix.value
        RecLen = MATRIX_ROWS * MATRIX_COLUMNS * 4
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        OneD = ConvertBytes(ReceivedData, 'UInt32')
        # print("OneD length: ", len(OneD))
        TwoD = reshape_1D_To_2D(OneD, MATRIX_ROWS, MATRIX_COLUMNS)
        return TwoD
    
    def GetMatrixRow(self, RowIndex):
        val = CMD.GET_MatrixRow.value
        RecLen = MATRIX_COLUMNS * 4
        SendData = []
        cmd = IntToBytes(int(val))
        arg = IntToBytes(RowIndex)
        SendData.extend(cmd)
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        RowData = ConvertBytes(ReceivedData, 'UInt32')
        return RowData


    def GetADCBuffer(self,channel):
        val = CMD.GET_ADCBuffer.value
        RecLen = ADCBufferHalfLength * 4
        SendData = []
        cmd = IntToBytes(int(val))
        arg = IntToBytes(channel)
        SendData.extend(cmd)
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        buffer = ConvertBytes(ReceivedData, 'UInt32')
        return buffer
    
    def GetReport(self):
        val = CMD.GET_Report.value
        RecLen = REPORT_LENGTH * 4
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        report = ConvertBytes(ReceivedData, 'UInt32')
        return report

    def GetState(self):
        val = CMD.GET_Status.value
        RecLen = 1
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        State = STATES(ReceivedData[0])
        return State
    
    def GetNoPulses(self,channel):
        val = CMD.GET_NoPulses.value
        RecLen = 4
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(channel)
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        NoPulses = ConvertBytes(ReceivedData, 'UInt32')
        return NoPulses[0]
    
    def GetPulseEdges(self,channel,NoPulses):
        val = CMD.GET_PulseEdges.value
        RecLen = 4 * NoPulses
        SendData = []
        cmd = IntToBytes(int(val))
        SendData.extend(cmd)
        arg = IntToBytes(channel)
        SendData.extend(arg)
        ReceivedData = DeviceClass.Communicate(self, SendData, RecLen)
        Edges = ConvertBytes(ReceivedData, 'UInt32')
        return Edges
    
    def Communicate(self, SendData, RecLen):
        ReceivedData = []
        ser = serial.Serial(self.Port, 9600, timeout=1)
        if ser.is_open == False:
            ser.close()
            return ReceivedData
        ser.write(SendData)
        ReceivedData = ser.read(RecLen) 
        if len(ReceivedData) != RecLen :
            ReceivedData = []
        ser.close()
        return ReceivedData

    def AvailablePorts():
        list_port = []
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            list_port.append(port)
        return list_port
        
def FloatToBytes(f):
    return struct.pack('<f', f)

def IntToBytes(i):
    return i.to_bytes(4, byteorder='little')

def ConvertBytes(byte_array, OutType, endian='little'):

    Out_list = []

    if OutType == 'float':

        if len(byte_array) % 4 != 0:
            raise ValueError("Byte array length must be a multiple of 4")

        endian_char = '<' if endian == 'little' else '>'

        for i in range(0, len(byte_array), 4):
            word_bytes = byte_array[i:i+4]
            word = struct.unpack(f'{endian_char}f', word_bytes)[0]
            Out_list.append(word)

    elif OutType == 'UInt32':
        if len(byte_array) % 4 != 0:
            raise ValueError("Byte array length must be a multiple of 4")

        for i in range(0, len(byte_array), 4):
            word_bytes = byte_array[i:i+4]
            word = int.from_bytes(word_bytes, byteorder='little')
            Out_list.append(word)

    elif OutType == 'SInt32':
        if len(byte_array) % 4 != 0:
            raise ValueError("Byte array length must be a multiple of 4")

        for i in range(0, len(byte_array), 4):
            word_bytes = byte_array[i:i+4]
            word = int.from_bytes(word_bytes, byteorder='little', signed=True)
            Out_list.append(word)

    else:
        raise ValueError("Unknown output type, choose from (float, UInt32, SInt32)")
    
    return Out_list

def reshape_1D_To_2D(one_d_list, rows, cols):
    if len(one_d_list) != rows * cols:
        raise ValueError("The total number of elements must match rows * cols.")
    
    two_d_list = [one_d_list[i * cols:(i + 1) * cols] for i in range(rows)]
    return two_d_list