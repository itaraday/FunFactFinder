from Tkinter import *
import tkFileDialog
import ttk as ttk
import GuiReportRow as rrow
import DataClass as data
import tkFont
from math import ceil
import textbox as textbox
import GuiFunctions as gFunc
#from multiprocessing import Process

class ReportsTab:          
    def transweek(self):
        year = self.year.get('1.0', 'end')
        week = self.week.get('1.0', 'end')
        try:
            year = int(year)
            week = int(week)
            cal = gFunc.iso_to_gregorian(year, week, 1)
            self.calendar.set(cal.strftime("%d %B %Y"), False)    
        except:
            print "Need to enter numbers for week and year"
        
    def updateUDF(self, type, action, name):
        self.reports["UDF Fundraisers"].updateDD(action, name)
        
    def update(self, eventtype):
        for key in sorted(self.reports.iterkeys()):
            self.reports[key].hide()
        for validreport in data.getrunnablereports(eventtype):
            self.reports[validreport].show()      
    
    def printreports(self):
        needtosaveExcel = False
        needtosaveCSV = False
        filename = ""
        directory = ""
        self.mydata.getready()
        counter = 0
        
        for report in sorted(self.reports.iterkeys()):
            if self.reports[report].selected():
                counter += 1
                if not (needtosaveExcel and needtosaveCSV):
                    foo = self.reports[report].getoutputs()
                    if "Excel Sheet" in foo and foo["Excel Sheet"] == True:
                        needtosaveExcel = True
                    if "CSV" in foo and foo["CSV"] == True:
                        needtosaveCSV = True
        counter = ceil(100/counter)   
        
        if needtosaveExcel:
            filename = tkFileDialog.asksaveasfilename(title='Save Excel workbook as',defaultextension="*.xlsx", filetypes=[('Excel File', '*.xlsx')])#,('CSV files', '*.csv')))
            #directory = filename.split("/")
            #directory = "/".join(directory[:-1])
            self.mydata.setexceloutput(filename)
            
        if needtosaveCSV:
            directory = tkFileDialog.askdirectory(title='Save CSV files in')
            self.mydata.setdirectory(directory)
        
        
        
        
        #if ((needtosaveExcel or needtosaveCSV) and filename) or (not (needtosaveExcel or needtosaveCSV)):
        if (bool(needtosaveExcel) == bool(filename)) and (bool(needtosaveCSV) == bool(directory)):
            print "Analysis started"
            for report in sorted(self.reports.iterkeys()):
                #print key + ' ' + str(self.reports[key].selected()) + ' ' + str(myreports[key].getoption()) + str(myreports[key].getoutputs())
                if self.reports[report].selected():
                    foo = self.reports[report].getoption()
                    if foo != "Error":
                        #p = Process(target=self.mydata.run, args=([self.reports[report].getoutputs(), self.reports[report].getoption()]))
                        self.mydata.run(report, self.reports[report].getoutputs(), self.reports[report].getoption())
                    else:
                        #p = Process(target=self.mydata.run, args=([self.reports[report].getoutputs()]))
                        self.mydata.run(report, self.reports[report].getoutputs())
                    #p.start()
                    self.pb2.step(counter)
                    self.pb2.update()
            #p.join()
            if (needtosaveExcel):
                self.mydata.printExcel() 
            print "Done"
            print "-------------------------"
        else:
            print "If saving to Excel/CSV you need to supply a filename"
                              
    def __init__(self, mytab, maindata):   
        self.mydata = maindata    
        #mytab widgets
        labelsframe = Frame(mytab)
        reportsframe = Frame(mytab)
        button = ttk.Button(mytab, text='Zeh Button', command=lambda: self.printreports()) 
        self.pb2 = ttk.Progressbar(mytab, length=100, mode='determinate')
        dateframe = Frame(mytab)
        
        
        #Labelframe
        title = tkFont.Font(size=16, underline=1, weight="bold")
        reportname = ttk.Label(labelsframe, text="Report", font=title)
        reportops = ttk.Label(labelsframe, text="Report Options", font=title)
        reportout = ttk.Label(labelsframe, text="Output", font=title)
        reportname.grid(column=0, row=0)
        reportops.grid(column=1, row=0)
        reportout.grid(column=2, row=0) 
        labelsframe.grid(column=0, row=0, sticky=(N,W), pady=(0,10))
        labelsframe.columnconfigure(0, minsize = 100)
        labelsframe.columnconfigure(1, minsize = 150)
        labelsframe.columnconfigure(2, minsize = 300)
                        
        #reportframe
        counter = 0
        self.reports = {}
        for myreport in data.getrunnablereports("All"):
            self.reports[myreport] = rrow.reportrow(reportsframe, myreport, 0, counter, data.getreportoptions(myreport), data.getoutputs(myreport))
            counter += 1

        reportsframe.grid(column=0, row=1, sticky=(N,W), padx=(10,0))   
           
        #button
        button.grid(column=0, row=2, sticky=(N,W), padx=(10,0))
        self.pb2.grid(column=0, row=3, sticky=(E,W),padx=(10,10))
        self.update("Describe")
        
        #dateframe
        dateframe.grid(column=0, row=4, sticky=(W), padx=(10,0))
        yearlbl = ttk.Label(dateframe, text="Year", width=10)
        weeklbl = ttk.Label(dateframe, text="Week", width=10)
        self.year = Text(dateframe, width=10, height=1)
        self.week = Text(dateframe, width=10, height=1)
        self.calendar = textbox.textbox(dateframe, 0, 3, 1, 40)
        self.calendar.readonly(True)
        datebutton = ttk.Button(dateframe, text='translate week number', command=lambda: self.transweek()) 

        yearlbl.grid(column=0, row=0, sticky=(W))
        weeklbl.grid(column=0, row=1, sticky=(W))
        self.year.grid(column=1, row=0, sticky=(W))
        self.week.grid(column=1, row=1, sticky=(W))        
        datebutton.grid(column=0, row=2, sticky=(W))