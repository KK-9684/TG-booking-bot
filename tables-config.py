import mysql.connector

db = mysql.connector.connect(host = "localhost",user = "root",passwd = "",database = "test1")

cur = db.cursor()

def table():
    try:
        cur.execute("CREATE TABLE book(BookID INT AUTO_INCREMENT Primary Key, Name VARCHAR(50), PhoneNumber INT, TypeOfRoom INT, CheckInDate DATE, CheckOutDate DATE, BookingSource INT, Price FLOAT(10,2), Payment bool, Deposit FLOAT(10,2), CheckedIn bool, Absent bool)")
            # Type of room:
            #   1 A, 2 B1, 3 B2, 4 C, 5 101, 6 102, 7 201, 8 202, 9 full house
            # Booking source:
            #   1 Agoda, 2 booking, 3 directbooking
            # Payment:
            #   0 full, 1 deposit
        db.commit()
        print("Tables created sucessfully")
    except:
        print("tables error1")

table()

