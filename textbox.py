import Tkinter as tk
from Tkinter import N,E,S,W
#import tkFont

class textbox:

    def __init__(self, master, col, row, height=-1, width=-1):
        self.yscrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.xscrollbar = tk.Scrollbar(master, orient=tk.HORIZONTAL)

        if height != 1:
            self.xscrollbar.grid(row=row+1, column=col, sticky=(E,W))    
            self.yscrollbar.grid(row=row, column=col+1, sticky=(N,S))
                    
        if height == -1 and width == -1:        
            self.textbox = tk.Text(master, background="black", foreground="green", wrap=tk.NONE, yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set)
        else:
            self.textbox = tk.Text(master, background="black", foreground="green", wrap=tk.NONE, yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set, width=width, height=height)
        #self.textbox.grid(column=col, row=row, sticky=(N,E,S,W))
        self.yscrollbar.config(command=self.textbox.yview)
        self.xscrollbar.config(command=self.textbox.xview)
        self.textbox.grid(row=row, column=col, sticky=(N,E,S,W))
        self.textbox.bind("<1>", self.set_focus)
        self.textbox.tag_configure('title', font=('Times New Roman', 20, 'bold', 'underline'))
        self.isreadonly = False
        
    def clear(self):
        self.readonly(False)
        self.textbox.delete(1.0, tk.END)
        if self.isreadonly:
            self.readonly(True)
        
    def get(self):
        return self.textbox.get(1.0, tk.END)
    
    def set(self, text, insert = True, title=None):
        if not insert:
            self.clear()
        if title:
            self.textbox.insert(tk.END, text,'title') 
        else:
            self.textbox.insert(tk.END, text)
    
    def readonly(self, isreadonly):
        self.isreadonly = isreadonly
        if isreadonly:
            self.textbox.config(state=tk.DISABLED)
        else:
            self.textbox.config(state=tk.NORMAL)
            
    def set_focus(self, event):
        '''Explicitly set focus, so user can select and copy text'''
        self.textbox.focus_set()       
        