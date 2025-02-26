# Progetto Demo

Questa demo, è in grado di pubblicare in maniera autonoma a partire da una lista di titoli, articoli di blog, uno per ogni titolo, completi di immagini, metadati per i motori di ricerca (sfrutta il plugin RankMath)
Un esempio di blog generato da questo progetto è disponibile su [egreenkarma.com](https://egreenkarma.com/). 
Tutti i contenuti disponibili su questo URL, sono stati generati in maniera completamente automatica da questo progetto Python.


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
