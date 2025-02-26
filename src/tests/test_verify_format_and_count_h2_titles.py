import re

def verify_format_and_count_h2_titles(generated_content):
    h2_count = 0
    format_correct = True
    
    for value in generated_content.values():
        # Cerca i tag di apertura e chiusura e i loro rispettivi numeri
        opening_tag_matches = re.match(r'^<h([1-6])>', value)
        closing_tag_matches = re.search(r'</h([1-6])>$', value)

        # Verifica che entrambi i match esistano e che i numeri dei tag corrispondano
        if not (opening_tag_matches and closing_tag_matches and opening_tag_matches.group(1) == closing_tag_matches.group(1)):
            format_correct = False
            break  # Interrompe al primo errore trovato
        
        if opening_tag_matches.group(1) == "2":
            h2_count += 1

    return h2_count, format_correct

# Esempio di utilizzo
generated_content = {
    "0": "<h2>Esplorando le sfide dei cambiamenti climatici</h2>",  # Formato errato
    "1": "<h3>L'impatto delle variazioni globali sull'ambiente e sulla società</h3>",
    "2": "<h4>Rischi e opportunità: come affrontare il cambiamento climatico</h4>",
    "3": "<h2>Innovazioni tecnologiche per un futuro sostenibile</h2>",
    # ecc...
}

h2_count, format_correct = verify_format_and_count_h2_titles(generated_content)
if format_correct:
    print(f"Il formato è corretto. Numero di titoli <h2> trovati: {h2_count}")
else:
    print("Il formato della risposta non è corretto.")
