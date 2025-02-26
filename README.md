# comandi
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