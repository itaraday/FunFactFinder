from Tkinter import *
import ttk as ttk
import mycheckbox as chk
import DropDownBox as dd

class reportrow:      
    def __init__(self, master, mytext, col, row, myoptions, myoutputs):
        self.myoutputs = myoutputs
        self.hidden = False
        self.myframe = Frame(master)
        self.mycheck = chk.singlecheck(self.myframe, mytext, 0, 0)
        if not "Error" in myoptions:
            self.dropdown = dd.DropDownBox(self.myframe, myoptions, 1, 0)            
        else:
            blank = ttk.Label(self.myframe, text='')
            blank.grid(column=1, row=row, sticky=(W))
        
        #["Summary", "Excel Sheet", "Graph"]
        if "Summary" in myoutputs:
            self.summary = chk.singlecheck(self.myframe, "Summary", 2, 0)
        else:
            blankSum = ttk.Label(self.myframe, text='')
            blankSum.grid(column=2, row=0)
            self.summary = "Error"
        if "Excel Sheet" in myoutputs:
            self.excel = chk.singlecheck(self.myframe, "Excel Sheet", 3, 0)
        else:
            blankExcel = ttk.Label(self.myframe, text='')
            blankExcel.grid(column=3, row=0)   
            self.excel = "Error"         
        if "Graph" in myoutputs:
            self.graph = chk.singlecheck(self.myframe, "Graph", 4, 0)
        else:
            blankGraph = ttk.Label(self.myframe, text='')
            blankGraph.grid(column=4, row=0) 
            self.graph = "Error"
        if "CSV" in myoutputs:
            self.csv = chk.singlecheck(self.myframe, "CSV", 5, 0)
        else:
            blankcsv = ttk.Label(self.myframe, text='')
            blankcsv.grid(column=5, row=0) 
            self.csv = "Error"            
        self.myframe.grid(column=col, row=row, sticky=(E,W))   
        self.myframe.columnconfigure(0, minsize = 150)
        self.myframe.columnconfigure(1, minsize = 150)
        self.myframe.columnconfigure(2, minsize = 100)
        self.myframe.columnconfigure(3, minsize = 100)
        self.myframe.columnconfigure(4, minsize = 100)
        self.myframe.columnconfigure(5, minsize = 100)
                  
    def getoption(self):
        try:
            foo = self.dropdown.getSelecton()
        except:
            foo = "Error"
        return foo
    
    def getoutputs(self):
        myouts = {"Summary": False, "Excel": False, "Graph": False, "CSV": False}
        if "Summary" in self.myoutputs:
            myouts["Summary"] = self.summary.ischeck()
        if "Excel Sheet" in self.myoutputs:
            myouts["Excel Sheet"] = self.excel.ischeck() 
        if "Graph" in self.myoutputs:
            myouts["Graph"] = self.graph.ischeck()           
        if "CSV" in self.myoutputs:
            myouts["CSV"] = self.csv.ischeck()               
        return myouts
        
        
    def selected(self):
        return self.mycheck.ischeck()
            
    def ishidden(self):
        return self.hidden
        
    def hide(self):
        self.hidden = True
        self.myframe.grid_remove()
    
    def show(self):
        self.hidden = False
        self.myframe.grid()
        
    def updateDD(self, action, name):
        self.dropdown.updateDD(action, name)
        
