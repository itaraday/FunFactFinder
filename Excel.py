import pandas as pd

class exceloutput:
    def __init__(self):
        self.data = {}
    
    def addworksheet(self, data, name):
        self.data[name] = data
    
    def printCSV(self, report, name, outputdir):
        outputdir = outputdir + "/" + name + ".csv"
        report.to_csv(outputdir)
        
    
    def printexcel(self, filename):
        if filename:
            writer = pd.ExcelWriter(filename)
            #for key in self.data.keys():
            #    self.data[key].to_excel(writer, key)
            oldworkbook = "error"
            #if the file exists open it and copy each worksheet to paste it with the new ones
            try:
                oldworkbook = pd.ExcelFile(filename)
                for sheet in oldworkbook.sheet_names:
                    oldworkbook.parse(sheet).to_excel(writer, sheet)
            except:
                print "new file"
            #writing new worksheets
            for key, value in self.data.iteritems():
                value.to_excel(writer, key)
            writer.save()
            self.clear()
        
    def clear(self):
        self.data = {}
        