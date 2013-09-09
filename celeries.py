import os
from cohab.celeries import celery

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cohab.celery')
    celery.start()