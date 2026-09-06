import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json
from RootGUI import RootGUI

class FileGUI:
    
    def __init__(self,rootGUI):
        self.file_path = ""
        self.rootGUI = rootGUI

    def FileNew(self):
        print("New file")
        # if guiState == "Init":
        #     # open a new file 
        #     self.file_path = filedialog.asksaveasfilename(
        #     initialdir="/",
        #     title="New",
        #     filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
        #     defaultextension=".mca")

        #     if self.file_path:
        #         guiState = "Confige"
        #         self.file = open(self.file_path, "w")
   

        # elif guiState == "Confige":
        #     self.FileSave()
        #     # open a new file 
        #     self.file_path = filedialog.asksaveasfilename(
        #         initialdir="/",
        #         title="New",
        #         filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
        #         defaultextension=".mca")
            
        #     if self.file_path:
        #         guiState = "Confige"
        #         self.file = open(self.file_path, "w")
                

        # else:
        #     # inform user
        #     print("no")

    def FileSaveAs(self, guiState):

        if guiState == "Confige":
            # open a new file 
            self.file_path = filedialog.asksaveasfilename(
                initialdir="/",
                title="Save as",
                filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
                defaultextension=".mca")
            
            if self.file_path:
                file = open(self.file_path, "w")
                self.FileSave()

    def FileOpen(self, guiState):

        if guiState == "Confige" or guiState == "Init":
            file_path = filedialog.askopenfilename(
                initialdir="/",
                title="Open",
                filetypes=(("MCA files", "*.mca*"), ("all files", "*.*")),
                defaultextension=".mca")
            
            if self.file_path:
                guiState = "Confige"
                self.FileLoad()

    def FileSave():
        pass
        # global file_path
        # print(file_path)
        # data = {
        #     "coincidenceWindow": coincidenceTime_entry.get(),
        #     "time": time_entry.get(),
        #     "Ch1":[1,23,456,7777]
        # }
        # with open(file_path,"w") as f:
        #     json.dump(data, f)

    def FileLoad():
        pass
        # global file_path
        # with open(file_path,"r") as f:
        #     data = json.load(f)
        #     coincidenceTime_entry.delete(0, tk.END)
        #     coincidenceTime_entry.insert(0, data.get("coincidenceWindow", ""))
        #     time_entry.delete(0, tk.END)
        #     time_entry.insert(0, data.get("time", ""))
        #     ch1 = data.get("Ch1", "")
        #     print(ch1)


    