import io
import tarfile
import pickle
import pytest
import numpy as np
from unittest import mock
import download_images


@pytest.fixture
def fake_cifar_html():
    return """
    <html>
        <body>
            <a href="cifar-10-python.tar.gz">CIFAR-10 Python</a>
            <a href="cifar-100-python.tar.gz">CIFAR-100 Python</a>
        </body>
    </html>
    """


def test_get_cifar_url_selects_python_tar_gz(fake_cifar_html):
    with mock.patch("requests.get") as mock_get:
        mock_get.return_value.content = fake_cifar_html.encode()
        url, href = download_images.get_cifar_url()
        assert url.startswith(download_images.BASE_URL)
        assert href.endswith("python.tar.gz")


def test_download_image_set_downloads_and_saves(tmp_path):
    url = "http://example.com/file.tar.gz"
    filename = "file.tar.gz"
    local_path = tmp_path / filename

    with mock.patch("os.path.exists", return_value=False), \
         mock.patch("builtins.open", mock.mock_open()) as m_open, \
         mock.patch("requests.get") as m_get:
        m_get.return_value.__enter__.return_value.iter_content = lambda chunk_size: [b"abc", b"def"]
        m_get.return_value.__enter__.return_value.raise_for_status = lambda: None
        result = download_images.download_image_set(url, filename)
        assert result.endswith(filename)
        assert m_open.called

    with mock.patch("os.path.exists", return_value=True):
        result = download_images.download_image_set(url, filename)
        assert result.endswith(filename)


def test_convert_to_jpeg_bytes_returns_bytes():
    arr = np.random.randint(0, 255, size=(3*32*32,), dtype=np.uint8)
    result = download_images.convert_to_jpeg_bytes(arr.tobytes())
    assert isinstance(result, bytes)
    assert result[:8] == b'\x89PNG\r\n\x1a\n'


def make_fake_tarfile(tmp_path, batch_name="data_batch_1", num_images=2):
    data = {
        b"data": np.random.randint(0, 255, size=(num_images, 3*32*32), dtype=np.uint8),
        b"filenames": [f"img_{i}.png".encode() for i in range(num_images)],
        b"batch_label": b"training batch 1 of 5"
    }
    batch_bytes = io.BytesIO()
    pickle.dump(data, batch_bytes)
    batch_bytes.seek(0)

    tar_path = tmp_path / "test.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        info = tarfile.TarInfo(name=batch_name)
        info.size = len(batch_bytes.getvalue())
        batch_bytes.seek(0)
        tar.addfile(info, batch_bytes)
    return tar_path


def test_extract_images_reads_and_returns_images(tmp_path):
    tar_path = make_fake_tarfile(tmp_path)
    images = download_images.extract_images(str(tar_path), max_images=2)
    assert len(images) == 2
    for title, batch, img_bytes in images:
        assert title.endswith(".png")
        assert isinstance(batch, str)
        assert isinstance(img_bytes, bytes)


def test_insert_images_to_db_calls_insert(monkeypatch):
    fake_conn = object()
    called = []
    def fake_insert(conn, record):
        called.append((conn, record))
    monkeypatch.setattr(download_images, "get_connection", lambda: fake_conn)
    monkeypatch.setattr(download_images, "insert_image_record", fake_insert)
    images = [("title1", "batch1", b"img1"), ("title2", "batch2", b"img2")]
    url = "http://example.com"
    download_images.insert_images_to_db(images, url)
    assert len(called) == 2
    for conn, record in called:
        assert conn is fake_conn
        assert record["url"] == url
        assert "title" in record
        assert "batch_name" in record
        assert isinstance(record["image"], bytes)


def test_download_and_store_images_integration(monkeypatch, tmp_path):
    # Patch all sub-functions to simulate workflow
    monkeypatch.setattr(download_images, "get_cifar_url", lambda: ("http://example.com/fake.tar.gz", "fake.tar.gz"))
    monkeypatch.setattr(download_images, "download_image_set", lambda url, fn: str(make_fake_tarfile(tmp_path)))
    monkeypatch.setattr(download_images, "extract_images", lambda tar, max_images=1000: [("t", "b", b"img")])
    called = []
    monkeypatch.setattr(download_images, "insert_images_to_db", lambda imgs, url: called.append((imgs, url)))
    download_images.download_and_store_images()
    assert called
    imgs, url = called[0]
    assert url == "http://example.com/fake.tar.gz"
    assert imgs == [("t", "b", b"img")]
