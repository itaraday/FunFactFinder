from Tkinter import *
import ttk as ttk
    
class singlecheck:
    def __init__(self, master, mytext, col, row):
        self.buttonval = IntVar()
        #self.buttonval.set(1)
        self.CheckButton = ttk.Checkbutton(master, text=mytext,
                                           variable=self.buttonval)    
        self.CheckButton.grid(column=col, row=row, sticky=(W))
        
    def ischeck(self):
        if self.buttonval.get():
            return True
        else:
            return False    
        
        
            
class checklist:
    def __init__(self, master, col, row, mytext = None, mydict = None):
        self.buttonDic = {}
        if mytext != None:
            self.buttonDic[mytext] = IntVar()
            aCheckButton = ttk.Checkbutton(master, text=mytext,
                                           variable=self.buttonDic[mytext])
            aCheckButton.grid(sticky='w')
        elif mydict != None:
            for key in sorted(mydict.iterkeys()):
                self.buttonDic[key] = IntVar()
                aCheckButton = ttk.Checkbutton(master, text=key,
                                                variable=self.buttonDic[key])
                aCheckButton.grid(column=col, row=row, sticky=(W))
                row += 1
        else:
            raise Exception("Must use either text or a dictionary")


    def geton(self, myvalue = 1):
        return [key for key, value in self.buttonDic.iteritems() if value == myvalue]