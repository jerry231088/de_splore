from database import get_connection
from database import drop_table


def drop_images_table():
    conn = get_connection()
    try:
        drop_table(conn)
    except Exception as e:
        print(f"Error dropping table: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    drop_images_table()
