import sqlite3

connection = sqlite3.connect("../.venv/fahrerinnnen_test.db")
cursor = connection.cursor()


#sql_command = """
#CREATE TABLE fahrerinnen (
#person_nummer INTEGER PRIMARY KEY,
#name VARCHAR(50),
#gender CHAR(1),
#geburtsdatum DATE,
#verein VARCHAR(50));"""

#cursor.execute(sql_command)


#sql_command = """INSERT INTO fahrerinnen (person_nummer, name, gender, geburtsdatum, verein)
#    VALUES (NULL, "Lara Müller", "w", "2002-07-23", "BW96 Schenefeld");"""
#cursor.execute(sql_command)

# never forget this, if you want the changes to be saved:
#connection.commit()


cursor.execute("SELECT geburtsdatum FROM fahrerinnen")
print("fetchall:")
result = cursor.fetchall()
for r in result:
    print(type(r[0]))

connection.close()
