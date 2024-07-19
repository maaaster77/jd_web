from celery import Celery

from jCelery import celeryconfig


def make_celery():
    celery = Celery('jd',
                    broker=celeryconfig.broker_url,
                    backend=celeryconfig.result_backend)
    celery.config_from_object(celeryconfig)
    return celery


celery = make_celery()
