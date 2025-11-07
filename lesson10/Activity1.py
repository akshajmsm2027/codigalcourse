class Person(object):
    def __init__(self,name,idnumber):
        self.name = name
        self.idnumber = idnumber
    def display(self):
        print(self.name)
        print(self.idnumber)
class Employee(Person):
    def __init__(self,name,idnumber,salary,post):
        self.salary = salary
        self.post = post
        Person.__init__(self,name,idnumber)
    def display1(self):
        print(self.salary)
        print(self.post)
a = Employee('Ritvik',202104777,15000,"Intern")
a.display()
a.display1()