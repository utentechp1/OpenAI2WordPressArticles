# Progetto Demo

Questa demo, è in grado di pubblicare in maniera autonoma a partire da una lista di titoli, articoli di blog, uno per ogni titolo, completi di immagini, meta per i motori di ricerca (sfrutta il plugin RankMath)
Un esempio di blog generato da questo progetto è disponibile su [text](https://egreenkarma.com/). 
Tutti i contenuti disponibili su questo URL, sono stati generati in maniera completamente automatica da questo progetto Python.

py_wordpress/
│
├── venv/                  # Ambiente virtuale
├── src/                   # Codice sorgente del progetto
│   ├── __init__.py
│   ├── main.py            # Punto di ingresso principale dell'applicazione
│   ├── api_clients/       # Moduli per interagire con le diverse API
│   │   ├──__init__.py
│   |   ├── openai_client.py        # modulo per la comunicazione con OpenAI
│   |   └── wordpress_client.py     # modulo per la comunicazione con WordPress
│   └── db
│        ├──__init__.py
│        └── class-db.py   # Classe per la gestione del database 
│ 
├── .env                   # File per variabili d'ambiente
└── requirements.txt       # Dipendenze del progetto


# avviare l'ambiente virtuale
```bash
python3 -m venv venv        # creazione ambiente virtuale
source venv/bin/activate    # attivazione ambiente virtuale
deactivate                  # disattivazione ambiente virtuale
```

# Installazione delle dipendenze
```bash
pip install -r requirements.txt # per installare le dipendenze
pip-sync requirements.txt  # per sincronizzare le dipendenze
```

# importante modifica a WordPress
Aggiungere la costante nel wp-config.php la seguente riga per permettere l'upload di file
````php
define('ALLOW_UNFILTERED_UPLOADS', true);
````
