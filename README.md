# Podcaster

Sito creato per l'esame di Introduzione alle Applicazioni Web, edizione 2022-2023.

## Istruzioni per l'uso

1. Installare le dipendenze tramite il comando `pip install -r requirements.txt`
2. Inizializzare il database con il comando `flask --app podcaster init-db`
3. Far partire il sito con il comando `flask --app podcaster --debug run`

Il sito è pensato principalmente per un dispositivo fisso, ed è stato testato principalmente su uno schermo con risoluzione 1920x1080, ma è completamente Responsive.

## Utenti Preimpostati

| Nome Utente       | Email                         | Password | Tipo        |
| ----------------- | ----------------------------- | -------- | ----------- |
| Marco Rossi       | marco.rossi@example.org       | password | Creatore    |
| Giovanni Lombardi | giovanni.lombardi@example.org | password | Creatore    |
| Maria Giordano    | maria.giordano@example.org    | password | Creatore    |
| Giulia Bianchi    | giulia.bianchi@example.org    | password | Ascoltatore |
| Andrea Neri       | andrea.neri@example.org       | password | Ascoltatore |
| Roberto Verde     | roberto.verde@example.org     | password | Ascoltatore |

## Librerie Usate

Sono state usate le seguenti librerie:

- Flask, Flask Login, Flask Session, come da richiesta per la consegna.
- Bootstrap e bootstrap_flask.
- [python_dateutil](https://pypi.org/project/python-dateutil/), per semplificare il calcolo del tempo passato.
- [Pillow](https://pypi.org/project/Pillow/), per il resize delle immagini.
- [Mutagen](https://pypi.org/project/mutagen/), per determinare la lunghezza dei file audio.

## Note sul contenuto

- Le immagini sono state prese da [Unsplash](https://unsplash.com/).
- Le descrizioni e i titoli dei podcast sono stati generati da [ChatGPT](https://openai.com/blog/chatgpt/)
- Le immagini profilo degli utenti sono state generate da [thispersondoesnotexist.com](https://thispersondoesnotexist.com/)
- Le traccie audio sono state prese da [Incompetech](https://incompetech.com/music/royalty-free/music.html) (Musiche di Kevin MacLeod)
- La favicon è presa da [IconArchive](https://iconarchive.com/show/blue-election-icons-by-iconarchive/Election-Mic-Outline-icon.html)
