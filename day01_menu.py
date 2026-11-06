
while True:

    print("\n SuryaGharSathi Menu ")
    print("1. About SuryaGharSathi")
    print("2. Sample Questions")
    print("3. Check Solar Scheme")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("SuryaGharSathi helps people understand rooftop solar schemes.")

    elif choice == "2":
        print("1. What is PM Surya Ghar Yojana?")
        print("2. What are the benefits of rooftop solar?")
        print("3. How can I apply for the solar scheme?")

    elif choice == "3":
        connection = input("Is your electricity connection residential or commercial? ")

        if connection.lower() == "residential":
            print("You can explore PM Surya Ghar scheme details.")
        elif connection.lower() == "commercial":
            print("This scheme is intended for residential households.")
        else:
            print("Please enter residential or commercial.")

    elif choice == "0":
        print("Thank you for using SuryaGharSathi!")
        break

    else:
        print("Invalid choice. Try again.")
