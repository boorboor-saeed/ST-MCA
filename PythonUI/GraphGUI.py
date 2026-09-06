import tkinter as tk
from tkinter import ttk
import DeviceClass
from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
from DataCapsule import DataCapsule


class Channels(Enum):
    CH1 = 1
    CH2 = 2
    BOTH= 3
    Ch1VsCh2 = 4

class GraphGUI:
    
    def __init__(self,root_Window):
        self.RootWindow = root_Window
        self.Channel = Channels.BOTH.value
        self.canvas_x0 = 200
        self.canvas_y0 = 50
        self.canvas_w = 500
        self.canvas_h = 500
        self.canvas_pad = 25
        self.DataCapsule = DataCapsule()
        self.DataCapsule.Build(1)
        self.ColorBar = 0

    def Build(self):
        self.RootWidth = self.RootWindow.winfo_width()
        self.RootHeight = self.RootWindow.winfo_height()
        self.canvas_w = self.RootWidth - self.canvas_x0 - 2 * self.canvas_pad
        self.canvas_h = self.RootHeight - self.canvas_y0 - 2 * self.canvas_pad
        self.fig, self.ax = plt.subplots()

        # Embed Matplotlib figure in Tkinter canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.RootWindow)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.place(x = self.canvas_x0, y = self.canvas_y0, width = self.canvas_w, height = self.canvas_h)
        self.canvas.draw()
        ToolBarFrame = tk.Frame(self.RootWindow)
        self.toolbar = NavigationToolbar2Tk(self.canvas, ToolBarFrame)
        self.toolbar.update()
        ToolBarFrame.place(x = self.canvas_x0, y=0 )
        self.RootWindow.bind("<Configure>", self.resize)

        # a combo to choose channel graph        
        self.channel_label = tk.Label(self.RootWindow,text="Channel: ")
        self.selected_channel = tk.StringVar()
        self.channels = [Channels.CH1.name, Channels.CH2.name, Channels.BOTH.name, Channels.Ch1VsCh2.name]
        self.channel_combo = ttk.Combobox(self.RootWindow, textvariable = self.selected_channel, values = self.channels, state="readonly")
        self.channel_combo.set(Channels.BOTH.name)
        self.channel_combo.bind("<<ComboboxSelected>>", self.select)
        self.channel_label.place(x = 590, y=15 )
        self.channel_combo.place(x = 650, y=15 , width=100)
       

    def Update(self, DataCapsule):
        self.ax.clear()
        self.DataCapsule = DataCapsule
        if self.Channel == Channels.Ch1VsCh2.name:
            self.PlotMatrix(DataCapsule)
        else:
            self.PlotSpectrum(DataCapsule)
            

    def PlotSpectrum(self, DataCapsule):
        ADCEndRange = 3700
        BufferLen = len(DataCapsule.Ch1Count)
        y1 = DataCapsule.Ch1Count
        y2 = DataCapsule.Ch2Count

        for i in range(ADCEndRange, BufferLen):
            y1[i] = 0
            y2[i] = 0

        plt.clf()
        self.ch1Line, = plt.plot(y1, label='Channel 1')
        self.ch2Line, = plt.plot(y2, label='Channel 2')

        plt.xlabel('bin')
        plt.ylabel('count/bin')
        plt.title('Spectrum')
        
        plt.legend()
        self.canvas.draw()
        self.canvas.flush_events()

        if self.Channel == Channels.CH1.name:
            self.ch1Line.set_visible(True)
            self.ch2Line.set_visible(False)
            leg = plt.legend()
            leg.set_visible(False)
        elif self.Channel == Channels.CH2.name:
            self.ch1Line.set_visible(False)
            self.ch2Line.set_visible(True)
            leg = plt.legend()
            leg.set_visible(False)
        elif self.Channel == Channels.BOTH.name:
            self.ch1Line.set_visible(True)
            self.ch2Line.set_visible(True)
            leg = plt.legend()
            leg.set_visible(True)


        self.ax.set_aspect('auto') 
        self.canvas.draw()
        self.canvas.flush_events()


    def PlotMatrix(self, DataCapsule):
        if not DataCapsule.Matrix:
            return
        
        plt.clf()

        NP_Matrix = np.array(DataCapsule.Matrix)
        im = plt.imshow(NP_Matrix, cmap='viridis', origin='lower') 
        plt.xlabel('Ch1')
        plt.ylabel('Ch2')
        plt.title('Matrix')
        self.ColorBar = self.fig.colorbar(im)

        self.canvas.draw()
        self.canvas.flush_events()

    def select(self,option):
        self.Channel = self.channel_combo.get()
        print(self.Channel)
        self.Update(self.DataCapsule)

    def resize(self, event):
        if(event.widget == self.RootWindow and
            (self.RootWidth != event.width or self.RootHeight != event.height)):
            self.RootWidth, self.RootHeight = event.width, event.height
            new_width = event.width
            new_height = event.height
            
            self.canvas_w = new_width - self.canvas_x0 - 2 * self.canvas_pad
            self.canvas_h = new_height - self.canvas_y0 - 2 * self.canvas_pad
            self.canvas_widget.place(x = self.canvas_x0, y = self.canvas_y0, width = self.canvas_w, height = self.canvas_h)

            
