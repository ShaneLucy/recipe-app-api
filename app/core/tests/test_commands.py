from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is available"""
        # override behaviour of connection handler to make it return true so
        # test case can continue
        with patch('django.db.utils.ConnectionHandler.__getitem__') \
                as get_item:
            get_item.return_value = True
            call_command('wait_for_db')

            self.assertEqual(get_item.call_count, 1)

    # replaces time.sleep with a mock function
    # that overrides time.sleep to true so test can
    # be executed faster as I don't have to wait for db
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, time_sleep):
        """Test waiting for db"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') \
                as get_item:
            # first 5 trys should raise operational error and sixth succeeds
            get_item.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')

            self.assertEqual(get_item.call_count, 6)
