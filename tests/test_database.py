import unittest
from unittest.mock import patch, MagicMock, mock_open
import psycopg2
from datetime import datetime
import uuid
import database
from image_structure import ImageStructure


class TestDatabase(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"host": "localhost", "user": "test"}')
    def test_load_db_config(self, mock_file):
        config = database.load_db_config("dummy_path.json")
        self.assertEqual(config, {"host": "localhost", "user": "test"})
        mock_file.assert_called_once_with("dummy_path.json", 'r')

    @patch("database.load_db_config")
    @patch("psycopg2.connect")
    def test_get_connection(self, mock_connect, mock_load_db_config):
        mock_load_db_config.return_value = {"host": "localhost"}
        conn = MagicMock()
        mock_connect.return_value = conn
        result = database.get_connection()
        mock_load_db_config.assert_called_once_with("db_config.json")
        mock_connect.assert_called_once_with(host="localhost")
        self.assertEqual(result, conn)

    @patch("uuid.uuid4")
    def test_insert_image_record(self, mock_uuid):
        mock_uuid.return_value = uuid.UUID("12345678123456781234567812345678")
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cur
        image_record = {
            "title": "Test Image",
            "batch_name": "Batch1",
            "url": "http://example.com/image.jpg",
            "downloaded_at": datetime(2024, 1, 1, 12, 0, 0),
            "image": b"binarydata"
        }
        database.insert_image_record(conn, image_record)
        cur.execute.assert_called_once()
        args, kwargs = cur.execute.call_args
        self.assertIn("INSERT INTO tb_images", args[0])
        self.assertEqual(args[1][0], str(mock_uuid.return_value))
        self.assertEqual(args[1][1], image_record["title"])
        self.assertEqual(args[1][2], image_record["batch_name"])
        self.assertEqual(args[1][3], image_record["url"])
        self.assertEqual(args[1][4], image_record["downloaded_at"])
        self.assertIsInstance(args[1][5], psycopg2.Binary)
        conn.commit.assert_called_once()

    def test_select_image(self):
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cur
        # Simulate DB row: id, title, batch_name, url, downloaded_at, image
        row = ("id123", "title1", "batchA", "http://url", datetime(2024, 1, 1, 12, 0, 0), b"imgdata")
        cur.fetchone.return_value = row
        gen = database.select_image(conn)
        result = next(gen)
        self.assertIsInstance(result, ImageStructure)
        self.assertEqual(result.id, row[0])
        self.assertEqual(result.title, row[1])
        self.assertEqual(result.batch_name, row[2])
        self.assertEqual(result.url, row[3])
        self.assertEqual(result.downloaded_at, row[4])
        self.assertEqual(result.image, row[5])

    def test_select_image_none(self):
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cur
        cur.fetchone.return_value = None
        gen = database.select_image(conn)
        with self.assertRaises(StopIteration):
            next(gen)

    def test_create_table(self):
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cur
        with patch("builtins.print") as mock_print:
            database.create_table(conn)
            cur.execute.assert_called_once()
            self.assertIn("CREATE TABLE IF NOT EXISTS tb_images", cur.execute.call_args[0][0])
            conn.commit.assert_called_once()
            mock_print.assert_called_with("Table 'tb_images' created successfully (or already exists).")

    def test_drop_table(self):
        conn = MagicMock()
        cur = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cur
        with patch("builtins.print") as mock_print:
            database.drop_table(conn)
            cur.execute.assert_called_once_with("DROP TABLE IF EXISTS tb_images;")
            conn.commit.assert_called_once()
            mock_print.assert_called_with("Table 'tb_images' dropped successfully.")


if __name__ == "__main__":
    unittest.main()
