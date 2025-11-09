import sqlite3
import pandas as pd

# Anmelde-Datei einlesen
anmeldung = pd.read_excel("../data/Anmeldung_Landesmeisterschaft_2025.xlsx", sheet_name = 1, skiprows=4)
anmeldung.columns = ['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Fährt_EK', 'Name_EK', 'Ak_EK', 'Fährt_PK', 'Name_PK', 'Ak_PK', 'Fährt_KG', 'Name_KG', 'Ak_KG', 'Fährt_GG', 'Name_GG', 'Ak_GG', 'Startgeld']
anmeldung = anmeldung[anmeldung['Name'].notna()]  # nur die Zeilen, die einen Namen enthalten speichern

# Verein hinzufügen
anzahl_fahrerinnen = anmeldung['Name'].size
anmeldung.insert(4, 'Verein', ['BW96 Schenefeld'] * anzahl_fahrerinnen)
anmeldung.drop(columns = 'Startgeld')
print(anmeldung.columns)
#print(anmeldung[['Name', 'Geburtsdatum', 'Alter', 'Geschlecht']])
print(anmeldung.convert_dtypes().dtypes)
x = 'x'
print(type(x))

df_fahrerinnen = anmeldung[['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Verein']]


# connection = sqlite3.connect("../data/fahrerinnen.db")
# cursor = connection.cursor()

#df_fahrerinnen.to_sql('fahrerinnen', connection, if_exists = 'append')
'''
sql_command = """
CREATE TABLE fahrerinnen (
Personen_Nummer INTEGER PRIMARY KEY,
Name VARCHAR(50),
Geschlecht CHAR(1),
Geburtsdatum DATE,
Alter INTEGER,
Verein VARCHAR(50));"""

# cursor.execute(sql_command)

for zeile in anmeldung:

    sql_command = """INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Verein)
        VALUES (NULL, "Lara Müller", "w", "2002-07-23", "BW96 Schenefeld");"""
    cursor.execute(sql_command)

# never forget this, if you want the changes to be saved:
# connection.commit()


cursor.execute("SELECT Name FROM fahrerinnen")
#print("fetchall:")
result = cursor.fetchall()
for r in result:
    print((r[0]))

connection.close()

'''