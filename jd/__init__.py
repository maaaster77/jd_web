import os
import pkgutil
from importlib import import_module

from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from jCelery import celery

db = SQLAlchemy()
socketio = SocketIO()
JD_ROOT = os.path.abspath(os.path.dirname(__file__))


class Application(Flask):

    def __init__(self):
        super(Application, self).__init__(__name__)
        config_file = os.path.abspath(os.path.join(JD_ROOT, '../config.py'))
        print(f'loading configuration:{config_file}')
        self.config.from_pyfile(config_file)
        local_config = os.path.abspath(os.path.join(JD_ROOT, '../config_local.py'))
        if os.path.exists(local_config):
            print('loading local config: %s' % local_config)
            self.config.from_pyfile(local_config)
        self.template_folder = os.path.abspath(os.path.join(JD_ROOT, '../templates'))
        self.static_folder = os.path.abspath(os.path.join(JD_ROOT, '../static'))
        self.secret_key = self.config.get('SESSION_SECRET_KEY')

    def ready(self, db_switch=True, web_switch=True, worker_switch=True, socketio_switch=False):
        if db_switch:
            db.init_app(self)
        if web_switch:
            self.prepare_blueprints()
        if worker_switch:
            self.prepare_celery()
        if socketio_switch:
            self.prepare_socketio()

    def prepare_blueprints(self):
        from jd import views
        auto_load(views)

        from jd.views.api import api
        prefix = self.config.get('API_PREFIX', '')
        self.register_blueprint(api, url_prefix=prefix)

    def prepare_celery(self):
        celery.conf.update(app.config)
        self.register_celery()

    def register_celery(self):
        class ContextTask(celery.Task):
            abstract = True

            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    def prepare_socketio(self):
        socketio.init_app(self, cors_allowed_origins="*")


    # def wsgi_app(self, environ, start_response):
    #     ctx = self.request_context(environ)
    #     ctx.push()
    #     error = None
    #     try:
    #         try:
    #             response = self.full_dispatch_request()
    #         except Exception as e:
    #             error = e
    #             response = self.handle_exception(e)
    #         except:
    #             error = sys.exc_info()[1]
    #             raise
    #         return response(environ, start_response)
    #     finally:
    #         if self.should_ignore_error(error):
    #             error = None
    #         ctx.auto_pop(error)


def auto_load(module):
    for loader, name, ispkg in pkgutil.iter_modules(module.__path__):
        module_name = '%s.%s' % (module.__name__, name)
        app.logger.debug('loading module: "%s" ispkg:%s', module_name, ispkg)
        _module = import_module(module_name)

        if ispkg:
            auto_load(_module)


app = Application()
