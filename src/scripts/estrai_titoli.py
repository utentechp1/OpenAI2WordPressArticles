import re

def rimuovi_virgolette_da_file(file_input, file_output):
    pattern = r'^\d+\.*\s*|"'
    
    with open(file_input, 'r', encoding='utf-8') as fin, open(file_output, 'w', encoding='utf-8') as fout:
        for linea in fin:
            linea_pulita = re.sub(pattern, '', linea)
            fout.write(linea_pulita)

file_input = 'src/script_utili/titles.txt'
file_output = 'src/script_utili/output.txt'
rimuovi_virgolette_da_file(file_input, file_output)