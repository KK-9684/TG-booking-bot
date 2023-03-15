import mysql.connector

db = mysql.connector.connect(host = "localhost",user = "root",passwd = "")

cur = db.cursor()


def database():
    try:
        cur.execute("CREATE DATABASE test1;")
        db.commit()
        print("Database created sucessfully!!")
        

    except:
        print("error")



database()











