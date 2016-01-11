#Options
#1) Team size 1 as individuals
#2) referals (microsites)
#3) Verified, Unverified, total, all
#4) check self sponsorship and returning users by email instead of con id 

from Tkinter import *
import ttk as ttk
import textbox as textbox
import DataClass as data
    
class OptionsTab:      
    def addnewref(self, mynewref):
        if mynewref:
            self.lbox.insert(END, mynewref)  
        self.refbox.delete(0, END)
    
    def delrefs(self):
        for idx in reversed(list(self.lbox.curselection())):
            self.lbox.delete(idx) 
    
    def TeamOneIndividual(self):
        self.data.notReady()
        if self.teamOfOne.get():
            self.data.setTeamOfOneAsInd(True)
        else:
            self.data.setTeamOfOneAsInd(False)
    
    def TeamRecombine(self):
        self.data.notReady()
        if self.recombine.get():
            self.data.recombineTeamDons(True)
        else:
            self.data.recombineTeamDons(False)

    def SetDateFirst(self):
        self.data.notReady()
        if self.dateFirst.get():
            self.data.SetdateFirst(True)
        else:
            self.data.SetdateFirst(False)
                
    def EventRecombine(self, val):
        self.data.combineevents(val)
        
        
    def updateValue(self, event):
        orglocations, newlocs = self.data.flattenlocations(100-self.slider.get())
        myout = []
        for a in orglocations:
            x = orglocations.index(a)
            if newlocs[x]:
                foo = "->".join((orglocations[x],newlocs[x]))    
            else:
                foo = "->".join((orglocations[x],orglocations[x]))
            foo += "\n"
            myout.append(foo)
        
        self.myout.clear()
        self.myout.readonly(False)
        for out in myout:
            self.myout.set(out, True)
        self.myout.readonly(True)
        self.data.notReady()
        
    def __init__(self, mytab, maindata):
        self.teamOfOne = IntVar()
        self.recombine = IntVar()
        self.dateFirst= IntVar()
        self.Eventcombine = StringVar()
        self.Eventcombine.set(data.getDepthLevels()[1])
        self.recombine.set(1)
        self.dateFirst.set(1)
        
        self.newref = StringVar()
        self.data = maindata
        
        #mytab widgets
        checkframe = Frame(mytab)
        refframe = Frame(mytab)
        sliderframe = Frame(mytab)
        
        #checkframe widgets
        self.CteamOfOne = ttk.Checkbutton(checkframe, text="Count people in Teams of 1 as individuals?", variable = self.teamOfOne, onvalue = 1, offvalue = 0, command=lambda: self.TeamOneIndividual())
        self.CteamRecombine = ttk.Checkbutton(checkframe, text="Recombine team donations?", variable = self.recombine, onvalue = 1, offvalue = 0, command=lambda: self.TeamRecombine())
        self.CdateFirst = ttk.Checkbutton(checkframe, text="Is day first (DD/MM/YYYY)", variable = self.dateFirst, onvalue = 1, offvalue = 0, command=lambda: self.SetDateFirst())
        depthlbl = ttk.Label(checkframe, text="Depth for groupby?")
        foo = data.getDepthLevels()
        self.CEventRecombine = ttk.OptionMenu(checkframe, self.Eventcombine, foo[1], *foo, command=self.EventRecombine)
        
        #self.CEventRecombine = ttk.Checkbutton(checkframe, text="Combine Events?", variable = self.Eventcombine, onvalue = True, offvalue = False, command=lambda: self.EventRecombine())
        
        #location round error
        self.sliderlabel = ttk.Label(sliderframe, text="How accurate to rename locations?: ")
        self.slider = Scale(sliderframe, from_=0, to=50, orient="horizontal")
        self.slider.bind("<ButtonRelease-1>", self.updateValue)
        self.myout = textbox.textbox(sliderframe, 0, 2)
        self.myout.readonly(True)    
        
        
        
        #refframe widgets
        self.lbox = Listbox(refframe, height=5, selectmode='extended')
        s = Scrollbar(refframe, orient=VERTICAL, command=self.lbox.yview)
        self.refbox = ttk.Entry(refframe, textvariable=self.newref)
        addbutton = ttk.Button(refframe, text="Add", command= lambda: self.addnewref(self.newref.get()))
        delbutton = ttk.Button(refframe, text="Delete", command=lambda: self.delrefs())
        
        checkframe.grid(column=0, row=0, sticky=(E,W))   
        #refframe.grid(column=0, row=1, sticky=(E,W))
        sliderframe.grid(column=0, row=3, sticky=(E,W))
        
        self.sliderlabel.grid(column=0, row=0, sticky=(E,W))
        self.slider.grid(column=0, row=1, sticky=(E,W))       
        
        self.lbox.grid(column=0, row=0, rowspan=5, sticky=(N,S,E,W))
        s.grid(column=1, row=0, rowspan=6, sticky=(N,S))
        delbutton.grid(column=0, row=6, sticky=(N,S,E,W))
        self.refbox.grid(column=2, row=0, sticky=(N,S,E,W))
        addbutton.grid(column=2, row=1, sticky=(N,S,E,W))
        
        self.CteamRecombine.grid(column=0, row=0, sticky=(W))      
        self.CteamOfOne.grid(column=0, row=1, sticky=(W))
        #self.CdateFirst.grid(column=0, row=2, sticky=(W))
        depthlbl.grid(column=0, row=3, sticky=(W))
        self.CEventRecombine.grid(column=0, row=4, sticky=(W))

