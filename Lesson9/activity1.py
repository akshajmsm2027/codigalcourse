class Library:
    def _init_(self,list,name):
        self.booklist = list
        self.name = name
        self.lendDict = {}
    def displayBooks(self):
        print(f"We have following books in our library:{self.name}")
        for book in self.booklList:
            print(book)
    def  lendBook(self,user,book):
        if book not in self.lendDict.keys():
            self.lendDict.update({book: user})
            print("Lender-Book database has been updated. You can take the book now ")
        else:
            print(f"Book is already being used by {self.lendDict(book)}")
    def addBook(self,book):
        self.bookList.append(book)
        print("Book has been added to the list")
    def returnBook(self,book):
        self.lendDict.pop(book)
    