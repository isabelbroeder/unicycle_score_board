import datetime
import sqlite3
import pandas as pd

WETTKAMPFTAG = datetime.datetime(2025, 5, 1, 0, 0)

# Anmelde-Datei einlesen
anmeldung = pd.read_excel("../data/Anmeldung_Landesmeisterschaft_2025.xlsx", sheet_name=1, skiprows=4,)
anmeldung.columns = ['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Fährt_EK', 'Name_EK', 'Ak_EK', 'Fährt_PK',
                     'Name_PK', 'Ak_PK', 'Fährt_KG', 'Name_KG', 'Ak_KG', 'Fährt_GG', 'Name_GG', 'Ak_GG', 'Startgeld']
anmeldung = anmeldung[anmeldung['Name'].notna()]  # nur die Zeilen, die einen Namen enthalten speichern
anmeldung = anmeldung.drop(columns='Startgeld')

#print(anmeldung.dtypes)
anmeldung = anmeldung.convert_dtypes()


# Verein hinzufügen
anzahl_fahrerinnen = anmeldung['Name'].size
anmeldung.insert(4, 'Verein', ['BW96 Schenefeld'] * anzahl_fahrerinnen)
print('anmeldung.columns',anmeldung.columns)


# Datenbank verbinden
connection = sqlite3.connect("../data/fahrerinnen.db")
cursor = connection.cursor()

df_fahrerinnen = anmeldung[['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Verein']]
#df_fahrerinnen.to_sql('fahrerinnen', connection, if_exists = 'append')

sql_erstellen = """
CREATE TABLE fahrerinnen (
Personen_Nummer INTEGER PRIMARY KEY,
Name VARCHAR(50),
Geschlecht CHAR(1),
Geburtsdatum DATE,
Alter_Wettkampf INTEGER,
Verein VARCHAR(50));"""

cursor.execute(sql_erstellen)


for zeile in range (0,anzahl_fahrerinnen):
    alter = 20 # später Alter richtig berechnen
    sql_einfuegen = f"""INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Verein) VALUES (NULL, {df_fahrerinnen['Name']}, {df_fahrerinnen['Geschlecht']}, {df_fahrerinnen['Geburtsdatum']},  {df_fahrerinnen['Verein']});"""
    sql_einfuegen = """INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Alter_Wettkampf, Verein) VALUES (?, ? , ? , ? , ? , ?) """
    daten = (None, df_fahrerinnen['Name'][zeile], df_fahrerinnen['Geschlecht'][zeile], df_fahrerinnen['Geburtsdatum'][zeile].strftime('%Y-%m-%d'), alter, df_fahrerinnen['Verein'][zeile])
    cursor.execute(sql_einfuegen, daten)

# Änderung Speichern
connection.commit()



# cursor.execute("SELECT Name FROM fahrerinnen")
# result = cursor.fetchall()
# for r in result:
#     print((r[0]))

connection.close()


