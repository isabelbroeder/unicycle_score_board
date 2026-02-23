# Einrad-Dashboard

<p>
  🇬🇧 <a href="README.md">English</a> |
  🇩🇪 <a href="README.de.md">Deutsch</a>
</p>

## Projektbeschreibung
Das Einrad-Dashboard ist ein Softwaretool zur Visualisierung und Verwaltung von Wettkampfdaten im Einradsport. Es integriert Daten aus Datenbanken und stellt sowohl eine Teilnehmerübersicht als auch eine Juryübersicht bereit.

Die Teilnehmerübersicht ermöglicht die Anzeige relevanter Informationen über die Teilnehmenden und ihre Kürprogramme. In der Juryübersicht können Jurymitglieder die Punkte für jede einzelne Kür eingeben. Die Gesamtpunktzahl pro Kür wird automatisch berechnet und interaktiv aktualisiert. 

## Projektumfang und Zielsetzung
- Datenbanken aus .xlsx-Dateien zur Speicherung von Teilnehmer- und Kürdaten erstellen.
- Teilnehmer- und Juryübersichten basierend auf Datenbankdaten bereitstellen.
- Punkteingabe durch Jury mit automatischer Gesamtpunktberechnung ermöglichen.
- Zugriff auf Juryübersicht durch verschlüsselte Passwortauthentifizierung sichern.``

## Einrichtung

Welche Bedingungen müssen die .xlsx-Dateien erfüllen!?

Die .xlsx-Dateien werden im Skript `create_database.py` verwendet, um die Datenbanken `riders.db`, `routines.db` und `riders_routines.db` zu erstellen, die im weiteren Verlauf verwendet werden.

## Verwendung

0. Stellen Sie sicher, dass alle Anforderungen aus der Datei `requirements.txt` erfüllt sind.


1. Starten Sie die Anwendung mit:

        python app.py

oder führen Sie die Datei in einer Python-Entwicklungsumgebung Ihrer Wahl aus [vorzugsweise PyCharm ;)].


2. Nach dem Ausführen erscheint in der Konsole ein Link. Klicken Sie auf diesen Link, um das Dashboard zu öffnen.

    <img src="images/console-link.png" width="1810" alt="">


3. Das Dashboard öffnet sich standardmäßig mit der Teilnehmerübersicht.


4. Verwenden Sie den Schalter oben links, um zwischen Dark Mode und Light Mode zu wechseln.

    <img src="images/switch-dark.png" width="100" alt=""> <img src="images/switch-light.png" width="100" alt="">


5. Klicken Sie oben rechts auf die Schaltfläche „Jury Ansicht“. Geben Sie das Passwort im Popup-Fenster ein.

    <img src="images/password.png" width="300" alt="">


6. In der Juryansicht können Sie Punkte für jede Kür eingeben. Die Gesamtpunktzahl wird automatisch berechnet.


7. Die vollständige Punktetabelle wird automatisch in der Datenbank `points.db` gespeichert.

## Weiterführende Ideen

- Punkte der Teilnehmenden auf der Teilnehmerseite zusammen mit einer Rangliste anzeigen.  
- Auswahl bestimmter Jurymitglieder für Bewertung oder Übersicht ermöglichen, jeweils mit individuellem Passwort.