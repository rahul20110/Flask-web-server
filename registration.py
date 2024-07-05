import csv

def save_registration_details(graduate_name, roll_number,phone_number, dob, hashed_password):
    with open('database.csv', mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow([graduate_name.lower(), roll_number, dob, phone_number, hashed_password])
if __name__ == '__main__':
    pass