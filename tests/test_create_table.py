import unittest
from unittest.mock import patch, MagicMock
import io
import create_table


class TestCreateImagesTable(unittest.TestCase):
    @patch('create_table.create_table')
    @patch('create_table.get_connection')
    def test_create_images_table_success(self, mock_get_connection, mock_create_table):
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn

        create_table.create_images_table()

        mock_get_connection.assert_called_once()
        mock_create_table.assert_called_once_with(mock_conn)
        mock_conn.close.assert_called_once()

    @patch('create_table.create_table', side_effect=Exception("DB Error"))
    @patch('create_table.get_connection')
    def test_create_images_table_exception(self, mock_get_connection, mock_create_table):
        mock_conn = MagicMock()
        mock_get_connection.return_value = mock_conn

        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            create_table.create_images_table()
            output = fake_out.getvalue()

        mock_get_connection.assert_called_once()
        mock_create_table.assert_called_once_with(mock_conn)
        mock_conn.close.assert_called_once()

        self.assertIn("Error creating table: DB Error", output)


if __name__ == '__main__':
    unittest.main()

