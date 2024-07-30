# -*- coding: utf-8 -*-

import logging
import sys

from jd import app

LOGGER = logging.getLogger()


def main():
    try:
        args = sys.argv.copy()
        job_name = args.pop(1)
        mod_name = 'jd.jobs.%s' % job_name
        app.ready(web_switch=False)

        mod = __import__(mod_name, fromlist=['*'])
        mod.run(*args[1:])
        return 0
    except Exception as e:
        LOGGER.exception(e)
        raise

    finally:
        pass


if __name__ == '__main__':
    with app.app_context():
        sys.exit(main())
