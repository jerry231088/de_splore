from database import get_connection
from database import create_table


def create_images_table():
    conn = get_connection()
    try:
        create_table(conn)
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    create_images_table()
