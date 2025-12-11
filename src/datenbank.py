import datetime
import sqlite3
import pandas as pd


WETTKAMPFTAG = datetime.datetime(2025, 5, 1, 0, 0)
KATEGORIEN = ["EK", "PK", "KG", "GG"]

# Anmelde-Datei einlesen
anmeldung = pd.read_excel(
    "../data/Anmeldung_Landesmeisterschaft_2025.xlsx", sheet_name=1, skiprows=4
)
anmeldung.columns = [
    "Name",
    "Geburtsdatum",
    "Alter",
    "Geschlecht",
    "Fährt_EK",
    "Name_EK",
    "AK_EK",
    "Fährt_PK",
    "Name_PK",
    "AK_PK",
    "Fährt_KG",
    "Name_KG",
    "AK_KG",
    "Fährt_GG",
    "Name_GG",
    "AK_GG",
    "Startgeld",
]
anmeldung = anmeldung[
    anmeldung["Name"].notna()
]  # nur die Zeilen, die einen Namen enthalten speichern
anmeldung = anmeldung.drop(columns="Startgeld")
# print(registration)
# registration = registration.where(registration.notna(), np.nan)
# print(registration)

# print(registration.dtypes)
anmeldung = anmeldung.convert_dtypes()


# Verein hinzufügen
anzahl_fahrerinnen = anmeldung["Name"].size
anmeldung.insert(4, "Verein", ["BW96 Schenefeld"] * anzahl_fahrerinnen)
print("registration.columns", anmeldung.columns)


# Datenbank fährt_kür erstellen
def starts_in_db(
    df_anmeldung, kategorie: str, connection: sqlite3.Connection, cursor: sqlite3.Cursor
):
    for zeile in range(0, anzahl_fahrerinnen):
        print(
            zeile,
            anmeldung["Name"][zeile],
            anmeldung["Name_EK"][zeile],
            anmeldung["Name_PK"][zeile],
        )


connection = sqlite3.connect("../data/faehrt_kuer.db")
cursor = connection.cursor()
starts_in_db(anmeldung, "EK", connection, cursor)
'''
    spalte_name = "Name_" + str(kategorie)
    spalte_kuername = "Kürname_" + str(kategorie)
    spalte_ak = "AK_" + str(kategorie)
    kuernamen = df_anmeldung[spalte_kuername].dropna().unique()
    kuernamen = [
        s for s in kuernamen if s.strip() != ""
    ]  # entfernt Strings, die nur aus Leerzeichen bestehen
    
    

    for kuername in kuernamen:
        sql_einfuegen = (
            """INSERT INTO faehrt (Kuer_Nummer, Kuername, Name) VALUES (?, ?, ?) """
        )
        daten = (None, kuername, df_anmeldung["Name"].where(spalte_kuername == kuername))
        cursor.execute(sql_einfuegen, daten)
        connection.commit()



# Datenbank verbinden
connection = sqlite3.connect("../data/fahrerinnen.db")
cursor = connection.cursor()

df_fahrerinnen = registration[["Name", "Geburtsdatum", "Alter", "Geschlecht", "Verein"]]
# df_fahrerinnen.to_sql('fahrerinnen', connection, if_exists = 'append')

cursor.execute("DROP TABLE IF EXISTS fahrerinnen")

sql_erstellen = """
CREATE TABLE fahrerinnen (
Personen_Nummer INTEGER PRIMARY KEY,
Name VARCHAR(50),
Geschlecht CHAR(1),
Geburtsdatum DATE,
Alter_Wettkampf INTEGER,
Verein VARCHAR(50));"""

cursor.execute(sql_erstellen)


for zeile in range(0, anzahl_fahrerinnen):
    alter = alter_berechnen(
        df_fahrerinnen["Geburtsdatum"][zeile].to_pydatetime(), WETTKAMPFTAG
    )
    sql_einfuegen = """INSERT INTO fahrerinnen (Personen_nummer, Name, Geschlecht, Geburtsdatum, Alter_Wettkampf, Verein) VALUES (?, ? , ? , ? , ? , ?) """
    daten = (
        None,
        df_fahrerinnen["Name"][zeile],
        df_fahrerinnen["Geschlecht"][zeile],
        df_fahrerinnen["Geburtsdatum"][zeile].strftime("%Y-%m-%d"),
        alter,
        df_fahrerinnen["Verein"][zeile],
    )
    cursor.execute(sql_einfuegen, daten)


# Änderung Speichern
connection.commit()


# cursor.execute("SELECT Name FROM fahrerinnen")
# result = cursor.fetchall()
# for r in result:
#     print((r[0]))


# Küren in Datenbank kuer.db

connection_kuer = sqlite3.connect("../data/kuer.db")
cursor_kuer = connection_kuer.cursor()

cursor_kuer.execute("DROP TABLE IF EXISTS kuer")

sql_erstellen = """
CREATE TABLE kuer (
Kuer_Nummer INTEGER PRIMARY KEY,
Kuername VARCHAR(50),
Kategorie VARCHAR(20),
Altersklasse VARCHAR(3));"""

cursor_kuer.execute(sql_erstellen)


def kueren_in_db(df_anmeldung, kategorie: str, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    spalte_name = "Name_" + str(kategorie)
    spalte_ak = "AK_" + str(kategorie)
    kuernamen = df_anmeldung[spalte_name].dropna().unique()
    kuernamen = [
        s for s in kuernamen if s.strip() != ""
    ]  # entfernt Strings, die nur aus Leerzeichen bestehen
    kuer_nummer = 0
    for kuername in kuernamen:
        kuer_nummer = kuer_nummer + 1
        ak_kuer = ((df_anmeldung[spalte_ak].where(kuername==df_anmeldung[spalte_name])).dropna()).iloc[0]
        print(ak_kuer)
        sql_einfuegen = (
            """INSERT INTO kuer (Kuer_Nummer, Kuername, Kategorie, Altersklasse) VALUES (?, ?, ?, ?) """
        )
        daten = (kuer_nummer, kuername, kategorie, ak_kuer)
        cursor.execute(sql_einfuegen, daten)
    connection.commit()


for kategorie in KATEGORIEN:
    kueren_in_db(registration, kategorie, connection_kuer, cursor_kuer)


connection.close()
connection_kuer.close()

'''
