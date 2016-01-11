#Options
#1) Team size 1 as individuals
#2) referals (microsites)
#3) Verified, Unverified, total, all
#4) check self sponsorship and returning users by email instead of con id 

from Tkinter import *
import ttk as ttk
import textbox as textbox
    
class UDFTab:   
    def __init__(self, mytab, reportTab, mydata):   
        self.myUDF = mytab  
        self.data = mydata
        self.reportTab = reportTab
        
        self.lbox = Listbox(mytab, height=5, selectmode='extended', name="list")#, exportselection=0)
        self.lbox.my_name = "list"
        self.lbox.bind('<<ListboxSelect>>',self.curselect)
        self.s = Scrollbar(mytab, orient=VERTICAL, command=self.lbox.yview)       
            
        self.lbox.grid(column=0, rowspan=5, columnspan=4, sticky=(N,S,E,W))
        self.s.grid(column=5, row=0, rowspan=5, sticky=(N,S))
 
        delmergebtn = ttk.Button(mytab, text="Delete Merge", command= lambda: self.removeUDFS(self.mergedbox))
        delmergebtn.grid(column=0, row=6, sticky=(N,S,E,W))       
        self.mergedUDF = textbox.textbox(mytab, 1, 6, 1,1)
        self.mergedUDF.readonly(False)
        mergebtn = ttk.Button(mytab, text="Merge", command= lambda: self.moveUDFSlist(self.lbox, self.mergedbox, self.mergedUDF))
        mergebtn.grid(column=2, row=6, sticky=(N,S,E,W))
                
        self.mergedbox = Listbox(mytab, height=5, selectmode='extended', name="merge")
        self.mergedbox.my_name = "merge"
        self.mergedbox.bind('<<ListboxSelect>>',self.curselect)
        self.smerged = Scrollbar(mytab, orient=VERTICAL, command=self.mergedbox.yview)       
        self.mergedbox.grid(column=0, row=7, rowspan=5, columnspan=4, sticky=(N,S,E,W))
        self.smerged.grid(column=5, row=7, rowspan=5, sticky=(N,S))        

        delgroupbtn = ttk.Button(mytab, text="Delete Group", command= lambda: self.removeUDFS(self.groupedbox))
        delgroupbtn.grid(column=0, row=13, sticky=(N,S,E,W))        
        self.groupedUDF = textbox.textbox(mytab, 1, 13, 1,1)
        self.groupedUDF.readonly(False)
        groupbtn = ttk.Button(mytab, text="Group", command= lambda: self.moveUDFSlist(self.mergedbox, self.groupedbox, self.groupedUDF))
        groupbtn.grid(column=2, row=13, sticky=(N,S,E,W))
                
        self.groupedbox = Listbox(mytab, height=5, selectmode='extended', name="group")
        self.groupedbox.my_name = "group"
        self.groupedbox.bind('<<ListboxSelect>>',self.curselect)
        self.sgrouped = Scrollbar(mytab, orient=VERTICAL, command=self.groupedbox.yview)       
        self.groupedbox.grid(column=0, row=14, rowspan=5, columnspan=4, sticky=(N,S,E,W))
        self.sgrouped.grid(column=5, row=14, rowspan=5, sticky=(N,S))               
        
        mytab.columnconfigure(0, weight=1)
        mytab.columnconfigure(1, weight=1)
        mytab.columnconfigure(2, weight=1)
        mytab.columnconfigure(3, weight=1)
        mytab.rowconfigure(0, weight=1)
        mytab.rowconfigure(7, weight=1)
    
    
    #move UDF's from start list to end list
    #need to make sure the dataclass keeps track of which UDF's are part of which lists/dictionary
    def moveUDFSlist(self, start, end, mytextbox):
        #getting keys from merged/grouped UDF dictionarys from data class
        mydict = self.data.getUDFS(end.my_name)
        #getting name from textbox passed
        mergedname = mytextbox.get().strip().replace(" ", "_")
        #need to make sure the name is not blank and is unique
        #also need to make sure name doesn't exist as a column already
        if mergedname and self.data.checkname(end.my_name, mergedname) and len(start.curselection()):
            self.data.notReady()
            end.insert(0,mergedname)
            for idx in reversed(list(start.curselection())):     
                idx = int(idx)
                text = start.get(idx)
                self.data.tidyUDF(mergedname, text, end.my_name)
            self.reportTab.updateUDF("dropdown", "add", " ".join([end.my_name, mergedname]))
            mytextbox.clear()
        else:
            print "Need to include a unique name to call the UDFS"
                

    #for future date make sure when deleting a merged UDF there is no grouped UDF that uses it
    def removeUDFS(self, start):
        self.data.notReady()
        for idx in reversed(list(start.curselection())):     
            idx = int(idx)
            text = start.get(idx)
            self.data.removeUDF(text, start.my_name)
            start.delete(idx)
            self.reportTab.updateUDF("dropdown", "remove", " ".join([start.my_name, text]))
            
            
                
    def update(self):
        for start in [self.mergedbox, self.groupedbox]:
            self.removeUDFS(start)
        self.lbox.delete(0, self.lbox.size())
        for UDF in self.data.getUDFS(self.lbox.my_name):
            self.lbox.insert(END, UDF) 
    
    
    #when you select UDF's need to highlight which ones they represent
    #Also unselect values from the other UDFS
    def curselect(self, evt):
        mylistboxes = { 
                       self.mergedbox.my_name: self.lbox,
                       self.groupedbox.my_name: self.mergedbox
                    }
        myboxes = [self.lbox, self.mergedbox, self.groupedbox]
        for box in myboxes:
            for idx in range(0, box.size()):     
                idx = int(idx)
                box.itemconfig(idx, bg='white') 
                
        w = evt.widget
        #print w.my_name
        #need to highlight values from listbox above
        if w.my_name in mylistboxes:
            myudfs = []
            #pull UDFS for each one selected
            for idx in reversed(list(w.curselection())):     
                idx = int(idx)
                text = w.get(idx)
                myudfs.append(self.data.getUDF(text, w.my_name))
            myudfs = [val for sublist in myudfs for val in sublist]
            for idx in range(0, mylistboxes[w.my_name].size()):     
                text = mylistboxes[w.my_name].get(idx)
                if text in myudfs:
                    mylistboxes[w.my_name].itemconfig(idx, bg='green') 
                    #if group highlight from normal list
                    if (mylistboxes[w.my_name].my_name in mylistboxes):
                        myudfsMerge = self.data.getUDF(text, mylistboxes[w.my_name].my_name)
                        #myudfsMerge = [val for sublist in myudfs for val in sublist]
                        for idx in range(0, mylistboxes[mylistboxes[w.my_name].my_name].size()): 
                            textlist = mylistboxes[mylistboxes[w.my_name].my_name].get(idx)
                            if textlist in myudfsMerge:
                                mylistboxes[mylistboxes[w.my_name].my_name].itemconfig(idx, bg='green') 
                     
                     
                
        

