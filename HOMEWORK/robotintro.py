class robot:
    def __init__(self,name1,name2):
        self.name1=name1
        self.name2=name2
    def display_names(self):
        print("The name of Robot1 is ",self.name1)
        print("The name of Robot2 is ",self.name2)
ob= robot("Tom","Jerry")
ob.display_names()