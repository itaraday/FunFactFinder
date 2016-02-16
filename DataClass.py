import pandas as pd
import Excel as excelwriter
from fuzzywuzzy import fuzz
import datetime
import matplotlib.pyplot as plt
import numpy as np
#import statsmodels.api as sm
from Mosaic import MosaicPlot
import PyQt4
import itertools
import json
#import time
#from statsmodels.graphics.mosaicplot import mosaic

#import scipy as sci

#constants
###############################
#outputs
EXCEL = "Excel Sheet"
SUMMARY = "Summary"
GRAPH = "Graph"
CSV = "CSV"
#last column before UDFS
BEFOREUDFS = "URL Referrer"
#UDF constants
LIST = "list"
GROUP = "group"
MERGE = "merge"
#For groupby
COMBINED = "Combined"
EVENT = "Event"
LOC = "Location"


def getDepthLevels():  
    foo = [COMBINED, EVENT, LOC]
    return foo
    
#convert a list of lists into 1 long list
def flattenlist(l):
    return [item for sublist in l for item in sublist]

#Quick function to combine 2 strings to get "title (option)"
def maketitle(text, options):
    return "".join((text, " (", options, ")"))

#all runnable reports that the GUI shows
#for adding new options need to:
#ignore text, no longer used
#1) add the report here
#2) add the report options in getreportoptions
#3) add outputs in getoutputs
def getrunnablereports(text):
        myreports = ["Mapping", "Corporate teams", "Signups", "Active Users", "Proxy", "Goal", "Donations", "Histogram", "Self Sponsors", "Growth", "Returning Users", "Donation Timeline", "Registrant Timeline", "Fundraised by Typology", "Team Details", "Social Media", "Mobile", "UDF Fundraisers", "Summary", "Reg Fee"]
        #if text == "Compare":
        #    myreports = ["Active Users", "Donations", "Histogram", "Self Sponsors", "Returning Users"]
        #elif text == "Year":
        #    myreports = ["Active Users", "Donations", "Histogram", "Self Sponsors", "Growth", "Returning Users"]
        #elif text == "Describe":
        #    myreports = ["Active Users", "Goal", "Donations", "Histogram", "Self Sponsors", "Growth", "Returning Users", "Locations", "Donation Timeline", "Registrant Timeline", "Fundraised by Typology", "Team Details", "Social Media", "Mobile"]
        #elif text == "All":
        #    myreports = ["Active Users", "Goal", "Donations", "Histogram", "Self Sponsors", "Growth", "Locations", "Returning Users", "Donation Timeline", "Registrant Timeline", "Fundraised by Typology", "Team Details", "Social Media", "Mobile", "UDF Fundraisers"]
        #else:
        #    raise Exception("Not a good event type comparison")
        if myreports:
            myreports.sort()
        return myreports

#options per report
def getreportoptions(text):
    myoptions = []
    if text in ["Histogram", "Donations"]:
        myoptions = ["Verified","Pledges","Online","Mobile","Facebook", "Paidins", "orgs", "All"] #"whitepaper" 
    elif text in ["Returning Users", "Self Sponsors"]:
        myoptions = ["Constituent ID", "Email"]
    elif text in ["Active Users", "Locations", "Growth", "Donation Timeline", "Goal"]:
        myoptions = ["Verified", "Total"]
    elif text in ["Fundraised by Typology"]:
        myoptions = ["Verified", "Total", "Pledges"]
    elif text in ["Social Media"]:
        myoptions = ["All", "Referral", "FPF", "Facebook Connect"]
    elif text in ["Mobile"]:
        myoptions = ["Registrants", "Fundraisers"]
    elif text in ["UDF Fundraisers"]:
        myoptions = []
    elif text in ["Proxy"]:
        myoptions = ["Proxies", "Data Entry", "Registered Others"]
    elif text in ["Mapping"]:
        myoptions = ["Canada", "USA", "AUS"]
    elif text in ["Corporate teams"]:
        myoptions = ["Verified", "Pledges"]
    elif text in ["Registrant Timeline"]:
        myoptions = ["Online","Import"]
    else:
        myoptions = ["Error"]
    return myoptions

#outputs for the reports (see constants for options)
def getoutputs(text):
    outputs = []
    if text in ["Mapping", "Goal"]:
        outputs = [EXCEL, CSV]
    elif text in ["Returning Users", "Social Media", "Summary", "Reg Fee", "Team Details", "Proxy", "Corporate teams"]:
        outputs = [EXCEL, SUMMARY, CSV]
    elif text in ["Signups"]:
        outputs = [SUMMARY]
    else:
        outputs = [SUMMARY, EXCEL, GRAPH, CSV]
    return outputs

#Data munging for the Snapshot report
#Need to convert "date" strings into Python dates
#Convert all strings to upper case
#Convert currency data into floats                
def cleandata(data):
    data["Postal Code"] = data["Postal Code"].astype(str)
    remcur = ["Donation Amount", "Team Goal", "Payment Amount", "Participant Goal", "Net Reg Fee Amount"]
    convdate = ["Registration Date"]
    convdatetime = [["Donation Datetime", "Donation Date", "Donation Time"]]
    convupper = ["Mobile App", "Email Address","First Name", "Last Name", "Solicitor First Name", "Solicitor Last Name", "Location ID", "Location Name", "URL Referrer", "Postal Code"]
    concoding = ["Team Name", "First Name", "Last Name", "Email Address", "Solicitor Last Name", "Solicitor First Name"]
    data["Event ID"] = data["Event ID"].astype(str)
    data = removecurrency(data, remcur)
    data = converttodate(data, convdate)
    data = convertupper(data, convupper)
    data = converttodatetime(data, convdatetime)
    data = changeencode(data, concoding)
    data["Location Name"] = data["Location Name"].fillna("Unsolicited")
    return data

#making sure the encryption is the right one for printing to Excel
def changeencode(data, cols):
    for col in cols:
        data[col] = data[col].str.decode('iso-8859-1').str.encode('utf-8')
        #try:
            #data[col] = data[col].str.decode('iso-8859-1').str.encode('utf-8')
        #except: 
            #print "\n ---- can't convert case in {}".format(col)
    return data   

#takes a tuple col[0] = new column name in DF, col[1] = date and col[2] = time
def converttodatetime(data, condatetime):
    for col in condatetime:
        data[col[0]] = pd.to_datetime(data[col[1]]+ ' ' + data[col[2]], dayfirst=True)#self.dateFirst)
    return data

def convertupper(data, convupper):
    for col in convupper:
        #data[col] = data[col].str.decode('iso-8859-1').str.encode('utf-8').str.upper()
        try:
            data[col] = data[col].str.decode('iso-8859-1').str.encode('utf-8').str.upper()
        except AttributeError:
            pass
    return data

def converttodate(data, convdate):
    for col in convdate:
        data[col] = pd.to_datetime(data[col], dayfirst=True)#self.dateFirst)
    return data

#convert currency to number 
def removecurrency(data, remcur):
    for col in remcur:
        try:
            data[col] = data[col].str.replace("[^\d\.]","").astype(float)
        except:
            ids = data["Event ID"].unique().tolist()
            #print "\n----- Currency problem in {}: {}".format(ids, col)
    return data
            
#returning list of all UDFS in report
#see constants for assumed last column before UDFS
def getUDFsFromData(data):
    URLRefLoc = data.columns.get_loc(BEFOREUDFS)+1
    foo = data.ix[:, URLRefLoc:].columns.tolist()
    return foo
        
                  
class datasets: 
    def clear(self):
        self.maindata = pd.DataFrame()
        
    def __init__(self):
        self.maindata = pd.DataFrame() #main data, but aside from cleaning it I shouldn't change this data!!!!
        self.reporttype = "Describe"
        self.events = []
        self.mainevent = ""
        self.ready = False
        self.excelout = excelwriter.exceloutput()
        self.TeamsOfOne = True
        self.dataFilByEvent = self.maindata
        self.changelocations = False
        self.RecombineTeams = True
        self.UDFS = []
        self.CleanedUDFs = {}
        self.GroupedUDFs = {}
        self.depthLevel = EVENT
        self.dateFirst = True
        
    def settype(self, mytype):
        self.reporttype = mytype
           
    def depth(self):
        if self.depthLevel == COMBINED:
            return ["Event ID"]
        elif self.depthLevel == EVENT:
            return ["Event ID"]
        elif self.depthLevel == LOC:
            return ["Event ID", "Location Name"]
    
    def notReady(self):
        self.ready = False
    
    

        
    #When reading in data can either set it as new data or append to the existing data set
    #this function reads a snapshot report, cleans it and sets that data as a new dataset
    def setMainData(self, data):
        data = cleandata(data)
        print data['Event ID'].unique()
        self.UDFS = []
        self.CleanedUDFs = {}
        self.GroupedUDFs = {}
        self.UDFS.append(getUDFsFromData(data))
        self.maindata = data
    
    #appending data to the main data set
    def appendMainData(self, data):
        data = cleandata(data)
        print data['Event ID'].unique()
        self.UDFS.append(getUDFsFromData(data))
        self.maindata = self.maindata.append(data, ignore_index=True)       
    
    #Need to know where to save Excel files
    def setexceloutput(self, filename):
        self.outputfile = filename  
    def setdirectory(self, filename):
        self.outputdir = filename  
            
    #If running the dataset on just a subset of events    
    def setevents(self, events, mainevent):
        self.events = events
        self.mainevent = mainevent
        self.ready = False
    
    def combineevents(self, combined):
        self.depthLevel = combined
        self.ready = False
        
    
    #For summarizing data sets where to print the data    
    def setoutput(self, out):
        self.output = out
    
    #Should teams of 1 be counted as individuals (when looking at fundraisers)    
    def setTeamOfOneAsInd(self, TeamOfOneAsInd):
        if TeamOfOneAsInd:
            self.TeamsOfOne = False
        else:
            self.TeamsOfOne = True
    
    #flag that controls if need to recombine team donations. 
    def recombineTeamDons(self, recombine):
        if recombine:
            self.RecombineTeams = True
        else:
            self.RecombineTeams = False
        
    def SetdateFirst(self, isDateFirst):
        if isDateFirst:
            self.dateFirst = True
        else:
            self.dateFirst = False       
           
        
    #see setevents function. Even If I use all datasetas though I don't want to
    #change the original dataset
    def filterbyevent(self):
        self.dataFilByEvent = self.maindata[self.maindata["Event ID"].isin(self.events)]
    #I want locations like "Toronto, On" to match with "Toronto". Returns a tuple of 2 lists
    #1 with the old location names
    #1 with the new location names   
    def flattenlocations(self, percentage):
        #getting a list of all unique locations BY EVENT
        self.filterbyevent()
        locgrps = self.dataFilByEvent.groupby("Event ID")["Location Name"].unique().tolist()
        self.orglocations = []
        map(self.orglocations.extend, locgrps)
        self.newlocs = list(self.orglocations)
        #if percentage not 100 than start to flatten
        if percentage < 100:
            self.changelocations = True
            for loc in self.newlocs:
                #only want to flatten locations that are unique across all events
                if self.newlocs.count(loc)<=1:
                    pos = self.newlocs.index(loc)
                    mymax = percentage
                    best = ""
                    #going through all locations to see which it best matches to
                    for comp in self.newlocs:
                        if pos != self.newlocs.index(comp):
                            ratio = fuzz.ratio(loc, comp)
                            ratio = ratio + 3*self.newlocs.count(comp) - 3
                            #if the match percentage is within acceptable error message keep track of it, else don't change
                            if ratio > mymax:
                                best = comp
                                mymax = ratio
                    self.newlocs[pos] = best
        else:
            self.changelocations = False
        return self.orglocations, self.newlocs
    
        
    def changeplaces(self, x):
        if self.newlocs[x]:
            return self.newlocs[x]
        else:
            return self.orglocations[x]
    
    #returns the UDF's the way the program sees them
    def getUDFS(self, mytype):
        #full list of all UDFS
        if (mytype == LIST):
            foo = list(set(flattenlist(self.UDFS)))
            foo.sort()
            return foo
        #keys of the grouped UDFs
        elif (mytype == GROUP):
            return self.GroupedUDFs.keys()
        #keys of the merged UDF
        elif (mytype == MERGE):
            return self.CleanedUDFs.keys() 
     
    #merging/grouping UDFS
    def tidyUDF(self, key, text, mytype):
        #group UDF contains a dictionary of merged UDF's
        if (mytype == "group"):
            if key not in self.GroupedUDFs:
                self.GroupedUDFs[key] = []               
            self.GroupedUDFs[key].append(text)
        #for merged UDF it contains a dictionary of all UDF's that get merged into 1
        #key is how to refer to the merger and the value is a list of all UDF's that it contains
        elif (mytype == "merge"):
            if key not in self.CleanedUDFs:
                self.CleanedUDFs[key] = []   
            self.CleanedUDFs[key].append(text)
    
    #deleting UDF's
    def removeUDF(self, key, mytype):
        if (mytype == "group"):
            self.GroupedUDFs.pop(key, None)
        #WARNING!!!!
        #need to make sure no group UDF's used the deleted merge UDF
        elif (mytype):
            self.CleanedUDFs.pop(key, None)    
    
    def getUDF(self, key, mytype):
        if (mytype == "group"):
            return self.GroupedUDFs[key]
        elif (mytype == "merge"):
            return self.CleanedUDFs[key]   
    
    #make sure a name doesn't exist in the UDF's or the dataframe  
    def checkname(self, mytype, name):
        mydict = self.getUDFS(mytype)
        if name in mydict or name in self.dataFilByEvent.columns.tolist():
            return False
        return True
        
        
    #getting the dataset ready for analysing by splitting it into
    #donations
    #fundraisers
    #teams        
    #DON'T OVERWRITE THE ORIGINAL DATASET!!!!!
    def getready(self):
        if not self.ready:
            self.filterbyevent()
            if self.depthLevel == COMBINED:
                self.dataFilByEvent["Event ID"] = "combined"
            
            #if I flatten the locations I now apply that change to the dataset
            if self.changelocations:
                self.dataFilByEvent["Location Name"] = self.dataFilByEvent["Location Name"].apply(lambda x: self.changeplaces(self.orglocations.index(x))) 
                
            #for CCA "verified" values       
            #self.dataFilByEvent = self.dataFilByEvent[(self.dataFilByEvent['Transaction Source'] != "Import") &\
            #                                (self.dataFilByEvent['Transaction Source'] != "Data Entry")]
            
                            
            self.donations = self.dataFilByEvent[(self.dataFilByEvent["Transaction Type"] != "Registration")]  
            self.donations = self.donations[["Transaction Type", "Donation Type", "Constituent ID", \
                                             "Location Name", "Donation Datetime", "Event ID", \
                                             "Donation Amount", "Solicitor First Name", "Solicitor Last Name", \
                                             "Solicitor ID", "Donation Date", "Donation Time", "Payment Status", \
                                             "TeamID","Transaction Source","PaymentVerification","URL Referrer", \
                                             "Mobile Donation","Facebook FPF Donation", "Email Address", \
                                             "First Name", "Last Name", "Solicited Donation", "Corporate Team Name"]]
                       
            
            #self.donations[self.donations["URL Referrer"].isnull()] = "UNKNOWN"
            self.donations.loc[self.donations["URL Referrer"].isnull(), "URL Referrer"] = ("UNKNOWN")
            self.donations.loc[self.donations["Transaction Source"] == 'Import', 'Payment Status'] = 'Succeeded'
            
            #mydons = mydons[mydons["Solicitor ID"].notnull()]
            #recombine team donations
            
            foo = flattenlist(self.CleanedUDFs.values())
            #getting UDF's for selected events
            self.UDFdf = self.dataFilByEvent.loc[self.dataFilByEvent["Transaction Type"] == "Registration",["Constituent ID", "Event ID"] +foo] 
            self.UDFdf = convertupper(self.UDFdf, foo)
                  
            if self.RecombineTeams:
                dons = self.donations
                #recombine split teams
                teamsplits = self.donations[self.donations["Solicited Donation"] == "Team Split"].groupby(["Event ID", "Constituent ID"])["Donation Amount"].sum()
                teamsplits = teamsplits.reset_index()
                teamsplits["Solicited Donation"] = "Team Split"
                teamsplits = teamsplits.set_index(["Event ID", "Constituent ID", "Solicited Donation"])
                
                #update only the split team amounts
                dons = dons.set_index(["Event ID", "Constituent ID", "Solicited Donation"])
                dons.update(teamsplits)
                dons = dons.reset_index()
                
                #get unique for the split teams
                foo = dons[dons["Solicited Donation"] == "Team Split"]
                foo = foo.drop_duplicates(subset=['Event ID', "Constituent ID"], keep='last')
                
                #only keep a unique split team donation and make them look like a team doantion
                dons = dons[dons["Solicited Donation"] != "Team Split"]
                dons = dons.append(foo)
                dons.loc[dons["Solicited Donation"] == "Team Split", ["Solicitor First Name", "Solicitor Last Name", "Solicitor ID"]] = np.NaN
                self.donations = dons

            #finding some donation info like typology of entity that recvieved the donations
            self.donations["Typology"] = ""
            self.donations.loc[self.donations["Solicitor ID"].notnull() & self.donations["TeamID"].notnull(), "Typology"] = "team_member"
            self.donations.loc[self.donations["Solicitor ID"].notnull() & self.donations["TeamID"].isnull(), "Typology"] = "Individual"
            
            self.donations.loc[self.donations["Solicitor ID"].isnull() & self.donations["TeamID"].notnull(), "Typology"] = "Team"     
            
            self.donations.loc[self.donations["Solicitor ID"].isnull() & 
                               self.donations["TeamID"].isnull() &
                               self.donations["Corporate Team Name"].notnull(), "Typology"] = "Corporate Team"
                                           
            self.donations.loc[self.donations["Solicitor ID"].isnull() & 
                               self.donations["TeamID"].isnull() &
                               self.donations["Corporate Team Name"].isnull(), "Typology"] = "Unsolicited"
            
            #fundraiser info
            self.fundraisers = self.dataFilByEvent.loc[self.dataFilByEvent["Transaction Type"] == "Registration", \
                                                       ["Registration Date", "Transaction Source", "Constituent ID", \
                                                        "Event ID", "Email Address", "First Name", "Last Name", \
                                                        "Postal Code", "Location Name", "Location Type ID", "TeamID", "Facebook Connect", \
                                                        "Mobile App", "Participant Goal", 'Registration Status', \
                                                        'Registration Type', 'Registration Fee Status', 'Coupon Code', \
                                                        'Net Reg Fee Amount', 'Registered By', 'iPhone', 'Android', \
                                                        'Mobile Web', "Big Browser", 'Login', "Corporate Team Name", "Personal Page Message"]]
            #self.fundraisers = self.fundraisers.dropna(axis=1,how='all')
            self.fundraisers["FSA"] = self.fundraisers["Postal Code"].map(lambda x: str(x)[:3])
            #putting mobile data
            def changeApp(x):
                mw = False
                app = False
                for mystr in x.split(';'):
                    mystr = mystr.strip()
                    if mystr == "IPHONE" or mystr == "ANDROID":
                        app = True
                    elif mystr == "MOBILE WEB":
                        mw = True
                if app and mw:
                    return "APP & MOBILE WEB"
                elif app:
                    return "APP Only"
                elif mw:
                    return "MOBILE WEB"
                else:
                    return x
            
            
            self.fundraisers["apps"] = self.fundraisers["Mobile App"]
            self.fundraisers["Mobile App"] = self.fundraisers["Mobile App"].fillna("None")
            self.fundraisers["Mobile App"] = self.fundraisers["Mobile App"].apply(lambda row: changeApp(row))
            
                    
            #finding fundraiser team size for those on a team
            self.fundraisers["TeamID"] = self.fundraisers["TeamID"].fillna(-1)
            #self.fundraisers = self.fundraisers.merge(pd.DataFrame({'Team Size':self.fundraisers.groupby(['Event ID', 'TeamID']).size()}), left_on=['Event ID', 'TeamID'], right_index=True)
            self.fundraisers["Team Size"] = self.fundraisers.groupby(['Event ID', 'TeamID'])["Constituent ID"].transform('count')
            self.fundraisers.loc[self.fundraisers["TeamID"] == -1, "Team Size"] = 0
            self.fundraisers["Team"] = "Individual"
            self.fundraisers.loc[self.fundraisers["Team Size"] >0, "Team"] = "team_member"
            #calculating how much the fundraiser raised
            self.fundraisers =  self.fundraisers.set_index(['Event ID', 'Constituent ID'])
            self.fundraisers["ver raised"] = self.donations[self.donations["Payment Status"] == "Succeeded"].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].sum()
            self.fundraisers["ver sponsors"] = self.donations[self.donations["Payment Status"] == "Succeeded"].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].count()
            self.fundraisers["pledges"] = self.donations[pd.isnull(self.donations["Payment Status"])].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].sum()
            self.fundraisers["pledges sponsors"] = self.donations[pd.isnull(self.donations["Payment Status"])].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].count()
			
            #self.fundraisers["ABMT"] = self.donations[pd.isnull(self.donations["Payment Status"]) | (self.donations["PaymentVerification"] == "OfflinePaidIn")].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].sum()
            #self.fundraisers["ABMT sponsors"] = self.donations[pd.isnull(self.donations["Payment Status"]) | (self.donations["PaymentVerification"] == "OfflinePaidIn")].groupby(["Event ID", "Solicitor ID"])["Donation Amount"].count()
            #self.fundraisers["ABMT"] = self.fundraisers["ABMT"].fillna(0)
            #self.fundraisers["ABMT sponsors"] = self.fundraisers["ABMT sponsors"].fillna(0)
            
            self.fundraisers["total"] = self.fundraisers["ver raised"] + self.fundraisers["pledges"]
            self.fundraisers["total sponsors"] = self.fundraisers["ver sponsors"] + self.fundraisers["pledges sponsors"]
            self.fundraisers["pledges"] = self.fundraisers["pledges"].fillna(0) 
            self.fundraisers["pledges sponsors"] = self.fundraisers["pledges sponsors"].fillna(0) 
            self.fundraisers["ver raised"] = self.fundraisers["ver raised"].fillna(0) 
            self.fundraisers["ver sponsors"] = self.fundraisers["ver sponsors"].fillna(0) 
            self.fundraisers["total"] = self.fundraisers["total"].fillna(0) 
            self.fundraisers["total sponsors"] = self.fundraisers["total sponsors"].fillna(0)
            self.fundraisers["Week"] = self.fundraisers["Registration Date"].apply(lambda x: x + datetime.timedelta(days=-x.weekday()))
            self.fundraisers["Week"] = self.fundraisers["Week"].apply(lambda x: x.isocalendar()[1])
        
            #Team info
            self.teams = self.dataFilByEvent.loc[self.dataFilByEvent["Transaction Type"] == "Registration", ["Event ID", "TeamID", "Team Captain ID", "Team Name", "Corporate Team Name"]]
            self.teams = self.teams.dropna(subset=[["TeamID"]])         
            try:
                teamsizeDF = pd.DataFrame({'Team Size':self.teams.groupby(['Event ID', 'TeamID']).size()})
                self.teams = self.teams.merge(teamsizeDF, left_on=['Event ID', 'TeamID'], right_index=True)
            except:
                self.teams['Team Size'] = 0
            self.teams = self.teams.drop_duplicates()
            self.teams = self.teams.set_index(['Event ID', 'TeamID'])         
            self.teams["team ver raised"] = self.donations[(self.donations["Payment Status"] == "Succeeded") & (pd.isnull(self.donations["Solicitor ID"]))].groupby(['Event ID', "TeamID"])["Donation Amount"].sum()
            self.teams["team ver sponsors"] = self.donations[(self.donations["Payment Status"] == "Succeeded") & (pd.isnull(self.donations["Solicitor ID"]))].groupby(['Event ID', "TeamID"])["Donation Amount"].count()
            self.teams["team pledges"] = self.donations[(pd.isnull(self.donations["Payment Status"])) & (pd.isnull(self.donations["Solicitor ID"]))].groupby(['Event ID', "TeamID"])["Donation Amount"].sum()
            self.teams["team pledges sponsors"] = self.donations[(pd.isnull(self.donations["Payment Status"])) & (pd.isnull(self.donations["Solicitor ID"]))].groupby(['Event ID', "TeamID"])["Donation Amount"].count()
            self.teams["team pledges sponsors"] =  self.teams["team pledges sponsors"].fillna(0)
            self.teams["team pledges"] = self.teams["team pledges"].fillna(0)  
            self.teams["team ver raised"] = self.teams["team ver raised"].fillna(0)
            self.teams["team ver sponsors"] = self.teams["team ver sponsors"].fillna(0) 
            self.teams["total"] =  self.teams["team ver raised"] + self.teams["team pledges"]
            
            
            self.fundraisers = self.fundraisers.reset_index()
            self.teams = self.teams.reset_index()
            #putting team amounts of team of 1 as personal amount for fundraisers
            if (not(self.TeamsOfOne)):
                #self.fundraisers["Team"][self.fundraisers["Team Size"] ==1] = "Individual"
                self.fundraisers.loc[self.fundraisers["Team Size"] ==1, "Team"] = "Individual"
                self.fundraisers = pd.merge(self.fundraisers,  pd.DataFrame(self.teams[["Event ID", "TeamID", "team ver raised","team ver sponsors", "team pledges", "team pledges sponsors"]]), left_on=['Event ID', 'TeamID'],  right_on=["Event ID","TeamID"], how='outer')
                
                self.fundraisers["ver raised"] = self.fundraisers.apply(lambda row: (row["ver raised"] + row["team ver raised"] 
                                                                                     if row["Team Size"] == 1 else row["ver raised"]), 
                                                                                     axis=1)
    
                self.fundraisers["ver sponsors"] = self.fundraisers.apply(lambda row: (row["ver sponsors"] + row["team ver sponsors"] 
                                                                                     if row["Team Size"] == 1 else row["ver sponsors"]), 
                                                                                     axis=1)
                
                self.fundraisers["pledges"] = self.fundraisers.apply(lambda row: (row["pledges"] + row["team pledges"] 
                                                                    if row["Team Size"] == 1 else row["pledges"]),
                                                                    axis=1)
                
                self.fundraisers["pledges sponsors"] = self.fundraisers.apply(lambda row: (row["pledges sponsors"] + row["team pledges sponsors"] 
                                                                                     if row["Team Size"] == 1 else row["pledges sponsors"]), 
                                                                                     axis=1)
                                            
                self.fundraisers = self.fundraisers.drop(['team ver raised', 'team ver sponsors', "team pledges"],1)
                self.fundraisers["total"] = self.fundraisers["ver raised"] + self.fundraisers["pledges"]
                self.fundraisers["total"] = self.fundraisers["total"].fillna(0)
                self.fundraisers["total sponsors"] = self.fundraisers["ver sponsors"] + self.fundraisers["pledges sponsors"]
                self.fundraisers["total sponsors"] = self.fundraisers["ver sponsors"].fillna(0)
                self.teams.loc[self.teams["Team Size"] == 1, ["team ver raised", "team ver sponsors", "team pledges", "team pledges sponsors", "total"]] = 0

                self.ready = True
    
    def donationoptions(self, options):
        if options == "Verified":
            mydons = self.donations[self.donations["Payment Status"] == "Succeeded"]
        elif options == "Pledges":
            mydons = self.donations[pd.isnull(self.donations["Payment Status"])]
        elif options == "Online":
            mydons = self.donations[(self.donations["Payment Status"] == "Succeeded") &\
                                    (self.donations["Donation Type"] == "Online") &\
                                    (self.donations["Mobile Donation"] == "No")]
        elif options == "Mobile":
            mydons = self.donations[(self.donations["Payment Status"] == "Succeeded") & \
                                    (self.donations["Mobile Donation"] == "Yes")]
        elif options == "Facebook":
            mydons = self.donations[(self.donations["Payment Status"] == "Succeeded") & \
                                    ((self.donations["Facebook FPF Donation"] == "Yes") | \
                                    (self.donations["URL Referrer"].str.contains("FACEBOOK")))]     
        elif options == "Paidins":
            mydons = self.donations[self.donations["PaymentVerification"] == "OfflinePaidIn"]          
        elif options == 'orgs':
            mydons = self.donations[(self.donations["Payment Status"] == "Succeeded") & \
                                    (self.donations["Transaction Type"] == "Organization Donation")]            
        else:
            mydons = self.donations[self.donations["Payment Status"] != "Pending"]
        return mydons
    
    def fundraiseroptions(self, options, active):
        if options == "Verified":
            if active:
                foo = self.fundraisers[self.fundraisers["ver raised"] > 0]
            else:
                foo = self.fundraisers[self.fundraisers["ver raised"] == 0]
        elif options == "Pledges":
            if active:
                foo = self.fundraisers[self.fundraisers["pledges"] > 0]
            else:
                foo = self.fundraisers[self.fundraisers["pledges"] == 0]
        else:
            if active:
                foo = self.fundraisers[self.fundraisers["total"] > 0]
            else:
                foo = self.fundraisers[self.fundraisers["total"] == 0]
        return foo    
                  
    def run(self, report, outputs, options = "None"):            
        #make sure events are selected
        if self.events and len(outputs) > 1:
            if report == "Active Users" :
                self.findactives(outputs, options)
            elif (report == "Donations"):
                self.findDonationStats(outputs, options)
            elif (report == "Histogram"):
                self.findHistogram(outputs, options)
            elif (report == "Self Sponsors"):
                self.findSelfSponsors(outputs, options)
            elif (report == "Growth") and (len(self.events) > 1):
                self.findGrowth(outputs, options)
            elif (report == "Locations"):
                self.findLocations(outputs, options)
            elif (report == "Returning Users") and (len(self.events) > 1):
                self.findReturnUsers(outputs, options)    
            elif (report == "Donation Timeline"):
                self.findDonationTimeline(outputs, options)  
            elif (report == "Registrant Timeline"):
                self.findRegTimeline(outputs, options) 
            elif (report == "Fundraised by Typology"):
                self.findFunTyp(outputs, options)             
            elif (report == "Team Details"):
                self.findTeamSizes(outputs, options)
            elif (report == "Social Media"):
                self.findSocialMedia(outputs, options)
            elif (report == "Mobile"):
                self.findmobile(outputs, options)
            elif (report == "Goal"):
                self.findgoal(outputs, options)
            elif (report == "UDF Fundraisers"):
                self.findUDF(outputs, options)
            elif (report == "Summary"):
                self.findEventSummary(outputs, options) 
            elif (report == "Reg Fee"):
                self.findRegFee(outputs, options)
            elif (report == "Mapping"):
                self.findmap(outputs, options)
            elif (report == 'Proxy'):
                self.findproxies(outputs, options)
            elif (report == 'Signups'):
                self.findSignups(outputs, options)
            elif (report == "Corporate teams"):
                self.findCorporate(outputs, options)
    
    def findCorporate(self, outputs, options):
        title = maketitle("Corporate ", options)
        
        if "Corporate Team Name" not in self.fundraisers:
            print "No corporate teams to report on"
            return
            
        corporate1 = self.fundraisers.loc[self.fundraisers["Corporate Team Name"].notnull(), ["Event ID", 'Corporate Team Name', "Constituent ID", "TeamID", 'ver raised', 'ver sponsors', 'pledges', 'pledges sponsors']]
        
        corporate2 = self.teams.loc[self.teams["Corporate Team Name"].notnull(), ["Event ID", "Corporate Team Name", "TeamID", 'team ver raised', 'team ver sponsors', 'team pledges', 'team pledges sponsors']]
        corporate2 = corporate2.rename(columns={'team ver raised': 'ver raised',
                                                'team ver sponsors':'ver sponsors',
                                                'team pledges':'pledges',
                                                'team pledges sponsors':'pledges sponsors'})
        
        corporate3 = self.fundraisers[self.fundraisers["Corporate Team Name"].notnull()][["Event ID", "Corporate Team Name"]]
        corporate3 = corporate3.drop_duplicates()
        corporate3 = corporate3.set_index(['Event ID', "Corporate Team Name"]) 
        donations = self.donationoptions("Verified")    
        corporate3["ver raised"] = donations[donations["Typology"] == "Corporate Team"].groupby(["Event ID", "Corporate Team Name"])["Donation Amount"].sum()
        corporate3["ver sponsors"] = donations[donations["Typology"] == "Corporate Team"].groupby(["Event ID", "Corporate Team Name"])["Donation Amount"].count()
        donations = self.donationoptions("Pledges")
        corporate3["pledges"] = donations[donations["Typology"] == "Corporate Team"].groupby(["Event ID", "Corporate Team Name"])["Donation Amount"].sum()
        corporate3["pledges sponsors"] = donations[donations["Typology"] == "Corporate Team"].groupby(["Event ID", "Corporate Team Name"])["Donation Amount"].count()
        for col in ["ver raised", "ver sponsors", "pledges", "pledges sponsors"]:
            corporate3[col] = corporate3[col].fillna(0)
        corporate3 = corporate3.reset_index()
        
        corporateDF = pd.concat([corporate1,corporate2,corporate3])
        corporateDF = corporateDF.sort_values(by=['Event ID', "Corporate Team Name"])
                      
        if outputs[SUMMARY]:
            mycol = "ver raised"
            if options <> "Verified":
                mycol = "pledges"  
            corp = corporateDF[["Event ID", "Corporate Team Name"]]
            corp = corp.drop_duplicates()
            corp = corp.set_index(['Event ID', "Corporate Team Name"]) 
            corp["team_members Raised"] = corporateDF[corporateDF["Constituent ID"].notnull()].groupby(["Event ID", "Corporate Team Name"])[mycol].sum()
            corp["Teams Raised"] = corporateDF[(corporateDF["Constituent ID"].isnull()) & (corporateDF["TeamID"].notnull())].groupby(["Event ID", "Corporate Team Name"])[mycol].sum()
            corp["Teams Raised"] = corp["Teams Raised"].fillna(0)
            corp["Corporate Raised"] = corporateDF[(corporateDF["Constituent ID"].isnull()) & (corporateDF["TeamID"].isnull())].groupby(["Event ID", "Corporate Team Name"])[mycol].sum()
            corp["Corporate Raised"] = corp["Corporate Raised"].fillna(0)
            corp["Num People"] = corporateDF.groupby(["Event ID", "Corporate Team Name"])["Constituent ID"].count()
            try:
				corp["Num Teams"] = corporateDF[corporateDF["TeamID"] != -1].groupby(["Event ID", "Corporate Team Name"])["TeamID"].nunique()
            except:
				pass
			#corp.head()
            self.outputs(corp, title, {SUMMARY: True})          
        if outputs[EXCEL] or outputs[CSV]:

            if outputs[EXCEL]:
                self.outputs(corporateDF, title, {EXCEL: True})  
            if outputs[CSV]:
                self.outputs(corporateDF, title, {CSV: True})
        
    def findSignups(self, outputs, options):
        title = maketitle("Sign Ups ", options)
        regs = self.fundraisers[self.fundraisers["Transaction Source"] == "Online"]
        regs = regs.groupby(self.depth())["Constituent ID"].count()     
        self.outputs(regs, title, outputs) 
    
    def findproxies(self, outputs, options):
        df = self.fundraisers
        df["Proxies"] = False
        df["Data Entry"] = False
        #df.loc[df["Registered By"].notnull(), "Proxies"] = True
        regothers = df.loc[df["Registered By"].notnull(), ["Registered By", "Event ID"]]
        regothers = regothers.drop_duplicates()
        regbyIDS = set(regothers["Registered By"].tolist())
        missingsIDS = regbyIDS - set(df["Constituent ID"].tolist())
        goodIDS = list(regbyIDS - missingsIDS)
        df["Registered Others"] = False
        df.loc[df["Constituent ID"].isin(goodIDS), "Registered Others"] = True
        df.loc[df["Registered By"].isin(goodIDS), "Proxies"] = True
        df.loc[df["Registered By"].isin(missingsIDS), "Data Entry"] = True
        #regothers = regothers[regothers["Registered By"].isin(goodIDS)]
        
        #regothers["Registered Other"] = True
        #regothers = regothers.rename(columns={'Registered By': 'Constituent ID'})
        #df["Registered Other"] = False
        #df["Registered Other"] = regothers.set_index(["Event ID", "Constituent ID"])["Registered Other"].combine_first(df.set_index(["Event ID", "Constituent ID"])["Registered Other"]).values
                                #df2.set_index(['c1','c2'])['val'].combine_first(df1.set_index(['c1','c2'])['val']).values
        title = maketitle("Proxies ", options)  
        if outputs[SUMMARY]:  
            stats = df[df["ver sponsors"] > 0].groupby(self.depth() + [options])[["ver raised", "ver sponsors"]].agg(['mean', 'median', 'sum'])  
            stats["Registrants"] = df.groupby(self.depth() + [options])["Constituent ID"].count()  
            stats["Active"] = df[df["ver sponsors"] > 0].groupby(self.depth() + [options])["Constituent ID"].count()  
            stats["Percent Active"] = df.groupby(self.depth() + [options]).apply(lambda x: x[x["ver sponsors"] >0].count() / len(x))["Constituent ID"]
            
            #stats["sponsors_mean"]= df.groupby(["Event ID", options])["ver sponsors"].agg(['mean', 'median', 'count', 'sum'])  
            self.outputs(stats, title, {SUMMARY: True})          
        if outputs[EXCEL] or outputs[CSV]:
            stats = self.fundraisers[['Event ID', 'Constituent ID', "Registered By", "ver raised", "ver sponsors", \
                                      "Proxies", "Data Entry", "Registered Others"]]
            if outputs[EXCEL]:
                self.outputs(stats, title, {EXCEL: True})  
            if outputs[CSV]:
                self.outputs(stats, title, {CSV: True})     
        
    
    def findmap(self, outputs, options):
        title = maketitle("Map", options)           
        stats = pd.DataFrame()
        if options == "Canada":
            postaltype = "FSA"
        else:
            postaltype = "Postal Code"
        stats["Registrants"] =  self.fundraisers.groupby([postaltype, "Event ID"])["Constituent ID"].count()
        stats["Raised"] = self.fundraisers.groupby([postaltype, "Event ID"])["ver raised"].sum()
        stats = stats.unstack("Event ID")
        self.outputs(stats, title, outputs) 
        
    
    def findRegFee(self, outputs, options):
        if outputs[SUMMARY]:  
            stats = pd.DataFrame()
            stats["Registrants"] =  self.fundraisers.groupby(self.depth() + ['Registration Status', 'Registration Type', 'Registration Fee Status'])["Constituent ID"].count()
            stats["Fee Collected"] = self.fundraisers.groupby(self.depth() + ['Registration Status', 'Registration Type', 'Registration Fee Status'])["Net Reg Fee Amount"].sum()
            self.outputs(stats, "Reg Fee", {SUMMARY: True})
            
            if 'Coupon Code' not in self.fundraisers:
                print "No coupons used"
                return
            
            stats = self.fundraisers.groupby(self.depth() + ['Coupon Code'])["Constituent ID"].count()
            self.outputs(stats, "Coupons Used", {SUMMARY: True})
            
        if outputs[EXCEL] or outputs[CSV]:
            stats = self.fundraisers[['Event ID', 'Constituent ID', 'Registration Status', 'Registration Type', \
                                      'Registration Fee Status', 'Coupon Code', 'Net Reg Fee Amount']]
            if outputs[EXCEL]:
                self.outputs(stats, "Reg Fee", {EXCEL: True})  
            if outputs[CSV]:
                self.outputs(stats, "Reg Fee", {CSV: True})              
            
                    
    def findEventSummary(self, outputs, options):
        stats = pd.DataFrame()
        
        stats["Registrants"] = self.fundraisers.groupby("Event ID")["Constituent ID"].count()
        stats["Teams"] = self.fundraisers[self.fundraisers["TeamID"] != -1].groupby(["Event ID"])["TeamID"].nunique()
        stats["Verified Amount"] = self.donationoptions("Verified").groupby("Event ID")["Donation Amount"].sum()  
        stats["Pledges"] = self.donationoptions("Pledges").groupby("Event ID")["Donation Amount"].sum()
        stats["Total"] = stats["Verified Amount"] + stats["Pledges"]
        
        title = "Event Summary"
        self.outputs(stats, title, outputs)        
        
    
    def findUDF(self, outputs, options):
        if (options != ""):
            title = maketitle("F UDF ", options)  
            fundUDF = self.fundraisers.merge(self.UDFdf, left_on=["Event ID", "Constituent ID"], right_on=["Event ID", "Constituent ID"])
            udfs = ["Event ID"]
            #fundUDF["dup"] = False
            #fundUDF["offset"] = 1.
            
            def sjoin(x, offset, key): 
                if len(x.dropna()) == 0:
                    return pd.Series({key: "Unknown", 'offset': offset})
                elif len(x.dropna()) == 1:
                    return pd.Series({key: ';'.join(x[x.notnull()].astype(str)), 'offset': offset})
                else:
                    return pd.Series({key: ';'.join(x[x.notnull()].astype(str)), 'offset': offset / len(x.dropna())})
               
            def concat(*args):
                strs = [str(arg) for arg in args if not pd.isnull(arg) and arg]
                return ';'.join(strs) if strs else ""  
            #np_concat = np.vectorize(concat)             
                #else:
                #    return ';'.join(x[x.notnull()].astype(str))
            
            if options.split(" ")[0] == "merge":
                udfs.append(options.split(" ")[1])
                filtered_dict = {k:v for (k,v) in self.CleanedUDFs.items() if options.split(" ")[1] in k}
            else:
                udfs.extend(self.GroupedUDFs[options.split(" ")[1]])
                filtered_dict = {k:v for (k,v) in self.CleanedUDFs.items() if k in self.GroupedUDFs[options.split(" ")[1]]}
                  
            #t0 = time.time()  
            #for key, value in filtered_dict.iteritems():
            #    fundUDF[[key, "offset"]] = fundUDF[value + ["offset"]].apply(lambda row: sjoin(row[:-1], row.offset, key), axis=1)
            #    s = fundUDF[key].str.split(';').apply(pd.Series, 1).stack()
            #    s.index = s.index.droplevel(-1) # to line up with df's index
            #    s.name = key # needs a name to join
            #    del fundUDF[key]
            #    fundUDF = fundUDF.join(s)
            #    fundUDF.loc[fundUDF["offset"] != 1, "dup"] = True   
            #    fundUDF["ver raised"] = fundUDF["ver raised"] * fundUDF["offset"]     
            #t1 = time.time()
            #print t1-t0
            #t0 = time.time()  
            #for key, value in filtered_dict.iteritems():
            #    fundUDF[key] = ""
            #    for myvalue in value:
            #        fundUDF[key] = np_concat(fundUDF[key], fundUDF[myvalue])
            #    s = fundUDF[key].str.split(';').apply(pd.Series, 1).stack()
            #    s.index = s.index.droplevel(-1) # to line up with df's index
            #    s.name = key # needs a name to join
            #    del fundUDF[key]
            #    fundUDF = fundUDF.join(s)
            #    fundUDF = fundUDF.drop_duplicates()
            #    fundUDF["ver raised2"] = fundUDF.groupby(["Event ID", "Constituent ID"])["ver raised"].apply(lambda x: x / len(x))
            #t1 = time.time()
            #print t1-t0
            #t0 = time.time()  
            
            #if a user selected multiple options for a UDF I want to spli that user between both options (so create new rows so each is unique, but the total is the same)
            for key, value in filtered_dict.iteritems():      
                #melting data so each UDF answer is it's own row           
                foo = pd.melt(fundUDF, id_vars=["Event ID", "Constituent ID"], value_vars=value, var_name=key)
                #getting ready of unanswered rows
                foo = foo.dropna(how='all', subset=[["value"]])
                #getting ride of excess columns
                del foo[key]
                foo = foo.rename(columns={'value': key})
                #adding UDF's per registrant back to the fundraising dataframe
                fundUDF = fundUDF.merge(foo, how='left',right_on=["Event ID", "Constituent ID"], left_on=["Event ID", "Constituent ID"])
                fundUDF[key] = fundUDF[key].fillna("Unknown") 
            fundUDF = fundUDF.drop_duplicates()
            #for each duplicate split the users status and amount raised evenly across all rows (that will keep the totals the same)
            
            for col in ['ver raised', 'ver sponsors', 
                        'pledges', 'pledges sponsors', 
                        'total', 'total sponsors']:
                fundUDF[col] = fundUDF.groupby(["Event ID", "Constituent ID"])[col].apply(lambda x: x / len(x))
            fundUDF["people"] = fundUDF.groupby(["Event ID", "Constituent ID"])["ver raised"].transform(lambda x: 1. / len(x))
            #t1 = time.time()
            #print t1-t0
            
            if outputs[SUMMARY]:
                stats = fundUDF[fundUDF["ver raised"]>0].groupby(udfs)["ver raised"].agg(['mean', 'median', 'sum'])
                stats["mode"] = fundUDF[fundUDF["ver raised"]>0].groupby(udfs)["ver raised"].agg(lambda x:x.value_counts().index[0]) 
                stats["registrants"] = fundUDF.groupby(udfs)["people"].sum()
                stats["fundraisers"] = fundUDF[fundUDF["ver raised"]>0].groupby(udfs)["people"].sum()
                stats["ratio"] = 100 * stats["fundraisers"].astype(float) / stats["registrants"].astype(float)
                self.outputs(stats, title, {SUMMARY: True})
            if outputs[EXCEL]:
                self.outputs(fundUDF, title, {EXCEL: True})
            if outputs[GRAPH]:
                f,ax = plt.subplots(1,figsize=(7,7))
                gap = 0.05
                #MosaicPlot(Counter(list(self.fundraisers.loc[self.fundraisers["Event ID"] != "WALK12", ['Event ID', 'gender', 'age']].itertuples(index=False))),ax=ax,gap=gap,direction='v')
                foo = fundUDF.groupby(udfs)["Constituent ID"].count()
                #foo = self.fundraisers.loc[self.fundraisers["Event ID"] != "WALK12"].groupby(['Event ID', 'gender', 'age'])["Constituent ID"].count()
                MosaicPlot(dict(foo),ax=ax,gap=gap,direction='v')
                #mosaic(self.fundraisers, ['Event ID', 'age', 'gender'])
                #plt.show()
                df = fundUDF[["ver raised", "ver sponsors"] + udfs]
                groups = df.groupby(udfs)
                
                # Plot
                plt.rcParams.update(pd.tools.plotting.mpl_stylesheet)
                colors = pd.tools.plotting._get_standard_colors(len(groups), color_type='random')
                
                fig, ax = plt.subplots()
                plt.xlabel('Donors')
                plt.ylabel('Amount Raised')
                plt.title('Donors vs Amount Raised by ' + ', '.join(udfs))
                ax.set_color_cycle(colors)
                ax.margins(0.05)
                for name, group in groups:
                    ax.plot(group["ver sponsors"], group["ver raised"], marker='o', linestyle='', ms=7, label=name)#, alpha =0.5)
                # Shrink current axis's height by 10% on the bottom
                box = ax.get_position()
                ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width, box.height * 0.9])
                
                # Put a legend below current axis
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                          fancybox=True, shadow=True, ncol=3)   
                plt.show(block=False)
            if outputs[CSV]:
                self.outputs(fundUDF, title, {CSV: True})
        

        
    def findgoal(self, outputs, options):
        title = maketitle("Goal", options)           
        if outputs[SUMMARY]:  
            stats = pd.DataFrame()

            stats = self.fundraisers.groupby(self.depth())["Participant Goal"].agg(['mean', 'median'])
            stats = stats.rename(columns={'mean': 'Goal Mean', 'median': 'Goal Median'})
            stats["Goal Mode"] = self.fundraisers.groupby(self.depth())["Participant Goal"].agg(lambda x:x.value_counts().index[0])
            stats["Goal 2 Mode"] = self.fundraisers.groupby(self.depth())["Participant Goal"].agg(lambda x:x.value_counts().index[1])
            stats["Goal 3 Mode"] = self.fundraisers.groupby(self.depth())["Participant Goal"].agg(lambda x:x.value_counts().index[2])
            
            stats["No Goal"] = self.fundraisers[self.fundraisers["Participant Goal"]==0].groupby(self.depth())["Constituent ID"].count()
            stats["Set Goal"] = self.fundraisers[self.fundraisers["Participant Goal"]>0].groupby(self.depth())["Constituent ID"].count()
            
            if (options == "Verified"):       
                stats["Completed Goal"] = self.fundraisers[((self.fundraisers["Participant Goal"]>0) & (self.fundraisers["ver raised"]>self.fundraisers["Participant Goal"]))].groupby(self.depth())["Constituent ID"].count()
            else:
                stats["Completed Goal"] = self.fundraisers[((self.fundraisers["Participant Goal"]>0) & (self.fundraisers["total"]>self.fundraisers["Participant Goal"]))].groupby(self.depth())["Constituent ID"].count()
            stats["ratio"] = 100*(stats["Completed Goal"] / stats["Set Goal"])
            self.outputs(stats, title, {SUMMARY: True})            
        if outputs[EXCEL]:
            self.outputs(self.fundraisers, title, {EXCEL: True})  
        #if outputs[GRAPH]:
        #    myY = "ver raised"
        #    if (options != "Verified"):  
        #        myY='total'
        #    plt.figure()
        #    for i, group in self.fundraisers.groupby(self.depth()):         
        #        mytitle = title + " for " + str(i)
        #        model = sm.OLS(group[myY], group["Participant Goal"])
        #        fitted = model.fit()
        #        self.output.set(fitted.summary(), "OLS regression report for {}".format(str(i)))
        #        group.plot(kind='scatter', x="Participant Goal", y=myY, title=mytitle)
        #        plt.plot(group["Participant Goal"], fitted.fittedvalues, 'b')
                
        #        plt.show(block=False) 
        if outputs[CSV]:
            self.outputs(self.fundraisers, title, {CSV: True})
            
    def findmobile(self, outputs, options):
        if (options == "Fundraisers"):
            df = self.fundraisers[self.fundraisers["ver raised"] >0]         
        else:
            df = self.fundraisers
        title = maketitle("App", options)           
        if outputs[SUMMARY]:  
            if (options == "Fundraisers"):
                stats = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])[["ver raised", "ver sponsors"]].agg(['mean', 'median', 'sum'])
                stats["mode raised"] = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])["ver raised"].agg(lambda x:x.value_counts().index[0])  
                stats["mode donations"] = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])["ver sponsors"].agg(lambda x:x.value_counts().index[0])
                stats["raised STD"] = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])["ver raised"].std()
                #stats["raised variance"] = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])["ver raised"].var()
                stats["num people"] = self.fundraisers[self.fundraisers["ver raised"] >0].groupby(self.depth() + ["Mobile App"])["Constituent ID"].count()          
            else:
                stats = self.fundraisers.groupby(self.depth() + ["Mobile App"])[["ver raised", "ver sponsors"]].agg(['mean', 'median', 'sum'])
                stats["mode raised"] = self.fundraisers.groupby(self.depth() + ["Mobile App"])["ver raised"].agg(lambda x:x.value_counts().index[0])  
                stats["mode donations"] = self.fundraisers.groupby(self.depth() + ["Mobile App"])["ver sponsors"].agg(lambda x:x.value_counts().index[0])
                stats["raised STD"] = self.fundraisers.groupby(self.depth() + ["Mobile App"])["ver raised"].std()
                #stats["raised variance"] = self.fundraisers.groupby(self.depth() + ["Mobile App"])["ver raised"].var()
                stats["num people"] = self.fundraisers.groupby(self.depth() + ["Mobile App"])["Constituent ID"].count()   
            self.outputs(stats, title, {SUMMARY: True})  
            downloads = self.fundraisers[self.fundraisers["Mobile App"].notnull()].groupby(["Event ID", "apps"])["Constituent ID"].count()   
            self.outputs(downloads, "App Downloads", {SUMMARY: True})  
            cohens = {}
            stats = stats.reset_index()
            for appType in stats["Mobile App"].unique():
                #cohens[appType] = (stats.loc[stats["Mobile App"] == appType, "ver raised"]["mean"].values[0] - stats.loc[stats["Mobile App"] == 'None', "ver raised"]["mean"].values[0]) / ((stats.loc[stats["Mobile App"] == appType, "raised STD"].values[0] + stats.loc[stats["Mobile App"] == 'None', "raised STD"].values[0]) / 2)
                numerator = (stats.loc[stats["Mobile App"] == appType, "ver raised"]["mean"].values[0] - stats.loc[stats["Mobile App"] == 'None', "ver raised"]["mean"].values[0])
                s1 =  (stats.loc[stats["Mobile App"] == appType, "num people"].values[0]-1) * (stats.loc[stats["Mobile App"] == appType, "raised STD"].values[0]**2)
                s2 =  (stats.loc[stats["Mobile App"] == "None", "num people"].values[0]-1) * (stats.loc[stats["Mobile App"] == "None", "raised STD"].values[0]**2)
                s3 = stats.loc[stats["Mobile App"] == appType, "num people"].values[0] + stats.loc[stats["Mobile App"] == "None", "num people"].values[0] - 2
                denominator = ((s1 + s2) / s3) ** 0.5
                cohens[appType] = numerator / denominator
            self.outputs(cohens, "Cohen's D", {SUMMARY: True})  
            
        if outputs[EXCEL]:
            self.outputs(df, title, {EXCEL: True}) 
            #self.excelout.printexcel(self.outputfile, stats, title)
        if outputs[GRAPH]:  
            stats = df
            stats.boxplot(column=["ver raised"], by=["Event ID", "Mobile App"])
            #delete graph print if I fox the scatter plot
            plt.title(title)
            plt.show(block=False)  
            #counter = 1
            #not putting the scatter on the right boxplot, NEED TO FIX
            #for i in stats["Event ID"].unique():
            #    for k in stats.loc[stats["Event ID"] == i, "Mobile App"].unique():
            #        y = stats.loc[(stats["Event ID"] == i) & (stats["Mobile App"] == k), "ver raised"].dropna()
            #        foo = len(y)
            #        x = np.random.normal(counter, 0.04, size=foo)
            #        counter += 1
            #        plt.plot(x,y,'g.', alpha=0.2)  
            #        plt.title(title)
            #        plt.show(block=False) 
        if outputs[CSV]:
            self.outputs(df, title, {CSV: True})
        
        #fix graphs
        #self.outputs(stats, title, outputs)     
        
    
    def findSocialMedia(self, outputs, options):
        #myoptions = ["All", "Referral", "FPF", "Facebook Connect"]
        socialstats = self.fundraisers
        usedFB = []
        if (options == "All"):
            usedFB = self.findwhousedsocial("Referral")
            usedFB += self.findwhousedsocial("FPF")
            usedFB += self.findwhousedsocial("Facebook Connect")
        else:
            usedFB = self.findwhousedsocial(options)
        socialstats["Used_FB"] = False
        #socialstats.loc[self.fundraisers["Constituent ID"].isin(usedFB),"Used_FB"] = True
        socialstats.loc[np.in1d(self.fundraisers["Constituent ID"], usedFB),"Used_FB"] = True
        title = maketitle("SocialMedia", options)
        if outputs[SUMMARY]:
            foo = self.fundraiseroptions("Verified", True)
            mysummary = foo.groupby(self.depth() + ["Used_FB"])["ver raised"].agg(['mean', 'median', 'count', 'sum'])  
            mysummary["sponsors_mean"]= foo.groupby(self.depth() + ["Used_FB"])["ver sponsors"].mean(); 
            self.outputs(mysummary, title, {SUMMARY: True}) 
        if outputs[EXCEL]:
            #self.excelout.printexcel(self.outputfile, socialstats[["Event ID", "Constituent ID", "ver raised","pledges","total","Used_FB"]], maketitle("SocialMedia", options)) 
            self.outputs(socialstats[["Event ID", "Constituent ID", "ver raised","pledges","total","Used_FB"]], title, {EXCEL: True}) 
        if outputs[CSV]:
            self.outputs(socialstats[["Event ID", "Constituent ID", "ver raised","pledges","total","Used_FB"]], title, {CSV: True})
            
    def findwhousedsocial(self, option):
        people = []
        if (option == "Referral"):
            people = self.donations.loc[self.donations["URL Referrer"].str.contains("FACEBOOK"), "Solicitor ID"].unique().tolist()  
        elif (option == "FPF"):
            people = self.donations.loc[self.donations["Facebook FPF Donation"] == "Yes", "Solicitor ID"].unique().tolist()  
        elif (option == "Facebook Connect"):
            people = self.fundraisers.loc[self.fundraisers["Facebook Connect"] == "Yes", "Constituent ID"].tolist()     
        return people     
        
    def findTeamSizes(self, outputs, options):
        #for each team calculate sum of team_members
        teams = self.teams
        teams = teams.set_index(['Event ID', 'TeamID'])  
        teammembers = self.fundraisers.groupby(["Event ID", "TeamID"])["ver raised", "pledges", "ver sponsors", "pledges sponsors"].sum()
        teams = pd.merge(teams, teammembers, how='left', left_index=True, right_index=True)
        captains = self.fundraisers[["Event ID", "Constituent ID", "Email Address", "First Name", "Last Name", "Location Name", "Location Type ID"]]
        teams = teams.reset_index()
        
        #cleanup
        teams = pd.merge(teams, captains, how='left', left_on=['Event ID', 'Team Captain ID'], right_on=['Event ID', 'Constituent ID'])
        teams = teams.drop_duplicates()
        teams = teams.set_index(['Event ID', 'TeamID'])
        teams = teams.drop("Constituent ID",1)
        teams = teams.reindex(columns=["Team Name", 
										"Location Name", 
										"Location Type ID",
                                       "Team Size", 
                                       "Team Captain ID", 
                                       "Email Address", 
                                       "First Name", 
                                       "Last Name", 
                                       "team ver raised", 
                                       "team pledges", 
                                       "team ver sponsors", 
                                       "team pledges sponsors", 
                                       "ver raised", 
                                       "pledges", 
                                       "ver sponsors", 
                                       "pledges sponsors"])
        teams = teams.rename(columns={'team ver raised': 'Team Raised Verified', 
                                      'team pledges': 'Team Raised Unverified', 
                                      "ver raised": "team_members Verified", 
                                      "pledges": "team_members Unverified", 
                                      "ver sponsors": "Team Memmbers verified sponsors", 
                                      "pledges sponsors":"team_member unverified sponsors",
                                      "team ver sponsors": "Team verified sposnors",
                                      "team pledges sponsors": "Team unverified Sponsors",                                     
                                      })            
        teams["Total Verified"] = teams["Team Raised Verified"] + teams["team_members Verified"]
        teams["Total Unverified"] = teams["Team Raised Unverified"] + teams["team_members Unverified"]
        teams = teams.reset_index();
        
        title = maketitle("Team Details", options)
        if outputs[SUMMARY]:
            stats = teams.groupby(["Event ID"])["Team Size"].agg({'mean': np.mean, "median": np.median})        
            stats["most common"] = teams.groupby(["Event ID"])["Team Size"].agg(lambda x:x.value_counts().index[0])    
            stats["2nd most common"] = teams.groupby(["Event ID"])["Team Size"].agg(lambda x:x.value_counts().index[1])  
            self.outputs(stats, title, {SUMMARY: True}) 
        if outputs[EXCEL]:
            self.outputs(teams, title, {EXCEL: True}) 
        if outputs[CSV]:
            self.outputs(teams, title, {CSV: True})
           
        
             
    def findFunTyp(self, outputs, options):
        if options == "Verified":
            amount = self.fundraisers[self.fundraisers["ver raised"] > 0].groupby(self.depth() + ["Team"])["ver raised"]
            sponsors = self.fundraisers[self.fundraisers["ver sponsors"] > 0].groupby(self.depth() + ["Team"])["ver sponsors"]
        elif options == "Pledges":
            amount = self.fundraisers[self.fundraisers["pledges"] > 0].groupby(self.depth() + ["Team"])["pledges"]
            sponsors = self.fundraisers[self.fundraisers["pledges sponsors"] > 0].groupby(self.depth() + ["Team"])["pledges sponsors"]         
        else:
            amount = self.fundraisers[self.fundraisers["total"] > 0] .groupby(self.depth() + ["Team"])["total"]
            sponsors = self.fundraisers[self.fundraisers["total sponsors"] > 0].groupby(self.depth() + ["Team"])["total sponsors"]
        stats = amount.agg({'amount_mean': np.mean, "amount_median": np.median, "amount_sum": np.sum, "amount_count": "count"})
        stats["amount_mode"] = amount.agg(lambda x:x.value_counts().index[0])     
        stats = stats.merge(sponsors.agg({'sponsors_mean': np.mean, "sponsors_median": np.median, "sponsors_sum": np.sum, "sponsors_count": "count"}), left_index=True, right_index=True)
        stats["sponsors_mode"] = sponsors.agg(lambda x:x.value_counts().index[0])           
        title = maketitle("Fundraisers", options)
        if outputs[SUMMARY]:
            self.outputs(stats, title, {SUMMARY: True}) 
            #self.output.set(stats, title)             
        if outputs[EXCEL]:
            self.outputs(self.fundraisers, title, {EXCEL: True}) 
            #self.excelout.printexcel(self.outputfile, self.fundraisers, title)
        if outputs[GRAPH]: 
            #fig = plt.figure()
            #ax1 = fig.add_subplot(111)
            #ax1.set_ylabel('Sum')        
            #ps1 = ax1.bar(np.arange(len(stats.index)), stats["amount_sum"], label="Sum")
            #ax2 = plt.twinx()
            #ax2.set_ylabel('Mean')
            #ps2 = ax2.scatter(np.arange(len(stats.index))+0.5, stats["amount_mean"],c='g',s=120, label="Mean")
            #ax1.legend([ps1, ps2], [ps1.get_label(), ps2.get_label()])
            #plt.xlim(xmin=0)
            #ax1.set_xticklabels(stats.index, rotation=40, ha='center')
            #plt.title(title)
            #plt.show(block=False)boxplot
            if options == "Verified":
                col = "ver raised"
            elif options == "Pledges":
                col = "pledges"       
            else:
                col = "total"
            self.fundraisers[self.fundraisers["ver raised"] > 0].boxplot(column=col, by=["Event ID"])     
            plt.title(title)
            plt.show(block=False) 
        if outputs[CSV]:
            self.outputs(self.fundraisers, title, {CSV: True})
            
    def findDonationTimeline(self, outputs, options):
        mydons = self.donationoptions(options)
        mydons["Week"] = mydons["Donation Datetime"].apply(lambda x: x + datetime.timedelta(days=-x.weekday()))
        mydons["Week"] = mydons["Week"].apply(lambda x: x.isocalendar()[1])
        dontimeline = mydons.groupby(self.depth() + ["Week"])["Donation Amount"].sum().unstack(self.depth())
        mycols = dontimeline.columns.tolist()
        for col in mycols:
            dontimeline[col] = dontimeline[col].fillna(0) 
            if (isinstance(col, tuple)):
                colname = "cumsum " + ' '.join(col)
            else:
                colname = "cumsum " + col
            dontimeline[colname] = 100*dontimeline[col].cumsum() / dontimeline[col].sum()
        #dontimeline['percentage'] = 100 * dontimeline.cumsum() / dontimeline.sum()
        
        if outputs[GRAPH]: 
            dontimeline[mycols].plot()
        
        title = maketitle("Donation Timeline", options)
        self.outputs(dontimeline, title, outputs)          

    def findRegTimeline(self, outputs, options):
        regs = self.fundraisers[self.fundraisers["Transaction Source"] == options]
        regs["Week"] = regs["Registration Date"].apply(lambda x: x + datetime.timedelta(days=-x.weekday()))
        regs["Week"] = regs["Week"].apply(lambda x: x.isocalendar()[1])
        regtimeline = regs.groupby(self.depth() + ["Week"])["Constituent ID"].count().unstack(self.depth())
        mycols = regtimeline.columns.tolist()
        for col in mycols:
            regtimeline[col] = regtimeline[col].fillna(0) 
            if (isinstance(col, tuple)):
                colname = "cumsum " + ' '.join(col)
            else:
                colname = "cumsum " + col
            regtimeline[colname] = 100*regtimeline[col].cumsum() / regtimeline[col].sum()
            
        if outputs[GRAPH]: 
            regtimeline[mycols].plot()
        
        title = maketitle("Registrant Timeline", options)
        self.outputs(regtimeline, title, outputs)           
               
    def findReturnUsers(self, outputs, options):
        if options == "Constituent ID":
            returners = self.fundraisers[["Constituent ID", "Event ID", "ver raised"]]
            returners = pd.concat(g for _, g in returners.groupby("Constituent ID") if len(g) > 1)
            returnersexcel = returners.pivot(index="Constituent ID", columns="Event ID", values="ver raised")
            mergeon = ["Constituent ID"]
        elif options == "Email":
            #need to make sure "email" combo is unique within each event
            returners = self.fundraisers[["First Name", "Last Name", "Email Address", "Event ID", "ver raised", "Constituent ID"]]
            returners = returners.groupby(["First Name", "Last Name", "Email Address", "Event ID"])["ver raised"].sum().reset_index()
            returners = pd.concat(g for _, g in returners.groupby(["First Name", "Last Name", "Email Address"]) if len(g) > 1)
            returnersexcel = pd.pivot_table(returners, index=["First Name", "Last Name", "Email Address"], columns="Event ID", values="ver raised")
            mergeon = ["First Name", "Last Name", "Email Address"]
        #not working :(
        returnersexcel = returnersexcel.reset_index()
        for event in self.fundraisers["Event ID"].unique():
            returnersexcel = pd.merge(returnersexcel, self.fundraisers.loc[self.fundraisers["Event ID"] == event, mergeon + ['Mobile App']], how='left', left_on=mergeon, right_on=mergeon)
            returnersexcel = returnersexcel.rename(columns={"Mobile App": str(event) + " Mobile App"})
            #returnersexcel = returnersexcel.drop(mergeon,1)
            
        
        
        
        title = maketitle("Returning", options)
        if outputs[SUMMARY]:
            #pointer = "Constituent ID"
            #if pointer not in returners.columns:
            #    pointer = "Email Address"           
            mysummary = pd.DataFrame()
            my_r = range(2, len(self.events)+1)
            for r in my_r:
                eventIDs = list(itertools.combinations(self.events, r=r))
                for combo in eventIDs:    
                    dupes = returnersexcel                
                    for old,new in zip(combo, combo[1:]):
                        dupes = dupes[(dupes[old].notnull()) & (dupes[new].notnull())]
                        myname = "_".join(["growth", old, new])
                        dupes[myname] = 100 * ((dupes[new] - dupes[old]) / dupes[old])
                        #dupes[myname] = dupes[old] - dupes[new]
                        #dupes[myname] = 100*dupes.apply(lambda row: row[myname] / row[old] if row[old] > 0 else -row[myname], axis=1)
                        dupes[myname] = dupes[myname].replace([np.inf, -np.inf], np.nan)
                    myname = "-".join(list(combo))
                    mysummary.loc[myname, "Number People"] = len(dupes.index)
                    growth_col = [col for col in dupes.columns.tolist() if col.startswith('growth')]
                    #not sure this is right
                    mysummary.loc[myname, "Average growth"] = dupes[growth_col].mean(axis=1).mean()
                    mysummary.loc[myname, "Average raised"] = dupes[list(combo)].mean(axis=1).mean()
            self.outputs(mysummary, title, {SUMMARY: True}) 
            
        if outputs[EXCEL]:
            self.outputs(returnersexcel, title, {EXCEL: True}) 
            #self.excelout.printexcel(self.outputfile, returnersexcel, maketitle("Returning", options))             
        if outputs[GRAPH]:      
            mysummary = returners.groupby("Event ID")["Constituent ID"].count()
            mysummary.plot(kind = 'bar')
            plt.title(title)
            plt.show(block=False)   
        if outputs[CSV]:
            self.outputs(returnersexcel, title, {CSV: True})
            
    def findSelfSponsors(self, outputs, options):
        mydons = self.donations[self.donations["Payment Status"] == "Succeeded"]
        selfsponsprs = self.fundraisers.set_index(["Event ID", "Constituent ID"])
        if options == "Constituent ID":
            foo = mydons[mydons["Constituent ID"] == mydons["Solicitor ID"]].groupby(self.depth() + ["Solicitor ID"])["Donation Amount"]
            selfsponsprs["Self Sponsor amount"] = foo.sum()  
            selfsponsprs["Self Sponsor count"] = foo.count()    
        #Email
        else:
            foo = selfsponsprs[["Email Address", "First Name", "Last Name"]]
            mydons = mydons.set_index(['Event ID', 'Solicitor ID'])
            mydons[["fmail","fname","lname"]] = foo[["Email Address", "First Name", "Last Name"]]
            mydons = mydons.reset_index()
            foo = mydons[(mydons["fmail"] == mydons["Email Address"]) & (mydons["fname"] == mydons["First Name"]) & (mydons["lname"] == mydons["Last Name"])].groupby(self.depth() + ["Solicitor ID"])["Donation Amount"]
            selfsponsprs["Self Sponsor amount"] = foo.sum()
            selfsponsprs["Self Sponsor count"] = foo.count()
        
        selfsponsprs = selfsponsprs.dropna(how='all', subset=[["Self Sponsor amount"]])
        title = maketitle("Self Sponsors", options)
        if outputs[SUMMARY]:
            mysummary = selfsponsprs.reset_index().groupby(self.depth())[["Self Sponsor amount", "Self Sponsor count"]].agg(['mean', 'count', 'sum'])
            self.outputs(mysummary, title, {SUMMARY: True}) 
            #self.output.set(mysummary, title)    
        if outputs[EXCEL]:
            #self.excelout.addworksheet(selfsponsprs, title)
            self.outputs(selfsponsprs, title, {EXCEL: True})
            #self.excelout.printexcel(self.outputfile, selfsponsprs, title)             
        if outputs[GRAPH]:      
            mysummary = selfsponsprs.reset_index().groupby(self.depth())["Constituent ID"].count()
            mysummary.plot(kind = 'bar')
            plt.title(title)
            plt.show(block=False)                  
        if outputs[CSV]:
            self.outputs(selfsponsprs, title, {CSV: True})
            
    def findGrowth(self, outputs, options):
        mydons = self.donationoptions(options)  
        years = self.events
        growth = pd.DataFrame(years[1:])
        growth.columns = ['Event ID']
        growth["Reg"] = 0.0
        growth["Dons"] = 0.0
        growth = growth.set_index("Event ID")
        for old,year in zip(years,years[1:]):
            regyear = float(self.fundraisers.loc[self.fundraisers["Event ID"] == year, "Constituent ID"].count())
            regold = float(self.fundraisers.loc[self.fundraisers["Event ID"] == old, "Constituent ID"].count())
            donyear = float(mydons.loc[mydons["Event ID"] == year, "Donation Amount"].sum())
            donold = float(mydons.loc[mydons["Event ID"] == old, "Donation Amount"].sum())
            growth.loc[year, "Reg"] = 100.0 * ((regyear - regold) / regold)
            growth.loc[year, "Dons"] = 100.0 * ((donyear - donold) / donold)
        
        if outputs[GRAPH]: 
            foo = growth.plot()
            foo.legend(["Registrants", "Donations"])
        
        title = maketitle("Growth Rate", options)
        self.outputs(growth, title, outputs)   
    
    
    def findHistogram(self, outputs, options):
        mydons = self.donationoptions(options)      
        hist = mydons.reset_index()[self.depth() + ["Donation Amount"]]
        hist = hist.groupby(self.depth() + ["Donation Amount"]).size().unstack(self.depth())
        #https://en.wikipedia.org/wiki/Freedman-Diaconis_rule
        mysummary = 2*(hist.quantile(0.75) - hist.quantile(0.25))*hist.count()**(-1/3.0)
        mysummary = mysummary.apply(np.round)
        title = maketitle("Histogram", options)  
        if outputs[EXCEL]:
            self.outputs(hist, title, {EXCEL: True}) 
        if outputs[CSV]:
            self.outputs(hist, title, {CSV: True}) 
        if outputs[SUMMARY]:
            self.outputs(mysummary, "Bin Widths", {SUMMARY: True}) 
        if outputs[GRAPH]:
            #foo = mydons.reset_index().pivot(index="index", columns="Event ID", values="Donation Amount")
            #foo = foo.reset_index()
            #foo = foo.drop("index",1)
            #for col in foo.columns:
            #    plt.hist(foo[col].dropna(), int(round(mysummary.mean())), normed=True, color=np.random.rand(len(foo.columns),1), alpha=1.0/len(foo.columns), label=col)
            #plt.legend()  
            binssize = int(round(mysummary.mean()))
            bins = len(hist.index) / binssize
            hist.plot(kind='hist', bins = bins, alpha=0.5)
            plt.title(title)
            plt.show(block=False) 

        
        
    def findLocations(self, outputs, options):
        mydons = self.donationoptions(options)            
        locations = mydons.groupby(["Location Name", "Event ID"])["Donation Amount"].sum().reset_index().set_index(["Location Name", "Event ID"])
        foo = self.fundraisers.groupby(["Location Name", "Event ID"])["Constituent ID"].count()
        locations["Registrants"] = foo
        foo = self.fundraiseroptions(options, True)
        foo = foo.reset_index().groupby(["Location Name", "Event ID"])["Constituent ID"].count()
        locations["Active"] = foo
        locations["Teams"] = self.fundraisers[self.fundraisers["TeamID"] != -1].groupby(["Location Name", "Event ID"])["TeamID"].nunique()
        #locations["Teams"] = locations.groupby(["Location Name", "Event ID"])["Registrants"].transform(lambda x: 1. / len(x))

        if outputs[GRAPH]:
            fig, axes = plt.subplots(nrows=2, ncols=1, sharey=True)
            title = maketitle("Donations", options)
            locations["Donation Amount"].plot(ax=axes[0], kind='barh'); axes[0].set_title(title)
            title = maketitle("Registrants", options)
            locations[["Registrants", "Active"]].plot(ax=axes[1], kind='barh'); axes[1].set_title(title)
        
        locations = locations.reset_index()
        title = maketitle("Locations", options)
        self.outputs(locations, title, outputs)
        
    
    def findactives(self, outputs, options):
        foo = self.fundraiseroptions(options, True)
        foo = foo.groupby(["Team"]+ self.depth()).size()
        active = pd.DataFrame(index = foo.index)
        active["Active"] = foo
        foo = self.fundraiseroptions(options, False)
        active["Inactive"] = foo.groupby(["Team"] + self.depth()).size()
        active["total"] = active["Active"] + active["Inactive"] 
        active["ratio"] = 100*(active["Active"] / active["total"])
        
        if outputs[GRAPH]:
            active[["Active","Inactive"]].plot(kind='barh', stacked=True)
        
        title = maketitle("Active Users", options)
        self.outputs(active, title, outputs)
    
    
          
    def findDonationStats(self, outputs, options):
        if (options == "whitepaper"):
            mydons = self.donationoptions("Online")
            mydons = mydons[mydons["Solicitor ID"].notnull()]
            mydons["facebook"] = False
            mydons.loc[mydons["Facebook FPF Donation"] == "Yes","facebook"] = True
            mydons.loc[mydons["URL Referrer"].str.contains("FACEBOOK"),"facebook"] = True
            #self.fundraisers.loc[self.fundraisers["Team Size"] >0, "Team"] = "team_member"
            
            donstats = mydons.groupby(self.depth() + ["facebook"])["Donation Amount"].agg(['mean', 'median', 'count', 'sum'])
            donstats["mode"] = mydons.groupby(self.depth() + ["facebook"])["Donation Amount"].agg(lambda x:x.value_counts().index[0])  
            donstats = donstats.reset_index()
        else:
            mydons = self.donationoptions(options)
            donstats = mydons.groupby(self.depth() + ["Typology"])["Donation Amount"].agg(['mean', 'median', 'count', 'sum'])         
            donstats["mode"] = mydons.groupby(self.depth() + ["Typology"])["Donation Amount"].agg(lambda x:x.value_counts().index[0])  
            donstats = donstats.reset_index()

        if outputs[GRAPH]:   
            #fig = plt.figure()
            #ax1 = fig.add_subplot(111)      
            #ax1.set_ylabel('Sum')        
            #ps1 = ax1.bar(np.arange(len(donstats.index)), donstats["sum"], label="Sum")
            #ax2 = plt.twinx()
            #ax2.set_ylabel('Mean')
            #ps2 = ax2.scatter(np.arange(len(donstats.index))+0.5, donstats["mean"],c='g',s=120, label="Mean")
            #ax1.legend([ps1, ps2], [ps1.get_label(), ps2.get_label()])
            #plt.xlim(xmin=0)
            #ax1.set_xticks(np.arange(len(donstats.index)))
            #ax1.set_xticklabels(donstats.index, rotation=40, ha='center')
            #plt.draw()
        #if outputs[GRAPH]:
            mydons.boxplot(column=["Donation Amount"], by=["Event ID"])
            #counter = 1
            #for i in mydons["Event ID"].unique():
            #    y = mydons[mydons["Event ID"] == i]["Donation Amount"].dropna()
            #    foo = len(y)
            #    x = np.random.normal(counter, 0.04, size=foo)
            #    counter += 1
            #    plt.plot(x,y,'g.', alpha=0.2)
        
        title = maketitle("Donations", options)
        self.outputs(donstats, title, outputs)
        
    def outputs(self, report, name, outputs):
        if GRAPH in outputs and outputs[GRAPH]:
            plt.title(name)
            plt.show(block=False)
        if EXCEL in outputs and outputs[EXCEL]:
            self.excelout.addworksheet(report, name)
            #self.excelout.printexcel(self.outputfile, report, name)   
        if SUMMARY in outputs and outputs[SUMMARY]:
            self.output.set(report, name)  
        if CSV in outputs and outputs[CSV]:
            self.excelout.printCSV(report, name, self.outputdir)
            
    def printExcel(self):
        self.excelout.printexcel(self.outputfile)
        self.excelout.clear()