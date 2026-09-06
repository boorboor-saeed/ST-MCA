import tkinter as tk
from tkinter import ttk
import DeviceClass
from enum import Enum
from DeviceClass import OperationModes


class OperationModeGUI:
    
    def __init__(self, root_Window):
        self.RootWindow = root_Window
        self.__Mode = OperationModes.Independent.value
        self.__TimeWindow = "1"

    def GetMode(self):
        mode = OperationModes(self.__Mode)
        return mode
    
    def GetTimeWindow(self):
        timeWindow = int(self.__TimeWindow)
        return timeWindow

    def Build(self):

        self.Window = tk.Toplevel(self.RootWindow)
        self.Window.grab_set()
        self.Window.title("Operation mode")
        self.Window.minsize(200, 220)
        self.Window.resizable(False,False)
        self.Window.protocol("WM_DELETE_WINDOW", self.CloseCmd)
       
        self.selected_option = tk.IntVar(value=self.__Mode)
        self.mode_rb1 = tk.Radiobutton(self.Window, text="Independent", variable=self.selected_option, value = OperationModes.Independent.value, command=self.select)
        self.mode_rb2 = tk.Radiobutton(self.Window, text="Coincidence", variable=self.selected_option, value=OperationModes.Coincidence.value, command=self.select)
        self.mode_rb3 = tk.Radiobutton(self.Window, text="Anticoincidence", variable=self.selected_option, value=OperationModes.Anticoincidence.value, command=self.select)
        self.mode_rb4 = tk.Radiobutton(self.Window, text="Ch1 Vs. Ch2", variable=self.selected_option, value=OperationModes.CH1VSCH2.value, command=self.select)
        

        validate_command = (self.Window.register(self.validate), "%P")
        text_var = tk.StringVar(value=self.__TimeWindow)
        self.TimeWindow_label = tk.Label(self.Window,text="window (\u03bcs):")
        self.TimeWindow_entry = tk.Entry(self.Window, validate="key", validatecommand = validate_command, width=10, textvariable = text_var)
        x_pad = 25
        y_pad = 25
        xp = x_pad
        yp = y_pad

        self.mode_rb1.place(x = xp, y = yp)
        yp = yp + y_pad
        self.mode_rb2.place(x = xp, y = yp)
        yp = yp + y_pad
        self.mode_rb3.place(x = xp, y = yp)
        yp = yp + y_pad
        self.mode_rb4.place(x = xp, y = yp)
        yp = yp + y_pad
        self.TimeWindow_label.place(x = xp, y = yp)
        yp = yp + y_pad
        self.TimeWindow_entry.place(x = xp, y = yp)
        self.select()

    def select(self):
        if self.selected_option.get() == OperationModes.Independent.value:
            self.TimeWindow_entry.place_forget()
            self.TimeWindow_label.place_forget()
        else:
            self.TimeWindow_label.place(x=25,y=125)
            self.TimeWindow_entry.place(x=25,y=150)
             
    def CloseCmd(self):
        self.__Mode = self.selected_option.get() 
        if self.TimeWindow_entry.get():     
            self.__TimeWindow = self.TimeWindow_entry.get()
        self.Window.grab_release()
        self.Window.destroy()

    def validate(self, new_text):
        if not new_text:
            return True
        try:
            value = int(new_text)
            return value >= DeviceClass.TimeWindow_Min and value <= DeviceClass.TimeWindow_Max
    
        except ValueError:
            return False
        
    def Serialize(self):
        OutData = {
            "Mode": self.__Mode,
            "TimeWindow": self.__TimeWindow
        }
        return OutData

    def Deserialize(self,InData):
        self.__Mode = InData.get("Mode")        
        self.__TimeWindow = InData.get("TimeWindow")

