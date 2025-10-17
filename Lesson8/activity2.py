class student:
    grade = 5
    name = "Ritvik"
    def intro (self):
         print("Hi I am a student")
    def details(self):
         print("My name is ",self.name)
         print("I study in grade " , self.grade)
ob=student()
ob.intro()
ob.details()