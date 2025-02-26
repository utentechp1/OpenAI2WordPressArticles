import os
import argparse
import json
import re
from dotenv import load_dotenv
from api_clients.wordpress_client import WordPressAPI
from api_clients.openai_client import OpenAIClient
from db.class_db import ContentDB

# Carica le variabili d'ambiente dal file .env
load_dotenv()

def insert_titles_in_database(file_input):
    file_input="files/"+file_input
    db = ContentDB("database.db")
    pattern = r'^\d+\.*\s*|"'
    k=0
    with open(file_input, 'r', encoding='utf-8') as fin:
        for linea in fin:
            linea_pulita = re.sub(pattern, '', linea).strip()  # .strip() per rimuovere spazi bianchi iniziali/finali
            db.insert_post_title(linea_pulita)
            k+=1
    print(f"inseriti {k} titoli nel database")

def main():
    # Preparazione dell'argparse e definizione degli argomenti come mostrato precedentemente
    parser = argparse.ArgumentParser(description='WordPress CLI tool')
    parser.add_argument('--get', type=int, help='Get a post by its ID')
    parser.add_argument('--save', type=str, help='File name to save the post details')
    parser.add_argument('--create', action='store_true', help='Create a new post')
    parser.add_argument('--title', type=str, help='Title of the post to create', default='')
    parser.add_argument('--content', type=str, help='Content of the post to create', default='')
    parser.add_argument('--output', type=str, help='File name to save the new post details in JSON format')
    parser.add_argument('--json', type=str, help='JSON file with post details to create a new post')
    parser.add_argument('--status', type=str, choices=['publish', 'draft'], default='draft', help='Post status: publish or draft')
    parser.add_argument('--db_insert_titles', type=str, help='Path to the file containing titles to insert in the database')
    
    args = parser.parse_args()
    wp_api = WordPressAPI()
    #python src/main.py --db_insert_titles titles.txt     
    if args.db_insert_titles:
        insert_titles_in_database(args.db_insert_titles)
        print(f"Titles from {args.db_insert_titles} have been inserted into the database.")

    # python src/main.py --create --title "Cambiamenti Climatici: Innovazioni e Soluzioni per un Futuro Sostenibile"
    if args.create and args.title:
        db = ContentDB('database.db')  # Sostituisci con il nome corretto del tuo database
        post_id = db.insert_post_title(args.title)
        print(f"Post titled '{args.title}' created with ID: {post_id}")
        db.close()  
        return
    # python src/main.py --get 89 --save post_details.json
    if args.get:
        post_id = args.get
        post = wp_api.get_post_by_id(post_id)
        if args.save:
            file_name = args.save
            with open(file_name, 'w') as json_file:
                json.dump(post, json_file, indent=4, ensure_ascii=False)
            print(f"Post details saved in {file_name}")
        else:
            print(post)
        return

    if args.json:
        if os.path.exists(args.json):
            with open(args.json, 'r') as json_file:
                post_details = json.load(json_file)
            args.title = post_details.get('title', '')
            args.excerpt = post_details.get('excerpt', '')
            args.metas = post_details.get('metas', '')
            args.categories = post_details.get('categories','')
            args.tags =  post_details.get('tags', '')
            args.featured_media = post_details.get('featured_media', '')
            args.slug = post_details.get('slug', '')
            
            # Determina il nome del file di testo dal nome del file JSON
            txt_filename = os.path.splitext(args.json)[0] + '.txt'
            if os.path.exists(txt_filename):
                with open(txt_filename, 'r') as txt_file:
                    args.content = txt_file.read()
            else:
                print(f"No content file found matching {txt_filename}. Using content from JSON or default.")
        else:
            print(f"JSON file {args.json} not found.")
    # python src/main.py --create --json post_details.json
    if args.create:
        if not args.title or not args.content:
            print("Creating a post requires both title and content.")
            return
        response = wp_api.create_post(args.title, args.content, 'draft', args.excerpt, args.metas, args.categories, args.tags, args.featured_media, args.slug)
        print("Post created successfully:", response['id'])
        if args.output:
            post_data = {'title': args.title, 'content': args.content}
            with open(args.output, 'w') as json_file:
                json.dump(post_data, json_file, indent=4, ensure_ascii=False)
            print(f"New post details saved in {args.output}")



if __name__ == "__main__":
    main()