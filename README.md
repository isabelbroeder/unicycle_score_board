# Unicycle Dashboard

<p>
  🇬🇧 <a href="README.md">English</a> |
  🇩🇪 <a href="README.de.md">Deutsch</a>
</p>

## Project Description
The Unicycle Dashboard is a software tool designed to visualize and manage competition data for unicycle events. It integrates data from databases to provide both a participant overview and a jury overview.

The participant overview allows users to view relevant information about competitors and their routines. The jury overview enables jury members to enter scores for each individual routine. The total score per routine is calculated automatically and updated interactively.

## Project Scope and Goals
- Create databases from .xlsx files to store participant and routine information.
- Provide participant and jury overviews using integrated database data.
- Allow jury members to enter scores with automatic total calculation.
- Secure jury overview access using encrypted password authentication.

## Setup

What requirements must the .xlsx files fulfill?

The .xlsx files are used in the script `create_database.py` to create the databases `riders.db`, `routines.db`, and `riders_routines.db`, which are used by the application.

## How to Use

0. Make sure you fulfill the requirements in `requirements.txt`.


1. Run the application by executing:


        python app.py

or by running it in a python interpreter of your choice [preferably PyCharm ;)].


2. A link will appear in the console. Click on the link to access the dashboard.

    <img src="images/console-link.png" width="500" alt="">


3. The dashboard opens with the participant overview as the default page.


4. Use the switch in the top left corner to toggle between dark and light mode.

    <img src="images/switch-dark.png" width="100" alt=""> <img src="images/switch-light.png" width="100" alt="">


5. Click the "Jury Ansicht" button in the top right corner. Enter the password in the popup window.

    <img src="images/password.png" width="200" alt="">


6. In the jury view, you can enter scores for each routine. Total scores are calculated automatically.


7. The complete scoreboard is automatically saved in the database `points.db`.

## Further Ideas

- Show participants points along with a ranking on the participant page.
- Allow selecting specific judges for scoring or review with individual passwords.

