from jd.services.spider.tg import TgService


def run():
    # for origin in ['job', 'celery', 'web']:
    for origin in ['web']:
        tg = TgService.init_tg(origin)

        async def get_me():
            me = await tg.get_me()
            print('me:', me)

        with tg.client:
            tg.client.loop.run_until_complete(get_me())
