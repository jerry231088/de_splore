import psycopg2
import json
import uuid
from image_structure import ImageStructure


def load_db_config(path="db_config.json"):
    with open(path, 'r') as f:
        return json.load(f)


def get_connection():
    config = load_db_config("db_config.json")
    return psycopg2.connect(**config)


def insert_image_record(conn, image_record):
    insert_image_qeury = """
            INSERT INTO tb_images (id, title, batch_name, url, downloaded_at, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
    with conn.cursor() as cur:
        cur.execute(insert_image_qeury, (
            str(uuid.uuid4()),
            image_record['title'],
            image_record['batch_name'],
            image_record['url'],
            image_record['downloaded_at'],
            psycopg2.Binary(image_record['image'])
        ))
        conn.commit()


def select_image(conn):
    select_image_query = """
            SELECT id, title, batch_name, url, downloaded_at, image
            FROM tb_images
            ORDER BY RANDOM()
            LIMIT 1;
        """
    with conn.cursor() as cur:
        cur.execute(select_image_query)
        row = cur.fetchone()
        if row:
            yield ImageStructure(
                id=row[0],
                title=row[1],
                batch_name=row[2],
                url=row[3],
                downloaded_at=row[4],
                image=row[5]
            )


def create_table(conn):
    create_table_query = """
        CREATE TABLE IF NOT EXISTS tb_images (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            batch_name TEXT NOT NULL,
            url TEXT NOT NULL,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image BYTEA NOT NULL
        );
        """
    with conn.cursor() as cur:
        cur.execute(create_table_query)
        conn.commit()
        print("Table 'tb_images' created successfully (or already exists).")


def drop_table(conn):
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS tb_images;")
        conn.commit()
        print("Table 'tb_images' dropped successfully.")

