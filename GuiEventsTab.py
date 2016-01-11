from Tkinter import *
import ttk as ttk
import tkFont as tfont
import tkFileDialog as tfgiag
import pandas as pd
import GuiFunctions as gFunc
#from multiprocessing import Process, Queue


class EventsTab: 
    def radsel(self):
        text = str(self.reportBehav.get())   
        self.data.settype(text)
        self.myreports.update(text)
        if text == "Compare":
            self.mainEventBox["state"] = "readonly"
            self.getevents()
            self.moveelmframe.grid_remove()
        elif text == "Year":
            self.moveelmframe.grid()
            self.mainEventBox["state"] = "disabled"
        elif text == "Describe":
            self.moveelmframe.grid_remove()
            self.mainEventBox["state"] = "disabled"
      
    def move(self, movement):
        for idx in reversed(list(self.lbox.curselection())):
            idx = int(idx)
            last = self.lbox.index(END)-1
            if not((idx==0 and movement==-1) or (idx==last and movement==1)):
                text = self.lbox.get(idx)
                self.lbox.delete(idx)
                self.lbox.insert(idx+movement,text) 

    def curselect(self, evt):
        if self.lbox.curselection():
            self.getevents()
    
    def selectall(self):
        self.lbox.select_set(0, last=END)
        self.getevents()
        
    def getevents(self, *args):
        events = [self.lbox.get(idx) for idx in self.lbox.curselection()]
        text = str(self.reportBehav.get()) 
        main = ""
        if text == "Compare":
            main = self.mainEvent.get()        
        if main in events:
            events.remove(main)
        self.data.setevents(events, main)
        self.myudfs.update()
             
    def __init__(self, mytab, reportTab, udfTab, mydata):
        self.myudfs = udfTab
        self.myreports = reportTab  
        self.data = mydata
        self.mainEvent = StringVar()        
        self.reportBehav = StringVar()
        self.reportBehav.set("Describe")
        
        self.lbox = Listbox(mytab, height=5, selectmode='extended', exportselection=0)
        self.lbox.bind('<<ListboxSelect>>',self.curselect)
        self.s = Scrollbar(mytab, orient=VERTICAL, command=self.lbox.yview)       
        
        self.moveelmframe = Frame(mytab, bd=1, relief=RIDGE)
        moveupbtn = ttk.Button(self.moveelmframe, text="Move Up", command= lambda: self.move(-1))
        movedownbtn = ttk.Button(self.moveelmframe, text="Move Down", command= lambda: self.move(1))
        selectallbtn = ttk.Button(self.moveelmframe, text="Select All", command = lambda: self.selectall())
        self.pb = ttk.Progressbar(self.moveelmframe, orient=VERTICAL, mode='indeterminate')
        #self.pb = ttk.Progressbar(self.moveelmframe, orient=tk.VERTICAL, length=100)
        
        radioframe = Frame(mytab, bd=1, relief=RIDGE)
        foo = tfont.Font(underline=1, weight="bold")
        radioTitle = Label(radioframe, text="Describe or compare the events?", font=foo)
        self.descbutton = Radiobutton(radioframe, text="Describe", variable=self.reportBehav, value="Describe", command=lambda: self.radsel())
        self.compbutton = Radiobutton(radioframe, text="Compare", variable=self.reportBehav, value="Compare", command=lambda: self.radsel())
        self.yearbutton = Radiobutton(radioframe, text="Year to year", variable=self.reportBehav, value="Year", command=lambda: self.radsel())
        self.mainEventBox = ttk.Combobox(radioframe, textvariable=self.mainEvent, state="disabled")
        self.mainEvent.trace('w', self.getevents)
               
        self.lbox.grid(column=0, rowspan=5, sticky=(N,S,E,W))
        self.s.grid(column=1, row=0, rowspan=5, sticky=(N,S))
        #radioframe.grid(column=2, row=0, sticky=(N,E,W), padx=(10,10), pady=(10,0), ipadx=5, ipady=5)
        self.moveelmframe.grid(column=2, row=0, sticky=(N,E,W), ipadx=3, ipady=3, padx=(10,10), pady=(10,10))
        #self.moveelmframe.grid_remove()
        
        radioTitle.grid(column=0, row=0, sticky=(N,S,E,W), pady=(0,10))
        self.descbutton.grid(column=0, row=1, sticky=(N,S,E,W))
        self.compbutton.grid(column=0, row=3, sticky=(N,S,E,W))
        self.yearbutton.grid(column=0, row=2, sticky=(N,S,E,W))
        self.mainEventBox.grid(column=0, row=4, sticky=(N,S,E,W))
        
        moveupbtn.grid(column=0, row=0, sticky=(N,S,E,W))
        movedownbtn.grid(column=0, row=1, sticky=(N,S,E,W))
        selectallbtn.grid(column=0, row=2, sticky=(N,S,E,W))
        #self.pb.grid(column=0, row=3, sticky=(N,S))
        
        mytab.columnconfigure(0, weight=1)

        mytab.rowconfigure(0, weight=1)
    

    def changeLbox(self, mytab):         
        root = gFunc.getRoot(mytab)
        mynewdata = tfgiag.askopenfilenames(parent=root,title='Choose a file',filetypes=[('CSV files', '.csv')])
        vals = []
        self.mainEventBox["values"] = vals
        if mynewdata:
            #reset old variables
            self.pb.start()
            self.data.maindata = pd.DataFrame()     
            self.lbox.delete(0, self.lbox.size())
            #populate lists and data
            for myfile in root.tk.splitlist(mynewdata): 
                foo = pd.read_csv(myfile, error_bad_lines=False)   
                if (self.data.maindata.empty):
                    self.data.setMainData(foo)
                else:
                    self.data.appendMainData(foo)
                eventlist = []
                for eventID in foo["Event ID"].unique():
                    self.lbox.insert(END, eventID)
                    eventlist.append(eventID)
                    vals.append(eventID)
                print myfile
            self.mainEventBox["values"] = vals
            self.mainEventBox.set(vals[0])
            self.pb.stop()
        else:
            print "Cancelled"
        return mynewdata