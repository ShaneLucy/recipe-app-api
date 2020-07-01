import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution of db until db is available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        # while db connection isn't set, try setting it or except error
        # operational error and retry in 1 second
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavilable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available'))
