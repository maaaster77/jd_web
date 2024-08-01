from jd.services.spider.tg import TgService


def run():
    tg = TgService.init_tg()

    async def get_me():
        me = await tg.get_me()
        print('me:', me)

    with tg.client:
        tg.client.loop.run_until_complete(get_me())
