while True:

    print(" SuryaGharSathi Menu ")
    print("1. About SuryaGharSathi")
    print("2. Sample Questions")
    print("3. Check Solar System Capacity")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("SuryaGharSathi helps homeowners understand PM Surya Ghar.")
        print("It compares solar systems, subsidies and payback periods.")

    elif choice == "2":
        print("1. What is PM Surya Ghar Yojana?")
        print("2. How much central subsidy is available?")
        print("3. What is the difference between 2 kW and 3 kW?")
        print("4. How long does solar installation take to recover its cost?")

    elif choice == "3":
        capacity = input("Enter solar capacity (2 or 3 kW): ")

        if capacity == "2":
            print("You selected a 2 kW rooftop solar system.")

        elif capacity == "3":
            print("You selected a 3 kW rooftop solar system.")

        else:
            print("Please enter either 2 or 3.")

    elif choice == "0":
        print("Thank you for using SuryaGharSathi!")
        break

    else:
        print("Invalid choice. Try again.")