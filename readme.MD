This project automates the process of downloading CIFAR image datasets, storing images in a PostgreSQL database using Docker, and retrieving them on demand.

Project Structure

project/
├── docker-compose.yml        
├── requirements.txt          
├── create_table.py           
├── database.py               
├── download_images.py        
├── get_random_image_from_db
├── image_structure.py
├── Dockerfile
├── db_config.json
└── tests/
    └── test_create_table.py  # Unit tests

1. Docker Setup 
-- Start PostgreSQL with Docker Compose: 

Run cmd: docker-compose up -d

-- Credentials and ports are defined in docker-compose.yml.

-- If port 5432 is in use, we use:
ports:
  - "5433:5432"

2. Table Creation

Run: python create_table.py

3. Download & Store CIFAR Images

Run: python download_images.py

-- Randomly selects either CIFAR-10 or CIFAR-100 (Python version) from https://www.cs.toronto.edu/~kriz/cifar.html.

-- Downloads the archive only if not already present locally.

-- Extracts and stores up to 1000 images per run into PostgreSQL.

-- Images are converted to PNG before storage.

4. Retrieve a Random Image

Run: python get_random_image_from_db.py

-- Selects one random image from the database.

-- Writes it to a local file as random_image.png in the current directory.

5. Testing

Run: pytest tests/


Table schema:
id: string
title: string
batch_name: string
url: string
downloaded_at: datetime
image: bytes




