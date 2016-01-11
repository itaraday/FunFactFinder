from Tkinter import *
import datetime

def getRoot(widget):
    root = widget._nametowidget(widget.winfo_parent())
    while root.winfo_parent() != "":
        root = root._nametowidget(root.winfo_parent())
    return root

def loadreports(mytabs, tabevents, eventsTab):
    mynewdata = eventsTab.changeLbox(tabevents)
    if mynewdata:
        mytabs.tab(1, state="normal")
        mytabs.tab(2, state="normal")
        mytabs.tab(3, state="normal")
        mytabs.tab(4, state="normal")

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime.date(iso_year, 1, 4)
    delta = datetime.timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + datetime.timedelta(days=iso_day-1, weeks=iso_week-1)