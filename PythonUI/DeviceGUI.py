import tkinter as tk
from tkinter import ttk
import DeviceClass


class DeviceGUI:
    
    def __init__(self,root_Window):
        self.RootWindow = root_Window
        self.Port = "COM4"

    def Build(self):
        self.Window = tk.Toplevel(self.RootWindow)
        self.Window.grab_set()
        self.Window.title("Selecting device")
        self.Window.minsize(200, 220)
        self.Window.resizable(False,False)
        self.Window.protocol("WM_DELETE_WINDOW", self.CloseCmd)

        self.label_port = tk.Label(self.Window, text="Port: ")
        self.selected_option = tk.StringVar()
        self.options = DeviceClass.DeviceClass.AvailablePorts()
        self.port_combo = ttk.Combobox(self.Window, textvariable=self.selected_option, values = self.options, state="readonly")
        self.port_combo.bind("<<ComboboxSelected>>", self.ComboCmd)

        try:
            Ind = self.options.index(self.Port)
            if Ind >= 0:
                self.port_combo.current(Ind)
        except ValueError:
            pass
        
        self.Refresh_button = tk.Button(self.Window,  command = self.RefreshCmd, height = 1,  width = 20, text = "Refresh")
        self.Close_button = tk.Button(self.Window,  command = self.CloseCmd, height = 1,  width = 9, text = "Close")
        self.Apply_button = tk.Button(self.Window, command = self.ApplyCmd,height = 1, width = 9, text = "Apply")
        self.label_message = tk.Label(self.Window, text="Select a port...")

        self.label_port.place(x=20,y=20)
        self.port_combo.place(x=20,y=50)
        self.Refresh_button.place(x=20,y=100)
        self.Apply_button.place(x=20,y=150)
        self.Close_button.place(x=100,y=150)
        self.label_message.place(x=20,y=180)

    def ComboCmd(self,args):
        option = self.port_combo.get()
        # self.Port = option
        # print(f"Selected: {option}")

    def RefreshCmd(self):
        self.options = DeviceClass.DeviceClass.AvailablePorts()
        self.port_combo.config(values=self.options)

    def CloseCmd(self):
        self.Window.grab_release()
        self.Window.destroy()

    def ApplyCmd(self):
        temp = self.port_combo.get()
        if temp == "":
            return

        obj = DeviceClass.DeviceClass(temp)

        if obj.IsZombie == False:
            self.Port = temp
            self.label_message.config(text="Connection ok")
        else:
            self.Port = ""
            self.label_message.config(text=obj.Message)

    def Serialize(self):
        OutData = {
            "Port": self.Port,
        }
        return OutData

    def Deserialize(self,InData):
        self.Port = InData.get("Port")
