num=int(input("Enter a number:\n1"))
original=num
n=len(str(num))
sum_of_powers =sum(int(digit) ** n for digit in str(num))
if num== sum_of_powers:
    print(f"{original} is an Armstrong number")
else:
    print(f"{original} is not an Armstrong number")