import os
import tarfile
import random
import requests
import pickle
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from database import get_connection, insert_image_record

from PIL import Image
import io
import numpy as np
from numpy import ndarray

BASE_URL = "https://www.cs.toronto.edu/~kriz/"
DOWNLOAD_DIR = "image_sets"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_cifar_url():
    page = requests.get(BASE_URL + "cifar.html")
    soup = BeautifulSoup(page.content, "html.parser")
    links = soup.find_all("a", href=True)
    python_links = [lk for lk in links if "python.tar.gz" in lk["href"]]

    selected = random.choice(python_links)
    full_url = urljoin(BASE_URL, selected["href"])
    return full_url, selected["href"]


def download_image_set(url, local_filename):
    local_path = os.path.join(DOWNLOAD_DIR, local_filename)
    if os.path.exists(local_path):
        print(f"Imageset already exists: {local_filename}")
        return local_path

    print(f"Downloading imageset from {url}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path


def convert_to_jpeg_bytes(raw_bytes) -> bytes:
    raw_array: ndarray = np.frombuffer(raw_bytes, dtype=np.uint8)
    np_array = raw_array.reshape(3, 32, 32)

    np_array = np.transpose(np_array, (1, 2, 0))
    img = Image.fromarray(np_array)
    # Save Image as JPEG in memory
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def extract_images(tar_path, max_images=1000):
    images = []

    with tarfile.open(tar_path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if "data_batch" in m.name or "test_batch" in m.name or "train" in m.name]
        for member in members:
            file = tar.extractfile(member)
            if not file:
                continue
            data = pickle.load(file, encoding="bytes")

            for i in range(len(data[b"data"])):
                # image_bytes = data[b"data"][i].tobytes()
                image_bytes = convert_to_jpeg_bytes(data[b"data"][i])
                title = data[b"filenames"][i].decode() if b"filenames" in data else f"image_{i}.png"
                batch_label = data[b"batch_label"].decode() if b"batch_label" in data else f"batch_{i}"
                images.append((title, batch_label, image_bytes))

    random.shuffle(images)
    print(f"Extracted {len(images)} images, selecting up to {max_images}")
    return images[:max_images]


def insert_images_to_db(images, image_set_url):
    conn = get_connection()

    for title, batch_label, image_data in images:
        image_record = {
            'url': image_set_url,
            'title': title,
            'downloaded_at': datetime.utcnow(),
            'batch_name': batch_label,
            'image': image_data
        }
        insert_image_record(conn, image_record)
    print(f"Inserted the batch of images successfully.")


def download_and_store_images():
    image_set_url, filename = get_cifar_url()
    tar_path = download_image_set(image_set_url, filename)
    extracted_images = extract_images(tar_path, max_images=1000)
    insert_images_to_db(extracted_images, image_set_url)


if __name__ == "__main__":
    download_and_store_images()
