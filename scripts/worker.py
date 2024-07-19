import logging

import jd.tasks
# celery一定要引入，不然找不到application
from jd import app, celery

app.ready(web_switch=False)
logger = logging.getLogger(__name__)


def load_module_recursively(module):
    import pkgutil
    for loader, name, ispkg in pkgutil.iter_modules(module.__path__):
        module_name = '%s.%s' % (module.__name__, name)
        print('loading task: %s' % module_name)
        _module = __import__(module_name, fromlist=[''])
        if ispkg:
            load_module_recursively(_module)


load_module_recursively(jd.tasks)
