import tkinter as tk
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from ResizeTracker import ResizeTracker
from enum import Enum
from tkinter import filedialog
import threading
import time
import csv

from DeviceClass import DeviceClass
from DeviceGUI import DeviceGUI
from OperationModeGUI import OperationModeGUI
from GraphGUI import GraphGUI
from DataCapsule import DataCapsule
from DeviceClass import Responds
import DeviceClass


class GUIStates(Enum):
    Init        = 0
    Confige     = 1
    Acquisition	= 2


class RootGUI:
    
    def __init__(self):
        self.guiState = GUIStates.Init
        self.file_path = ""
        self.file = []
        self.AcqTime = "10"
        self.UpdateInterval = 1  # seconds

    def Build(self):
        self.Window = tk.Tk()
        self.Window.title("MCA")
        self.Window.minsize(1000, 600)
        self.Window.protocol("WM_DELETE_WINDOW", self.Window.quit)

        # ----------------------- menu bar ----------------------- #
        menu_bar = tk.Menu(self.Window)
        self.Window.config(menu=menu_bar)

        # file menu
        self.file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.New)
        self.file_menu.add_command(label="Open", command=self.Open)
        self.file_menu.add_command(label="Save", command=self.Save)
        self.file_menu.add_command(label="SaveAs", command=self.SaveAs)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="ExportSpectra", command=self.ExportSpectra)
        self.file_menu.add_command(label="ExportMatrix", command=self.ExportMatrix)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.Window.quit)

        # setting menu
        self.deviceGUI = DeviceGUI(self.Window)
        self.OPModeGUI = OperationModeGUI(self.Window)
        self.setting_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Settings", menu=self.setting_menu)
        self.setting_menu.add_command(label="Device", command=self.deviceGUI.Build)
        self.setting_menu.add_command(label="Operation Mode", command=self.OPModeGUI.Build)

        

        # ----------------------- Acquisition -------------------- #
        x_pad = 5
        y_pad = 5
        Acq_frame = tk.LabelFrame(self.Window,text="Run")
        Acq_frame.place(x=x_pad+x_pad, y=y_pad, width=150, height=150)

        self.StartStop_button = tk.Button(Acq_frame, command = self.StartStop, height = 3, width = 17, text = "Start")
        self.AcqTime_label = tk.Label(Acq_frame,text="Time(s):")
        validate_command = (self.Window.register(self.validateAcqTime), "%P")
        self.Acqtime_entry = tk.Entry(Acq_frame, validate="key", validatecommand=validate_command,textvariable=tk.StringVar(value=self.AcqTime))

        self.AcqTime_label.place(x = x_pad, y = 5, width= 40, height=30)
        self.Acqtime_entry.place(x = 55, y = 5, width= 70, height=30)
        self.StartStop_button.place(x = 7, y = 60)

        # ----------------------- report -------------------- #
        report_frame = tk.LabelFrame(self.Window,text="Report")
        report_frame.place(x=x_pad+x_pad, y=175, width=150, height=100)

        self.ElapsedTime_label = tk.Label(report_frame,text="Elapsed(s): 0" )
        self.Ch1Rate_label = tk.Label(report_frame,text="CH1 Rate(#/s): 0"  )
        self.Ch2Rate_label = tk.Label(report_frame,text="CH2 Rate(#/s): 0"  )

        self.ElapsedTime_label.place(x = x_pad, y = 10)
        self.Ch1Rate_label.place(x = x_pad, y = 30)
        self.Ch2Rate_label.place(x = x_pad, y = 50)



        # ----------------------- graph -------------------- #
        # self.Window.update()
        self.graphGUI = GraphGUI(self.Window)
        self.graphGUI.Build()

        #  ----------------------- data capsule -------------------- #
        self.dataCapsule = DataCapsule()
        self.dataCapsule.Build(1)

        self.UpdateWidgets()
        self.UpdateOutput()
    
    def New(self):     
         if self.guiState == GUIStates.Init or self.guiState == GUIStates.Confige:
            if self.guiState == GUIStates.Confige:
                self.Save()
            # open a new file 
            self.file_path = filedialog.asksaveasfilename(
            initialdir="/",
            title="New",
            filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
            defaultextension=".mca")
            if self.file_path:
                self.file = open(self.file_path, "w")
                if self.file.closed == False:
                    self.guiState = GUIStates.Confige
                    self.Window.title("MCA " + self.file_path)
                    self.ResetWidgets()
                    self.UpdateWidgets()
                    self.file.close()
                    self.dataCapsule.Build(1)
                    self.UpdateOutput()


    def SaveAs(self):
         if self.guiState == GUIStates.Confige:
            # open a new file 
            self.file_path = filedialog.asksaveasfilename(
            initialdir="/",
            title="Save as",
            filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
            defaultextension=".mca")
            if self.file_path:
                file = open(self.file_path, "w")
                if file.closed == False:
                    self.guiState = GUIStates.Confige
                    self.Window.title("MCA " + self.file_path)
                    self.Save()
                    # file.close()

    def Open(self):
        if self.guiState == GUIStates.Confige or self.guiState == GUIStates.Init:
            self.file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Open",
                filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
                defaultextension=".mca")
            if self.file_path:
                self.guiState = GUIStates.Confige
                self.Window.title("MCA " + self.file_path)
                self.ResetWidgets()
                self.UpdateWidgets()
                self.Load()
    
    def Save(self):
        print("Save")
        RootData = self.Serialize()
        data = {
            "RootData": RootData,
            "OperationMode": self.OPModeGUI.Serialize(),
            "Device": self.deviceGUI.Serialize(),
            "DataCapsule": self.dataCapsule.Serialize()
        }

        with open(self.file_path,"w") as f:
            json.dump(data, f)

    def Load(self):
        with open(self.file_path,"r") as f:
            data = json.load(f)
            RootData = data.get("RootData", "")
            OPModeData=data.get("OperationMode", "")
            DeviceData=data.get("Device", "")
            dataCapsule=data.get("DataCapsule", "")
            self.Deserialize(RootData)
            self.OPModeGUI.Deserialize(OPModeData)
            self.deviceGUI.Deserialize(DeviceData)
            self.dataCapsule.Deserialize(dataCapsule)
            self.UpdateOutput()

    def Serialize(self):
        OutData = {
            "AcqTime": self.Acqtime_entry.get()
        }
        return OutData

    def Deserialize(self,InData):
        self.Acqtime_entry.delete(0, tk.END)
        self.Acqtime_entry.insert(0, InData.get("AcqTime", ""))

    
    def ExportSpectra(self):
        file_path = filedialog.asksaveasfilename(
        title="Export spectra",
        filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")),
        defaultextension=".csv")
        data = self.dataCapsule.ExportSpectra()   
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer_ = csv.writer(file)
                writer_.writerows(data)
                

    def ExportMatrix(self): 
        file_path = filedialog.asksaveasfilename(
        title="Export Matrix",
        filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")),
        defaultextension=".csv")
        data = self.dataCapsule.ExportMatrix()   
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer_ = csv.writer(file)
                writer_.writerows(data)           
        
                    

    def ResetWidgets(self):
        pass

    def UpdateWidgets(self):
        if self.guiState == GUIStates.Init:
            self.StartStop_button.config(state="disabled")
            self.Acqtime_entry.config(state="readonly")
            self.file_menu.entryconfig("Save",state="disabled")
            self.file_menu.entryconfig("SaveAs",state="disabled")
            self.file_menu.entryconfig("ExportSpectra",state="disabled")
            self.file_menu.entryconfig("ExportMatrix",state="disabled")
            self.setting_menu.entryconfig("Device",state="disabled")
            self.setting_menu.entryconfig("Operation Mode",state="disabled")
            return
                     
        if self.guiState == GUIStates.Acquisition:
            self.StartStop_button.config(state="normal")
            self.StartStop_button.config(text="Stop")
            self.Acqtime_entry.config(state="readonly")
            self.file_menu.entryconfig("Save",state="disabled")
            self.file_menu.entryconfig("SaveAs",state="disabled")
            self.file_menu.entryconfig("Open",state="disabled")
            self.file_menu.entryconfig("New",state="disabled")
            self.file_menu.entryconfig("ExportSpectra",state="disabled")
            self.file_menu.entryconfig("ExportMatrix",state="disabled")
            self.setting_menu.entryconfig("Device",state="disabled")
            self.setting_menu.entryconfig("Operation Mode",state="disabled")
            return

        if self.guiState == GUIStates.Confige:
            self.StartStop_button.config(state="normal")
            self.StartStop_button.config(text="Start")
            self.Acqtime_entry.config(state="normal")
            self.file_menu.entryconfig("Save",state="normal")
            self.file_menu.entryconfig("SaveAs",state="normal")
            self.file_menu.entryconfig("Open",state="normal")
            self.file_menu.entryconfig("New",state="normal")
            self.file_menu.entryconfig("ExportSpectra",state="normal")
            self.file_menu.entryconfig("ExportMatrix",state="normal")
            self.setting_menu.entryconfig("Device",state="normal")
            self.setting_menu.entryconfig("Operation Mode",state="normal")
            return

    def UpdateOutput(self):
        self.graphGUI.Update(self.dataCapsule)
        self.ElapsedTime_label.config(text="Elapsed(s): " + str(self.dataCapsule.ElapsedTime))
        self.Ch1Rate_label.config(text="CH1 Rate(#/s): "  + str(self.dataCapsule.Ch1Rate))
        self.Ch2Rate_label.config(text="CH2 Rate(#/s): "  + str(self.dataCapsule.Ch2Rate))

    def StartStop(self):
        if self.guiState == GUIStates.Acquisition:
            self.StopAcquisition()
        else:
            self.StartAcquisition()

    def SetSettings(self):
        respond = self.device.SetAcqTime(int(self.AcqTime))
        if respond != Responds.OK:
            return False 
        
        respond = self.device.SetOperationMode(self.OPModeGUI.GetMode())
        if respond != Responds.OK:
            return False 
        
        respond = self.device.SetTimeWindow(self.OPModeGUI.GetTimeWindow())
        if respond != Responds.OK:
            return False 
        
        respond = self.device.SetTrigLevel(5)
        if respond != Responds.OK:
            return False
        
        print("setting successful")
        return True

    def StartAcquisition(self):
        # first check start validity
        Port = self.deviceGUI.Port
        self.device = DeviceClass.DeviceClass(Port)

        if self.device.IsZombie == True:
            print("Cannot access the device on port ", Port)
            return
        
        state = self.device.GetState()
        if state != DeviceClass.STATES.FREE:
            print("Cannot start because the device is not free")
            return
        
        flag = self.SetSettings()
        if flag == False:
            print("Cannot do settings for the device on port ", Port)
            return

        respond = self.device.Start()
        if respond != Responds.OK:
            print("Cannot start data acquisition")
            return

        self.guiState = GUIStates.Acquisition
        self.UpdateWidgets()
        timer = threading.Timer(self.UpdateInterval, self.TimerCallback)
        timer.start()

    def StopAcquisition(self):  
        state = self.device.GetState()
        if state == DeviceClass.STATES.FREE:
            print("Acquisition is already stopped")
            return
    
        respond = self.device.Stop()
        if respond == Responds.OK:
            print("Acquisition is stopped")
            return
        
        self.guiState = GUIStates.Confige
        self.UpdateWidgets()

    def TimerCallback(self):
        print("TimerCallback")
        self.guiState = GUIStates.Confige

        self.dataCapsule = self.device.GetMeasurementData()
        self.UpdateOutput()

        state = self.device.GetState()
        if state == DeviceClass.STATES.BUSY:
            self.guiState = GUIStates.Acquisition
        self.UpdateWidgets()
        if self.guiState == GUIStates.Acquisition:
            timer = threading.Timer(self.UpdateInterval, self.TimerCallback)
            timer.start()
        


    def validateAcqTime(self,new_text):
        if not new_text:
            return True
        try:
            value = int(new_text)
            if value >= DeviceClass.AcqTime_Min and value <= DeviceClass.AcqTime_Max:
                self.AcqTime = new_text
                return True
            
        except ValueError:
            return False