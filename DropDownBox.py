from Tkinter import *
import ttk as ttk
    
class DropDownBox:
    def __init__(self, master, myoptions, col, row):
        self.optionselection = StringVar()
        self.optionsbox = ttk.Combobox(master, textvariable=self.optionselection)
        self.optionsbox["state"] = "readonly"
        if len(myoptions) >0:
            self.optionsbox['values'] = myoptions
            self.optionsbox.set(myoptions[0])
        self.optionsbox.grid(column=col, row=row, sticky=(W))
        
    def getSelecton(self):
        return str(self.optionselection.get())
    
    def updateSelection(self, myoptions):
        self.optionsbox['values'] = myoptions
        self.optionsbox.set(myoptions[0])
    
    def updateDD(self, action, option):
        if action == "add":
            if self.optionsbox['values'] == "":
                foo = []
            else:
                foo = list(self.optionsbox['values'])
            foo.append(option)
            self.optionsbox['values'] = tuple(foo)
        else:
            foo = list(self.optionsbox['values'])
            foo.remove(option)
            self.optionsbox['values'] = tuple(foo)