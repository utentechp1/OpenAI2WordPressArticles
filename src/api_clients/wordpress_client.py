import os
import sys
import requests
import json
import base64
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)
from src.db.class_db import ContentDB

class WordPressAPI:
    def __init__(self):
        self.domain = os.getenv('WORDPRESS_DOMAIN')
        self.rest_url = f'https://{self.domain}/wp-json/wp/v2'
        self.username = os.getenv('WORDPRESS_USER')
        self.password = os.getenv('WORDPRESS_PASSWORD')

    def get_headers(self):
        # Codifica le credenziali in Base64 per l'autenticazione Basic
        credentials = f'{self.username}:{self.password}'
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {
            'Authorization': f'Basic {encoded_credentials}'
        }
        
    def clean_slug(self, slug):
        slug = slug.replace(" ", "-")
        slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
        slug = slug.lower()
        return slug

    def get_posts(self):
        headers = self.get_headers()
        response = requests.get(f'{self.rest_url}/posts', headers=headers)
        return response.json()
    
    def get_post_by_id(self, post_id):
        headers = self.get_headers()
        response = requests.get(f'{self.rest_url}/posts/{post_id}', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return f'Error: {response.status_code}'

    def create_post(self, title, content, status='draft', excerpt=None, metas=None, categories=None, tags=None, featured_media_id=None, slug=None):
        headers = self.get_headers()
        data = {
            'title': title,
            'content': content,
            'status': status
        }
        if excerpt is not None:
            data['excerpt'] = excerpt
        if metas is not None:
            data['metas'] = metas 
        if categories is not None:
            data['categories'] = categories if isinstance(categories, list) else [categories]
        if tags is not None:
            data['tags'] = tags if isinstance(tags, list) else [tags]
        if featured_media_id is not None:
            data['featured_media'] = featured_media_id
        if slug is not None:
            data['slug'] = self.clean_slug(slug)
        response = requests.post(f'{self.rest_url}/posts', headers=headers, json=data)
        return response.json()
    
    def upload_image(self, image_filename, image_name=None, image_type='image/jpeg', alt_text='', title='', description='', caption=''):
        image_path="files/images/" + image_filename
        headers = self.get_headers()
        if image_name is None:
            image_name = image_path.split('/')[-1]
        with open(image_path, 'rb') as image:
            files = {
                'file': (image_name, image, image_type)
            }
            response = requests.post(f'{self.rest_url}/media', headers=headers, files=files)    
        if response.status_code == 201:
            upload_response = response.json()
            media_id = upload_response['id']

            # Seconda parte: Aggiornamento dei metadati dell'immagine.
            media_data = {
                'alt_text': alt_text,
                'title': title,
                'description': description,
                'caption': caption
            }        
            update_response = requests.post(f'{self.rest_url}/media/{media_id}', headers=headers, json=media_data)
            return update_response.json()
        else:
            return response.json()

if __name__ == "__main__":
    wp_api=WordPressAPI()
    response = wp_api.upload_image('space_explorer_image.webp',         
        image_name='TestImage',         
        image_type='image/webp',
        alt_text='Un bellissimo paesaggio',         
        title='Titolo Immagine',        
        description='Descrizione dell\'immagine',         
        caption='Didascalia dell\'immagine')
    image_id = response['id']
    image_url = response['media_details']['sizes']['full']['source_url']
    print(f"ID: {image_id}, URL: {image_url}")
