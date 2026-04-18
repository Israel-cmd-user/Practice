def function_a ():
    x = 11
    print(f"The result of function a is {x}\n")
    return x

def function_b ():
    b = 5
    print(f"The result of function b is {b}\n")
    return b

def function_c ():
    sum = function_a() + function_b
    print(f"The total sum is: {sum}\n")
    return sum

def run_program():
    print("-"*40)
    print("WELCOME TO THE USER MANAGEMENT SYSTEM")
    print("-"*40)
    name = input("Enter your name ")
    print(f"Hello {name}" )

    print("\n Which function do you want to run?")
    print("1. Funtion to print images only.")
    print("2. Function that includes boundary boxes.")
    print("3. Function to add 1 and 2 together.")

    choice = input("\nEnter choice: 1-3 ")

    match choice:
        case "1":
            function_a()
        case "2":
            function_b()
        case "3":
            function_c()
        case _:
            print("Invalid selection please try again")

if __name__ =="__main__":
    run_program()

