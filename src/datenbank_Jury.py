import sqlite3

# ANZAHL_T = 4
# ANZAHL_P = 4
# ANZAHL_D_EK_PK = 2
# ANZAHL_D_KG_GG = 4

ALTERSKLASSEN = ["U15", "15+"]
KATEGORIEN = ["EK", "PK", "KG", "GG"]
KUERZEL = ["T1", "T2", "T3", "T4", "P1", "P2", "P3", "P4", "D1", "D2"]


connection = sqlite3.connect("../data/Jury.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS Jury")

sql_erstellen = """
CREATE TABLE jury (
Kuerzel VARCHAR(2) NOT NULL,
Kategorie VARCHAR(20) NOT NULL,
Altersklasse VARCHAR(3) NOT NULL,
PRIMARY KEY ('Kuerzel','Altersklasse', 'Kategorie'));"""

cursor.execute(sql_erstellen)

for kategorie in KATEGORIEN:
    for altersklasse in ALTERSKLASSEN:
        for kuerzel in KUERZEL:
            sql_einfuegen = """INSERT INTO jury (Kuerzel, Kategorie, Altersklasse) VALUES (?, ?, ?) """
            daten = (kuerzel, kategorie, altersklasse)
            cursor.execute(sql_einfuegen, daten)

# Änderung Speichern
connection.commit()
