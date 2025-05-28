import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from get_random_image_from_db import get_random_image
from image_structure import ImageStructure
from datetime import datetime


class TestGetRandomImage(unittest.TestCase):
    @patch("get_random_image_from_db.get_connection")
    @patch("get_random_image_from_db.select_image")
    @patch("builtins.open", new_callable=mock_open)
    @patch("get_random_image_from_db.Path")
    def test_get_random_image_success(self, mock_path, mock_open_file, mock_select_image, mock_get_connection):
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_path.return_value = Path("random_image.png")

        image = ImageStructure(
            id="1",
            title="Test Image",
            batch_name="Batch1",
            url="http://example.com/image.png",
            downloaded_at=datetime.now(),
            image=b"fakeimagedata"
        )
        mock_select_image.return_value = [image]

        with patch("builtins.print") as mock_print:
            get_random_image()

        mock_get_connection.assert_called_once()
        mock_select_image.assert_called_once_with(mock_conn)
        mock_open_file.assert_called_once_with(Path("random_image.png"), "wb")
        mock_open_file().write.assert_called_once_with(b"fakeimagedata")
        mock_conn.close.assert_called_once()

        printed = [str(call) for call in mock_print.call_args_list]
        assert any("Random image is fetched from database" in line for line in printed)
        assert any("ID: 1, Title: Test Image" in line for line in printed)

    @patch("get_random_image_from_db.get_connection")
    @patch("get_random_image_from_db.select_image")
    @patch("builtins.open", new_callable=mock_open)
    @patch("get_random_image_from_db.Path")
    def test_get_random_image_no_images(self, mock_path, mock_open_file, mock_select_image, mock_get_connection):
        # Setup
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_path.return_value = Path("random_image.png")
        mock_select_image.return_value = []

        with patch("builtins.print") as mock_print:
            get_random_image()

        mock_open_file.assert_not_called()
        mock_conn.close.assert_called_once()

    @patch("get_random_image_from_db.get_connection")
    @patch("get_random_image_from_db.select_image")
    @patch("builtins.open", new_callable=mock_open)
    @patch("get_random_image_from_db.Path")
    def test_get_random_image_exception(self, mock_path, mock_open_file, mock_select_image, mock_get_connection):
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn
        mock_path.return_value = Path("random_image.png")
        mock_select_image.side_effect = Exception("DB error")

        with patch("builtins.print") as mock_print:
            result = list(get_random_image())

        mock_get_connection.assert_called_once()
        mock_select_image.assert_called_once_with(mock_conn)
        mock_open_file.assert_not_called()
        self.assertEqual(result, [])
        mock_conn.close.assert_called_once()
        self.assertTrue(any("Error fetching random image" in str(call) for call in mock_print.call_args_list))


if __name__ == "__main__":
    unittest.main()
