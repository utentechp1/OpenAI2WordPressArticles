import openai
from openai import OpenAI
from dotenv import load_dotenv
import time
import os
import sys
import json
import requests
from PIL import Image
from io import BytesIO
import re


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)
from src.db.class_db import ContentDB
from src.api_clients.wordpress_client import WordPressAPI

# Carica le variabili d'ambiente da un file .env
load_dotenv()

class OpenAIClient:

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Token API di OpenAI non configurato. Assicurati di impostarlo in un file .env.")
        openai.api_key = self.api_key
        self.db = ContentDB('database.db')
        self.wp = WordPressAPI()

    def send_to_gpt_generate_text(self, messages, model="gpt-3.5-turbo-0125", frequency_penalty=1.0, presence_penalty=1.0, temperature=1.0 ):
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            temperature=temperature,
            messages=messages
        )
        generated_content = completion.choices[0].message.content
        return generated_content

    def send_to_gpt_subtitles_request(self, messages):
        client = OpenAI()
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" },
        frequency_penalty=0.5,
        presence_penalty=0.5,
        temperature=0.8,
        messages=messages
        )
        generated_content = response.choices[0].message.content
        return generated_content
    
    def send_to_dalle(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        client = OpenAI()
        try:
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
            )
            images = [response.data[i].url for i in range(len(response.data))]
            return images
        except Exception as e:
            raise ValueError(f"Errore nella generazione dell'immagine: {e}")

    def verify_titles_format(self, content):
        format_correct = True
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as e:
                return False
        for value in content.values():
            opening_tag_matches = re.match(r'^<h([1-6])>', value)
            closing_tag_matches = re.search(r'</h([1-6])>$', value)
            if not (opening_tag_matches and closing_tag_matches and opening_tag_matches.group(1) == closing_tag_matches.group(1)):
                format_correct = False
                break       
        return format_correct

    def clean_titles(self, h2_titles):
        cleaned_titles = []
        for title in h2_titles:
            cleaned_title = re.sub(r'<\/?h2>', '', title)
            cleaned_titles.append(cleaned_title)
        return cleaned_titles

    def download_image(self, url, file_name):
        try:
            save_path="files/images_original/" + file_name
            response = requests.get(url)
            response.raise_for_status()  # Controlla per errori
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Immagine scaricata e salvata in: {save_path}")
        except Exception as e:
            print(f"Errore nel download dell'immagine: {e}")

    def download_image_and_compress(self, image_url, filename):
        if '.' not in filename.split('/')[-1]:  # Controlla l'ultimo segmento nel caso di percorsi
            imagename=filename
            filename += '.webp'
        else:        # Se il filename ha già un'estensione, sostituiscila con '.webp'
            imagename='.'.join(filename.split('.')[:-1])
            filename = '.'.join(filename.split('.')[:-1]) + '.webp'
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            webp_filename = filename.rsplit('.', 1)[0] + '.webp'
            path = "files/images/" + webp_filename
            image.save(path, 'WEBP', quality=80) 
            print(f"Downloaded and converted to WebP: {webp_filename}")
            return webp_filename , imagename
        else:
            print("Failed to download the image.")
            return False

#-------------------------- step 1 ----------------------------------------------

    def generate_sub_titles(self, post_id):
        if not self.db.verify_step_1(post_id):
            title=self.db.get_post_title_by_id(post_id)
            print("sto costruendo i titoli per i paragrafi..")
            h2_count=0
            format_correct=False
            generated_content=""
            print("generazione dei sottotitoli in corso..")
            while not format_correct:
                if not format_correct:
                    # sia se il formato non è corretto sia se è la prima iterazione, il punto di partenza è questo
                    messages=[
                        {"role": "system", "content": "Mi devi aiutare a costruire dei titoli SEO-Friendly per il mio blog e il risultato deve essere in formato json"},
                        {"role": "user", "content": "TITOLO: 'Comunità e Attivismo: Storie di successo e consigli per diventare attivisti ambientali' Genera titoli e sottotitoli in formato HTML (h2, h3, h4 e h5) in maniera sensata per sviluppare una pagina di un articolo, in maniera sensata e usando correttamente i tag h2, h3, h4 e h5"},
                        {"role": "assistant", "content": "{\"0\": \"<h2>Esplorando il cuore dell'attivismo ambientale</h2>\", \"1\": \"<h3>Le radici del movimento: una storia di passione e perseveranza</h3>\", \"2\": \"<h4>Da locale a globale: la diffusione dell'attivismo verde</h4>\", \"3\": \"<h2>Storie di successo che ispirano</h2>\", \"4\": \"<h3>Progetti innovativi per la salvaguardia dell'ambiente</h3>\", \"5\": \"<h4>Casistica di successo: come piccole azioni portano a grandi cambiamenti</h4>\", \"6\": \"<h2>Strumenti e strategie per diventare attivisti</h2>\", \"7\": \"<h3>Guida pratica all'attivismo: dal pensiero all'azione</h3>\", \"8\": \"<h4>Mobilizzare supporto e costruire una comunità</h4>\", \"9\": \"<h2>Risorse e formazione per attivisti emergenti</h2>\", \"10\": \"<h3>Apprendere dalle voci esperienze: workshop e corsi consigliati</h3>\", \"11\": \"<h4>Strumenti digitali per amplificare il tuo messaggio</h4>\", \"12\": \"<h2>Sfide e superamenti nell'attivismo ambientale</h2>\", \"13\": \"<h3>Affrontare l'opposizione: strategie di resilienza e persistenza</h3>\", \"14\": \"<h4>Celebrazioni di vittorie: riconoscere ogni passo avanti</h4>\"}"},
                        {"role": "user", "content":f"ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{title}'"}
                    ]      
                generated_content = self.send_to_gpt_generate_text(messages, "gpt-3.5-turbo-0125", -0.3,1.0, 0.2)
                print(generated_content)
                format_correct  = self.verify_titles_format(generated_content)
            
            print("aggiornamento del database..")
            if isinstance(generated_content, str):
                try:
                    generated_content = json.loads(generated_content)
                except json.JSONDecodeError as e:
                    print(f"Errore nella decodifica JSON: {e}")
                    return False
            for _, title in generated_content.items():
                self.db.insert_title(post_id, title)
                print(title)
            print("step 1 completato..\n")
            return True
        else:
            return True

#---------------------------step 2 ----------------------------------------------

    def generate_images_by_titles(self, post_id):
        if self.db.verify_post_featured_image(post_id):
            k=-1
            titles=[]
        else:
            post_title=self.db.get_post_title_by_id(post_id)
            k=-2
            titles=[post_title]
        titles_tabled=self.db.get_titles_content_without_image(post_id)      
        ids=[]
        for elem in titles_tabled:
            if elem[2].startswith("<h2>"):
                ids.append(elem[0])
                titles.append(elem[2])
        titles=self.clean_titles(titles)
        for title in titles:
            k+=1
            if k<2:
                if k==-1:
                    print(f"1: Sto costruendo una descrizione sensata per l'articolo: {title}\n")
                else:
                    print(f"1: Sto costruendo una descrizione sensata per un immagine da inserire sotto al titolo: {title}\n")
                messages=[
                    {"role": "system", "content": "Mi devi aiutare a creare dei testi per DALLE-3 per generare immagini. Preferisco sempre immagini che sembrano scattate da una macchina fotografica ad alta risoluzione."},
                    {"role": "user", "content": "TITOLO: \"Alba dei Biofotovoltaici: La Rivoluzione Verde nell'Energia Solare\" Genera un testo da inviare a DALLE-3 per ottenere un immagine attinente a questo paragrafo" },
                    {"role": "assistant", "content": "Creare un'immagine che sembri una fotografia ad alta risoluzione di un impianto biofotovoltaico all'aperto durante una giornata soleggiata. L'immagine deve mostrare dettagliatamente dei bio-reattori in vetro o plastica trasparente, posizionati in fila su supporti metallici o in legno. All'interno di ogni reattore, si dovrebbero vedere chiaramente strati di microalghe di un verde intenso, bagnati dalla luce del sole. Sullo sfondo, un cielo azzurro limpido con qualche nuvola sparsa, e all'orizzonte, una leggera linea di alberi o colline. L'aspetto complessivo dovrebbe essere naturale, come se l'immagine fosse stata scattata con una fotocamera professionale, catturando la texture e i dettagli dei bio-reattori e l'ambiente circostante."},
                    {"role": "user", "content":f"Ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{title}'"}
                ] 
                text=self.send_to_gpt_generate_text(messages)
                print(f"text: \"{text}\"\n") 
                print("2: Sto costruendo i metadati dell'immagine\n")
                messages=[
                        {"role": "system", "content": "Mi devi aiutare a costruire {filename}, {alt}, {title}, {caption} per un immagine in formato JSON"},
                        {"role": "user", "content": "Mi servono i tag filename, alt, title, caption dell'immagine che è stata creata a partire da questo input: \"Creare un'immagine che sembri una fotografia ad alta risoluzione di un impianto biofotovoltaico all'aperto durante una giornata soleggiata. L'immagine deve mostrare dettagliatamente dei bio-reattori in vetro o plastica trasparente, posizionati in fila su supporti metallici o in legno. All'interno di ogni reattore, si dovrebbero vedere chiaramente strati di microalghe di un verde intenso, bagnati dalla luce del sole. Sullo sfondo, un cielo azzurro limpido con qualche nuvola sparsa, e all'orizzonte, una leggera linea di alberi o colline. L'aspetto complessivo dovrebbe essere naturale, come se l'immagine fosse stata scattata con una fotocamera professionale, catturando la texture e i dettagli dei bio-reattori e l'ambiente circostante.\""},
                        {"role": "assistant", "content": "{\"filename\":\"impianto-biofotovoltaico.png\",\"alt\": \"Impianto biofotovoltaico all'aperto con bio-reattori contenenti microalghe verdi, sotto il sole.\", \"title\":\"Innovazione Verde: Biofotovoltaici in Azione\", \"caption\":\"Questo impianto biofotovoltaico sfrutta l'energia solare tramite microalghe, dimostrando il potenziale delle tecnologie rinnovabili di nicchia. Situato all'aperto, i bio-reattori catturano la luce solare, trasformandola in energia pulita in un perfetto equilibrio tra innovazione e natura.\" }"},
                        {"role": "user", "content":f"Ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{title}'"}
                    ]     
                all_keys_present=False
                while not all_keys_present:
                    meta_tags_gpt=self.send_to_gpt_generate_text(messages, model="gpt-4", temperature=0.2)
                    if isinstance(meta_tags_gpt, str):
                        try:
                            meta_tags = json.loads(meta_tags_gpt)
                            expected_keys = ["filename", "alt", "title", "caption"]
                            all_keys_present = all(key in meta_tags for key in expected_keys)
                        except json.JSONDecodeError as e:
                            all_keys_present = False
                filename=meta_tags["filename"]
                print(meta_tags)
                max_attempts=5
                attempts = 0
                image_ok=False
                print(f"\n3: Sto creando l'immagine con dall-e\n")
                try:
                    if k==-1:
                        images = self.send_to_dalle(prompt=text, model="dall-e-3", quality="hd")
                    else:
                        images = self.send_to_dalle(prompt=text, model="dall-e-3")
                    if images: 
                        image_ok=True
                except ValueError as e:
                    print(f"Tentativo di generare l'immagine fallito. Errore: {e}")
                if image_ok:
                    image_url = images[0] 
                    self.download_image(image_url, filename)
                    filename, imagename=self.download_image_and_compress(image_url, filename)
                    if filename:
                        print(f"4: Sto pubblicando l'immagine su WordPress\n")
                        response=self.wp.upload_image(filename,       
                        image_name=imagename,         
                        image_type='image/webp',
                        alt_text=meta_tags["alt"],         
                        title=meta_tags["title"],             
                        caption=meta_tags["caption"])
                        image_id = response['id']
                        image_url = response['media_details']['sizes']['full']['source_url']
                        print(f"5: Sto salvando i dati dell'immagine nel database locale\n")
                        if k==-1:
                            self.db.update_post_featured_image(post_id, image_id)
                        else:
                            self.db.update_title_image(ids[k],image_url,meta_tags["alt"],meta_tags["title"],meta_tags["caption"],image_id)
        return True

#---------------------------step 3 ----------------------------------------------

    def generate_paragraphs(self, post_id):
        post_title=self.db.get_post_title_by_id(post_id)
        
        messages_base=[
            {"role": "system", "content": "Sei un assistente per costruire paragrafi per un blog, cerca di suscitare interesse nel lettore, in modo da creare curiosità. Il contenuto deve essere SEO-Friendly e avere un tono amichevole"},
            {"role": "user", "content": "TITOLO:  \"<h2>Storie di successo nell'attivismo ambientale</h2>\"  Scrivi un contenuto interessante per questo titolo. Usa paragrafi corti delimitati dai tag HTML <p> e </p> e enfatizza le parti salienti con i tag HTML <b> e </b>"},
            {"role":"assistant", "content":"<p>È facile sentirsi sopraffatti dalle <b>notizie negative</b> che ci circondano quotidianamente, soprattutto quando si tratta di questioni ambientali. Tuttavia, <b>storie di successo nell'attivismo ambientale</b> esistono e dimostrano il potere che abbiamo nel creare un cambiamento positivo. Queste storie non solo offrono una boccata d'aria fresca ma fungono anche da <b>fonte d'ispirazione</b> per tutti noi. In questo blog, ti porteremo alla scoperta di alcune delle vittorie più significative nell'ambito dell'ambiente, raccontate direttamente dai protagonisti o dagli esperti del settore che hanno contribuito a renderle possibili.</p>\n\n<p>Da piccole iniziative comunitarie a grandi movimenti globali, i casi di successo nell'attivismo ambientale sono la prova vivente che l'impegno individuale e collettivo può davvero fare la differenza. Troverai storie affascinanti di come persone ordinarie hanno trasformato la loro passione per la natura in azioni concrete che hanno portato a <b>cambiamenti legislativi</b>, salvaguardia delle specie in via di estinzione, innovazioni sostenibili e molto altro ancora. Preparati a essere ispirato!</p>"},
        ]
        
        if not self.db.verify_post_content(post_id):
            print(f"TITOLO DELL'ARTICOLO: {post_title}\n")
            messages=[
                {"role": "system", "content": "Sei un assistente per costruire il primo paragrafo di un blog, cerca di suscitare interesse nel lettore, in modo da creare curiosità. Il contenuto deve essere SEO-Friendly e avere un tono amichevole"},
                {"role": "user", "content": "TITOLO: \"Comunità e Attivismo: Storie di successo e consigli per diventare attivisti ambientali\"  costruisci un paragrafo breve introduttivo, usando tag <p> </p> (paragrfi brevi)  e <b> </b> (per evidenziare concetti chiave)\" "},
                {"role":"assistant", "content":"<p>In un mondo dove il <b>cambiamento climatico</b> e la <b>degradazione ambientale</b> non sono più scenari ipotetici ma realtà con cui conviviamo quotidianamente, <b>l'urgenza di agire è palpabile</b>. Ma <b>come possiamo</b>, individualmente e collettivamente, <b>fare la differenza?</b> \"Comunità e Attivismo: Storie di successo e consigli per diventare attivisti ambientali\" si propone di esplorare proprio questo. Attraverso storie ispiratrici di persone che hanno trasformato la loro preoccupazione in azione, scopriremo come anche le piccole iniziative possono generare grandi cambiamenti. Se ti sei mai chiesto come poter contribuire alla salvaguardia del nostro pianeta, questo blog è il punto di partenza perfetto per intraprendere un viaggio verso un <b>attivismo efficace ed appassionato.</b></p>"},
                {"role": "user", "content":f"Ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{post_title}'"}
            ] 
            text=self.send_to_gpt_generate_text(messages,model="gpt-4",frequency_penalty=0.2,presence_penalty=1.0,temperature=0.8)
            print(text)
            self.db.update_post_content(post_id, text)
        
        titles_tabled=self.db.get_titles_rows(post_id)    
        ids=[]
        titles=[]
        for elem in titles_tabled:
            ids.append(elem[0])
            titles.append(elem[2])
        if ids:
            if not self.db.verify_title_content(ids[0]):
                print(f"TITOLO DEL PARAGRAFO: {titles[0]}\n")
                messages=messages_base
                messages.append({"role": "user", "content": f"role: user, content: Ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{titles[0]}'"})
                text=self.send_to_gpt_generate_text(messages,model="gpt-4", temperature=0.6)
                print(text)
                self.db.update_title_content(ids[0],text)
            for i in range(1, len(titles)):
                if not self.db.verify_title_content(ids[i]):
                    messages=messages_base
                    print(f"TITOLO DEL PARAGRAFO: {titles[i]}\n")
                    messages.append({"role": "user", "content": f"role: user, content: Ottimo lavoro!! Adesso fai lo stesso lavoro per il TITOLO: '{titles[i]}'"})
                    text=self.send_to_gpt_generate_text(messages,model="gpt-4-0125-preview", temperature=0.7)
                    print(text)
                    self.db.update_title_content(ids[i],text)
        return True    

#---------------------------step 4 ----------------------------------------------

    def publish_article_on_WordPress(self,post_id):
        post_title=self.db.get_post_title_by_id(post_id)
        featured_media_id=self.db.get_featured_media(post_id)
        text="<!-- wp:rank-math/toc-block -->\n<!-- /wp:rank-math/toc-block -->"
        first_content=self.db.get_post_content(post_id)
        text+="\n"+first_content
        titles_tabled=self.db.get_titles_rows(post_id)    
        for elem in titles_tabled:
            title=elem[2]
            paragraph=elem[3]
            image_link=elem[4]
            image_alt=elem[5]
            image_title=elem[6]
            image_caption=elem[7]
            if image_link:
                image_html = f"\n<!-- wp:image {{\"align\":\"center\",\"sizeSlug\":\"full\",\"linkDestination\":\"none\"}} -->\n<figure class=\"wp-block-image aligncenter size-full\"><img src=\"{image_link}\" alt=\"{image_alt}\" title=\"{image_title}\" /><figcaption class=\"wp-element-caption\">{image_caption}</figcaption></figure>\n<!-- /wp:image -->"
                p_close_index = paragraph.find('</p>')
                if p_close_index != -1:
                    paragraph = paragraph[:p_close_index + 4] + image_html + paragraph[p_close_index + 4:]
                else:
                    paragraph += image_html              
            text += "\n\n" + title
            text += "\n\n" + paragraph
        print("sto generando i meta tags per l'articolo..")
        messages=[
            {"role": "system", "content": "Sei un assistente per costruire meta-tags per un articolo del mio blog in formato JSON"},
            {"role": "user", "content": "Mi aspetto una risposta con tutti i tag riempiti. Esempio di risposta attesa: {\"slug\": \"comunita-e-attivismo-storie-di-successo\",\"excerpt\": \"<p>La sostenibilità è diventata una priorità per molte persone in tutto il mondo. Sempre più individui, organizzazioni e comunità si stanno impegnando per fare la differenza e contribuire a un futuro migliore per il nostro pianeta. In questo articolo, esploreremo alcune storie di successo nel campo dell'attivismo e forniremo consigli su come diventare attivisti ambientali.</p>\n\",\"description\": \"Scopri storie di successo di attivismo ambientale e divertiti con consigli per diventare un attivista ambientale. Unisciti a noi per un futuro sostenibile!\",\"keywords\": \"attivismo ambientale, sostenibilità, successo, cambiamento\",\"title_SEO\": \"Attivismo Ambientale: Successi e Suggerimenti per un Cambiamento Sostenibile!\"}" },
            {"role": "user", "content": "RACCOMANDAZIONE MOLTO IMPORTANTE: Rispetta esattamente il formato, inserisci più keywords possibile, slug corto!"},
            {"role": "user", "content": f"TITOLO DELL'ARTICOLO:  {post_title}"}
        ]
        all_keys_present=False
        while not all_keys_present:
            meta_tags_gpt=self.send_to_gpt_generate_text(messages,model="gpt-4-0125-preview",frequency_penalty=0.2,presence_penalty=0.3,temperature=0.1)
            if isinstance(meta_tags_gpt, str):
                try:
                    meta_tags = json.loads(meta_tags_gpt)
                    print(meta_tags)
                    expected_keys = ["slug", "excerpt", "description", "title_SEO", "keywords"]
                    all_keys_present = all(key in meta_tags for key in expected_keys)
                except json.JSONDecodeError as e:
                    all_keys_present = False
        text+="\n\n\n Tags Suggeriti: " + meta_tags["keywords"]
        metas = {}
        metas["rank_math_description"]=meta_tags["description"]
        metas["rank_math_focus_keyword"]=meta_tags["keywords"]
        metas["rank_math_title"]=meta_tags["title_SEO"]
        self.wp.create_post(title=post_title,
                            content=text,
                            excerpt=meta_tags["excerpt"],
                            metas=metas,
                            featured_media_id=featured_media_id,
                            slug=meta_tags["slug"]
                            )
        print("articolo pubblicato con successo..")
        self.db.set_post_as_published(post_id)


# funzioni di prova..
def try__more_images_generation():
    client = OpenAIClient()
    image_prompt = "Un esploratore spaziale che osserva un misterioso pianeta pieno di foreste e oceani alieni."
    generated_images = client.send_to_dalle(image_prompt)
    print(generated_images)
    for idx, image_url in enumerate(generated_images):
        filename = f"space_explorer_image_{idx}.png"
        client.download_image(image_url, filename)
        print(f"Downloaded {filename}")
        
def try_generate_paragraph():
    client = OpenAIClient()
    generated_text = client.generate_paragraph()
    print(generated_text)
    return client

def try_generate_sub_titles():
    client = OpenAIClient()
    generated_text = client.generate_sub_titles("Cambiamenti Climatici: Innovazioni e Soluzioni per un Futuro Sostenibile", 1)
    return client

def try_image_generation():
    client = OpenAIClient()
    image_prompt = "Un esploratore spaziale che osserva un misterioso pianeta pieno di foreste e oceani alieni."
    generated_images = client.send_to_dalle(image_prompt) 
    if generated_images:  
        image_url = generated_images[0] 
        filename = "space_explorer_image1.cazzo"
        client.download_image_and_compress(image_url, filename)
        print(f"Downloaded {filename}")
    else:
        print("Non è stata generata alcuna immagine.")

if __name__ == "__main__":
    client = OpenAIClient()
    id=6
    # client.generate_sub_titles(id)
    # client.generate_images_by_titles(id)
    # client.generate_paragraphs(id)
    client.publish_article_on_WordPress(id)

