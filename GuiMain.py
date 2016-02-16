from Tkinter import *
import ttk as tkk
import DataClass as data
import tkMessageBox
import GuiEventsTab as gETab
import GuiUDFTab as gUTab
import GuiOptionsTab as gOTab
import GuiReports as gRTab
import GuiFunctions as gFunc
import GuiOutput as gOut
from tempfile import mkstemp
import pandas as pd
#import statsmodels.api


#destorying the gui elegantly    
def ask_quit(root, maindata):
    if tkMessageBox.askokcancel("Quit", "You want to quit now? *sniff*"):
        maindata.clear()
        root.destroy()
        
def main():   
    pd.options.mode.chained_assignment = None
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('expand_frame_repr', False)
    print "Pandas version: {}".format(pd.__version__)
    print "Fun Fact Finder now online!!"
    maindata = data.datasets() 
    
    root = Tk()
    
    #removing the Tkinter logo by creating a temp blank icon file
    ICON = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
            b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
            b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            '\x00\x01\x00\x00\x00\x01') + b'\x00'*1282 + b'\xff'*64

    _, ICON_PATH = mkstemp()
    with open(ICON_PATH, 'wb') as icon_file:
        icon_file.write(ICON)    
          
    root.iconbitmap(default=ICON_PATH)
    
    root.title("Fun Fact Finder")
    root.protocol("WM_DELETE_WINDOW",lambda: ask_quit(root, maindata))
    root.geometry('800x800+10+10')
    root.minsize(550,500)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    tkk.Sizegrip(root).grid(column=999, row=999, sticky=(S,E))
            
    mytabs = tkk.Notebook(root)   
    
    tabevents = Frame(mytabs)
    mytabs.add(tabevents, text="Choose Events")
    
    taboptions = Frame(mytabs) 
    mytabs.add(taboptions, text="Options")
    mytabs.tab(1, state="disabled")    

    tabudfs = Frame(mytabs) 
    mytabs.add(tabudfs, text="UDFs")
    mytabs.tab(2, state="disabled")  
        
    tabreports = Frame(mytabs)  
    mytabs.add(tabreports, text="Reports")
    mytabs.tab(3, state="disabled")    
    
    taboutput = Frame(mytabs)       
    mytabs.add(taboutput, text="output")
    mytabs.tab(4, state="disabled")
    
    reportTab = gRTab.ReportsTab(tabreports, maindata)
    
    udfTab = gUTab.UDFTab(tabudfs, reportTab, maindata)
    eventsTab = gETab.EventsTab(tabevents, reportTab, udfTab, maindata)
    optionsTab = gOTab.OptionsTab(taboptions, maindata)
    outputTab = gOut.output(taboutput)
    maindata.setoutput(outputTab)
    
    #Adding Menu
    root.option_add('*tearOff', FALSE)
    menubar = Menu(root)
    root['menu'] = menubar
    menu_file = Menu(menubar)
    menubar.add_cascade(menu=menu_file, label='File')
    
    menu_file.add_command(label='Open', command=lambda: gFunc.loadreports(mytabs, tabevents, eventsTab))
    mytabs.grid(row=0, column=0, sticky=(N,E,S,W))
    
    root.mainloop()
    
if __name__ == '__main__':
    main() 
