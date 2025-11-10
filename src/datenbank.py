import datetime
import sqlite3
import pandas as pd

from funktionen import alter_berechnen

COMPETITION_DAY = datetime.datetime(2025, 5, 1, 0, 0)

"""read in the sign-up file"""
sign_up = pd.read_excel("../data/Anmeldung_Landesmeisterschaft_2025.xlsx", sheet_name=1, skiprows=4, )
sign_up.columns = ['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Fährt_EK', 'Name_EK', 'Ak_EK', 'Fährt_PK',
                     'Name_PK', 'Ak_PK', 'Fährt_KG', 'Name_KG', 'Ak_KG', 'Fährt_GG', 'Name_GG', 'Ak_GG', 'Startgeld']
sign_up = sign_up[sign_up['Name'].notna()]  # nur die Zeilen, die einen Namen enthalten speichern
sign_up = sign_up.drop(columns='Startgeld')

#print(anmeldung.dtypes)
sign_up = sign_up.convert_dtypes()


"""add clubs to the database"""
connection = sqlite3.connect("../data/fahrerinnen.db")
total_participants = sign_up['Name'].size
sign_up.insert(4, 'Verein', ['BW96 Schenefeld'] * total_participants)
print('anmeldung.columns', sign_up.columns)


"""connect the database"""
connection = sqlite3.connect("../data/fahrerinnen.db")
cursor = connection.cursor()

df_participants = sign_up[['Name', 'Geburtsdatum', 'Alter', 'Geschlecht', 'Verein']]
#df_fahrerinnen.to_sql('fahrerinnen', connection, if_exists = 'append')

cursor.execute("DROP TABLE IF EXISTS fahrerinnen")

sql_create = """
CREATE TABLE fahrerinnen (
Personen_Nummer INTEGER PRIMARY KEY,
Name VARCHAR(50),
Geschlecht CHAR(1),
Geburtsdatum DATE,
Alter_Wettkampf INTEGER,
Verein VARCHAR(50));"""

cursor.execute(sql_create)


for line in range (0, total_participants):
    alter =  alter_berechnen(df_participants['Geburtsdatum'][line].to_pydatetime(), COMPETITION_DAY) # später Alter richtig berechnen
    #sql_einfuegen = f"""INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Verein) VALUES (NULL, {df_fahrerinnen['Name']}, {df_fahrerinnen['Geschlecht']}, {df_fahrerinnen['Geburtsdatum']},  {df_fahrerinnen['Verein']});"""
    sql_add = """INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Alter_Wettkampf, Verein) VALUES (?, ? , ? , ? , ? , ?) """
    daten = (None, df_participants['Name'][line], df_participants['Geschlecht'][line], df_participants['Geburtsdatum'][line].strftime('%Y-%m-%d'), alter, df_participants['Verein'][line])
    cursor.execute(sql_add, daten)

# Änderung Speichern
connection.commit()



# cursor.execute("SELECT Name FROM fahrerinnen")
# result = cursor.fetchall()
# for r in result:
#     print((r[0]))

connection.close()


