import xlsxwriter
from subscriber import Subscriber

class Tracker(Subscriber):
    
    def on_open(self):
        self.workbook_name = "WoTHistory.xlsx"
        with xlsxwriter.Workbook(self.workbook_name) as workbook:
            workbook.add_worksheet("Light")
            workbook.add_worksheet("Temp")
        
        self.row_t = 0
        self.row_l = 0

    def on_propertyStatus(self, message):
        with xlsxwriter.Workbook(self.workbook_name) as workbook:
            if "data" in message:
                if "light" in message["data"]:
                    workbook.get_worksheet_by_name('Light').write(self.row_l, 0, message["data"]["light"])
                    self.row_l += 1
                elif "temp" in message["data"]:
                    workbook.get_worksheet_by_name('Temp').write(self.row_t, 0, message["data"]["temp"])   
                    self.row_t += 1   

if __name__ == '__main__':
    s = Tracker("localhost:5000/things/tetoz")
    s.run()
