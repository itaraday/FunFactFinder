from Tkinter import *
import textbox as textbox

class output: 
    def __init__(self, mytab):
        self.myout = textbox.textbox(mytab, 0, 0)
        self.myout.readonly(True)
        mytab.columnconfigure(0, weight=1)
        mytab.rowconfigure(0, weight=1)
        clearbutton = Button(mytab, text="Clear", command=self.myout.clear)
        clearbutton.grid(row=2, column=0, sticky=(E,W))        
            
    def set(self, text, title=None, insert=True):
        self.myout.readonly(False)
        if title:
            self.myout.set(title, insert, "title") 
        self.myout.set("\n", insert)
        self.myout.set(text, insert)
        self.myout.set("\n", insert)
        self.myout.set("-----------------------------------------------------------------------------------------", insert)
        self.myout.set("\n", insert)
        self.myout.readonly(True)