from typing import Iterator
from database import get_connection, select_image
from image_structure import ImageStructure
from pathlib import Path


def get_random_image() -> Iterator[ImageStructure]:
    conn = get_connection()
    try:
        output_file = Path("random_image.png")
        for image in select_image(conn):
            print(f"ID: {image.id}, Title: {image.title}, Batch Name: {image.batch_name}, URL: {image.url}")
            with open(output_file, "wb") as f:
                f.write(image.image)

        print(f"Random image is fetched from database and stored at {output_file.resolve()}")

    except Exception as e:
        print(f"Error fetching random image: {e}")
        return iter([])
    finally:
        conn.close()


if __name__ == '__main__':
    get_random_image()
