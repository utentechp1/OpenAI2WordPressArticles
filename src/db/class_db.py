import sqlite3

class ContentDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.c = self.conn.cursor()
        self.setup_db()

    def setup_db(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS post_titles 
            (post_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, featured_image INTEGER, content TEXT, content_assembled TEXT, published INTEGER)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS titles_content
            (title_id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, title TEXT,
            content TEXT, image_url TEXT, image_alt TEXT, image_title TEXT, image_caption TEXT,
            FOREIGN KEY(post_id) REFERENCES post_titles(post_id))''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS post_metas
            (meta_id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, meta_key TEXT, meta_value TEXT, 
            FOREIGN KEY(post_id) REFERENCES post_titles(post_id))''')
        self.conn.commit()

    def add_missing_columns(self):
        try:
            # Aggiungi una colonna alla tabella post_titles
            # Aggiungere la colonna content_assembled di tipo TEXT
            self.c.execute("ALTER TABLE post_titles ADD COLUMN content_assembled TEXT")

            # Aggiungere la colonna published di tipo INTEGER come rappresentazione booleana
            self.c.execute("ALTER TABLE post_titles ADD COLUMN published INTEGER")

            # Aggiungi un'altra colonna alla tabella titles_content
            # self.c.execute("ALTER TABLE titles_content ADD COLUMN image_id INTEGER")
            self.conn.commit()
        except sqlite3.OperationalError as e:
            print(f"Errore nell'aggiungere colonne: {e}")

    def delete_all_related_to_post_id(self, post_id):
        self.c.execute("DELETE FROM post_metas WHERE post_id = ?", (post_id,))
        self.c.execute("DELETE FROM titles_content WHERE post_id = ?", (post_id,))
        self.c.execute("DELETE FROM post_titles WHERE post_id = ?", (post_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

#------------ table post_titles -------------------------------------------------------------------------------------------

    def insert_post_title(self, title):
        self.c.execute("INSERT INTO post_titles (title, published) VALUES (?, ?)", (title, 0))
        self.conn.commit()
        return self.c.lastrowid

    def verify_post_featured_image(self, post_id):
        self.c.execute("SELECT featured_image FROM post_titles WHERE post_id=?", (post_id,))     
        x=self.c.fetchall()[0][0]
        if isinstance(x, int) and x > 0:
            return True
        else:
            return False

    def verify_post_content(self, post_id):
        self.c.execute("SELECT content FROM post_titles WHERE post_id=?", (post_id,))     
        x=self.c.fetchall()[0][0]
        if x:
            return True
        else:
            return False

    def get_post_titles(self):
        self.c.execute("SELECT * FROM post_titles")
        post_titles= self.c.fetchall()
        return post_titles

    def get_post_title_by_id(self, post_id):
        self.c.execute("SELECT title FROM post_titles WHERE post_id=?",(post_id,))
        content= self.c.fetchall()[0][0]
        return content

    def get_post_content(self, post_id):
        self.c.execute("SELECT content FROM post_titles WHERE post_id=?",(post_id,))
        post_title= self.c.fetchall()[0][0]
        return post_title

    def get_featured_media(self, post_id):
        self.c.execute("SELECT featured_image FROM post_titles WHERE post_id=?",(post_id,))
        post_title= self.c.fetchall()[0][0]
        return post_title

    def update_post_content(self, post_id, content):
        self.c.execute("UPDATE post_titles SET content=? WHERE post_id=?",
            (content, post_id))
        self.conn.commit()

    def update_post_featured_image(self, post_id, featured_image_id):
        self.c.execute("UPDATE post_titles SET featured_image=? WHERE post_id=?",
            (featured_image_id, post_id))
        self.conn.commit()

    def update_post_content_assembled(self, post_id, content_assembled):
        self.c.execute("UPDATE post_titles SET featured_image=? WHERE post_id=?",
            (content_assembled, post_id))
        self.conn.commit()       

    def set_post_as_published(self, post_id):
        self.c.execute("UPDATE post_titles SET published=? WHERE post_id=?", (1, post_id))
        self.conn.commit()

#------------ table titles_content ---------------------------------------------------------------------------------------

    def insert_title(self, post_id, title):
        self.c.execute("INSERT INTO titles_content (post_id, title) VALUES (?, ?)",
            (post_id, title))
        self.conn.commit()
        return self.c.lastrowid

    def verify_step_1(self, post_id):
        self.c.execute("SELECT title FROM titles_content WHERE post_id=?", (post_id,))     
        x=self.c.fetchall()
        if x:
            return True
        else:
            return False

    def verify_title_content(self, title_id):
        self.c.execute("SELECT content FROM titles_content WHERE title_id=?", (title_id,))     
        x=self.c.fetchall()[0][0]
        if x:
            return True
        else:
            return False

    def get_titles_rows(self, post_id):
        self.c.execute("SELECT * FROM titles_content WHERE post_id=?", (post_id,))
        titles_content= self.c.fetchall()
        return titles_content

    def get_titles_rows_without_generated_image(self, post_id):
        self.c.execute("SELECT * FROM titles_content WHERE post_id=?  AND (image_url IS NULL OR image_url = '')", (post_id,))
        titles_content= self.c.fetchall()
        return titles_content

    def get_titles_content_without_image(self, post_id):
        self.c.execute("SELECT * FROM titles_content WHERE post_id=?  AND (image_url IS NULL OR image_url = '')", (post_id,))
        titles_content= self.c.fetchall()
        return titles_content

    def update_title_content(self, title_id, content=""):
        self.c.execute("UPDATE titles_content SET content=? WHERE title_id=?",
            (content, title_id))
        self.conn.commit()

    def update_title_image(self, title_id, image_url="", image_alt="", image_title="", image_caption="", image_id=""):
        self.c.execute("UPDATE titles_content SET image_url=?, image_alt=?, image_title=?, image_caption=?, image_id=? WHERE title_id=?",
            (image_url, image_alt, image_title, image_caption, image_id, title_id))
        self.conn.commit()      

#------------ table post_metas --------------------------------------------------------------------------------------------

    def insert_post_meta(self, post_id, meta_key, meta_value):
        self.c.execute("INSERT INTO post_metas (post_id, meta_key, meta_value) VALUES (?, ?, ?)",
            (post_id, meta_key, meta_value))
        self.conn.commit()

if __name__== "__main__":
    db = ContentDB('database.db')
    #db.add_missing_columns()
    print(db.get_titles_rows(2))
