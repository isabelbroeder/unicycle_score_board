import sqlite3
import pandas as pd

# read in excel
excel_path = "../data/Anmeldung_Landesmeisterschaft_2025.xlsx"   # update with your actual path
df = pd.read_excel(excel_path, sheet_name=1, skiprows=4)



print("Columns:", df.columns)

connection = sqlite3.connect("../data/fahrerinnnen_test1.db")
cursor = connection.cursor()

# # uncomment below to create database
# sql_command = """
# CREATE TABLE fahrerinnen (
# person_nummer INTEGER PRIMARY KEY,
# name VARCHAR(50),
# gender CHAR(1),
# geburtsdatum DATE);"""

# cursor.execute(sql_command)


#sql_command = """INSERT INTO fahrerinnen (person_nummer, name, gender, geburtsdatum)
#    VALUES (NULL, "Lara Müller", "w", "2002-07-23");"""
#cursor.execute(sql_command)

# never forget this, if you want the changes to be saved:
#connection.commit()


cursor.execute("SELECT geburtsdatum FROM fahrerinnen")
print("fetchall:")
result = cursor.fetchall()
for r in result:
    print(type(r[0]))

connection.close()
