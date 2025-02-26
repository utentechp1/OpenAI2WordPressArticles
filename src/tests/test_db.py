import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)
from src.db.class_db import ContentDB


def test_insert_post_title(db):
    print("Testing insert_post_title...")
    title = "Test Post Title"
    post_id = db.insert_post_title(title)
    assert post_id is not None, "post_id should not be None"
    print("insert_post_title passed.")
    return post_id

def test_insert_post_meta(db, post_id):
    print("Testing insert_post_meta...")
    meta_key = "author"
    meta_value = "Test Author"
    db.insert_post_meta(post_id, meta_key, meta_value)
    db.c.execute("SELECT * FROM post_metas WHERE post_id=?", (post_id,))
    result = db.c.fetchone()
    assert result is not None, "Meta should be inserted"
    assert result[2] == meta_key and result[3] == meta_value, "Meta key and value should match"
    print("insert_post_meta passed.")

def test_insert_and_update_title_content(db, post_id):
    print("Testing insert_title and update_title_content...")
    title = "Test Content Title"
    content = "This is test content."
    title_id = db.insert_title(post_id, title)
    assert title_id is not None, "title_id should not be None"
    db.update_title_content(title_id, content)
    db.c.execute("SELECT * FROM titles_content WHERE title_id=?", (title_id,))
    result = db.c.fetchone()
    assert result is not None and result[3] == content, "Content should be updated"
    print("insert_and_update_title_content passed.")
    return title_id

def test_update_title_image(db, title_id):
    print("Testing update_title_image...")
    image_details = {
        "image_url": "http://example.com/image.jpg",
        "image_alt": "Test Image",
        "image_title": "Test Image Title",
        "image_caption": "Test Image Caption"
    }
    db.update_title_image(title_id, **image_details)
    db.c.execute("SELECT * FROM titles_content WHERE title_id=?", (title_id,))
    result = db.c.fetchone()
    assert all([result[i+4] == image_details[key] for i, key in enumerate(image_details)]), "Image details should be updated"
    print("update_title_image passed.")

def test_fetch_post_titles(db):
    print("Testing fetch_post_titles...")
    results = db.fetch_post_titles()
    assert results is not None and len(results) > 0, "Should fetch at least one title"
    print("fetch_post_titles passed.")

def test_fetch_titles_content(db, post_id):
    print("Testing fetch_titles_content...")
    results = db.fetch_titles_content(post_id)
    assert results is not None and len(results) > 0, "Should fetch content for the post_id"
    print("fetch_titles_content passed.")

def run_tests():
    if os.path.exists('test_database.db'):
        os.remove('test_database.db')
    db = ContentDB('test_database.db')
    post_id = test_insert_post_title(db)
    test_insert_post_meta(db, post_id)
    title_id = test_insert_and_update_title_content(db, post_id)
    test_update_title_image(db, title_id)
    test_fetch_post_titles(db)
    test_fetch_titles_content(db, post_id)
    db.close()
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
