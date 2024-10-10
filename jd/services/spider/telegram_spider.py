import datetime
import os
import time
from random import randint

import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.contacts import GetContactsRequest, DeleteContactsRequest
from telethon.tl.functions.messages import CheckChatInviteRequest, ImportChatInviteRequest, GetFullChatRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChatInviteAlready, ChatInvite, Channel, Chat, Message, ChannelParticipantsSearch, \
    ChannelForbidden, InputMessagesFilterPhotos, ChannelParticipantsRecent, User, DocumentAttributeFilename

from jd import app


class TelegramSpider:

    def __init__(self):
        self._url = ''
        self._headers = {}
        self._proxies = None

    def _send_request(self):
        try:
            r = requests.get(self._url, headers=self._headers, proxies=self._proxies, timeout=10)
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return {}
            return self._parse_result(html)
        except Exception as e:
            print(e)
        return {}

    def _parse_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'photo_url': self._get_div_text(soup, 'tgme_page_photo'),
            'account': self._get_div_text(soup, 'tgme_page_extra'),
            'username': self._get_div_text(soup, 'tgme_page_title'),
            'desc': self._get_div_text(soup, 'tgme_page_description')
        }
        return data

    def _get_div_text(self, soup, class_name):
        div = soup.find_all(class_=class_name, limit=1)
        text = ''
        if div:
            if class_name == 'tgme_page_photo':
                text = div[0].img['src']
            else:
                text = div[0].text.replace('\n', '')
        return text

    def search_query(self, url=''):
        print('start...')
        if not url:
            return {}
        self._set_params(url)
        tel_data = self._send_request()
        print('end...')
        return tel_data

    def _set_params(self, url):
        self._url = url


class TelegramAPIs(object):
    def __init__(self):
        self.client = None

    def init_client(self, session_name, api_id, api_hash, proxy=None):
        """
        初始化client
        :param session_name: session文件名
        :param api_id: api id
        :param api_hash: api hash
        :param proxy: socks代理，默认为空
        """
        if proxy is None:
            self.client = TelegramClient(session_name, api_id, api_hash)
        else:
            self.client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
        self.client.start()

    def close_client(self):
        """
        关闭client
        """
        if self.client.is_connected():
            self.client.disconnect()

    # 加入频道或群组
    async def join_conversation(self, invite):
        """
        加入方式主要分为
            1. 加入公开群组/频道：invite为username
            2. 加入私有群组/频道：invite为hash

        注意：需要测试如下两个逻辑，
            1. 换了群组的username之后，使用新username加入时的返回值(会显示无效，已测)
            2. 是否能直接通过ID加入(不能，通过id只能获取已经加入的频道/群组信息，并通过get_entity方法获取该频道的信息)
        :param invite: channel/group username/hash
        :return: 返回json, {'data': {'id':, 'chat':}, 'result': 'success/failed', 'reason':''}
        data: chat_id
        """
        # 每个加组的操作都休眠10秒先，降低速率
        time.sleep(5)
        chat_id = 0
        result = "Failed"
        result_json = {
            "data": {"id": chat_id, "group_name": invite},
            "result": result,
            "reason": "",
        }
        try:
            # Checking a link without joining
            # 检测私有频道或群组时，由于传入的是hash，可能会失败(已测试，除非是被禁止的，否则也会成功)
            updates = await self.client(CheckChatInviteRequest(invite))
            if isinstance(updates, ChatInviteAlready):
                chat_id = updates.chat.id
                # chat = updates.chat
                result = "Done"
            elif isinstance(updates, ChatInvite):
                # Joining a private chat or channel
                updates = await self.client(ImportChatInviteRequest(invite))
                # updates = self.client(CheckChatInviteRequest(invite))
                chat_id = updates.chats[0].id
                # chat = updates.chats[0]
                result = "Done"
        except Exception as e:
            try:
                # Joining a public chat or channel
                updates = await self.client(JoinChannelRequest(invite))
                result = "Done"
            except Exception as ee:
                result_json["reason"] = str(ee)
                return result_json
            chat_id = updates.chats[0].id
            # chat = updates.chats[0]
        result_json["data"]["id"] = chat_id
        result_json["result"] = result

        return result_json

    def delete_all_dialog(self, is_all=0):
        """
        删除对话框
        """
        for dialog in self.client.get_dialogs():
            # like "4721 4720"、"5909 5908"
            name = dialog.name
            is_new_user = False
            if " " in name and ("1" in name or "3" in name or "6" in name):
                is_new_user = True
            # 退出频道或群组
            if is_all and hasattr(dialog.entity, "title"):
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已离开<{}>群组".format(dialog.entity.title))
            # 删除delete account
            elif dialog.name == "":
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除Deleted Account用户对话框")
            elif is_new_user:
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除{}用户对话框".format(dialog.name))
            elif is_all:
                chat = dialog.entity
                self.client.delete_dialog(chat)
                print("已删除{}用户对话框".format(dialog.name))
            else:
                pass

    async def get_me(self):
        """
        获取当前账户信息
        """
        myself = await self.client.get_me()
        return myself

    def get_contacts(self):
        """
        获取联系人
        """
        contacts = self.client(GetContactsRequest(0))
        return contacts

    def delete_contact(self, ids):
        """
        删除联系人
        """
        self.client(DeleteContactsRequest(ids))

    async def get_dialog_list(self):
        """
        获取已经加入的频道/群组列表
        :return: 返回json, {'data': [], 'result': 'success/failed', 'reason':''}
        data: list类型，
        """
        async for dialog in self.client.iter_dialogs():
            # 确保每次数据的准确性
            result_json = {"result": "success", "reason": "ok"}
            out = {}
            # 只爬取频道或群组，排除个人
            if hasattr(dialog.entity, "title"):
                chat = dialog.entity
                if isinstance(chat, Channel):
                    channel_full = await self.client(GetFullChannelRequest(chat))
                    member_count = channel_full.full_chat.participants_count
                    channel_description = channel_full.full_chat.about
                    username = channel_full.chats[0].username
                    megagroup = channel_full.chats[0].megagroup
                    group_type = 'channel'
                elif isinstance(chat, Chat):
                    channel_full = await self.client(GetFullChatRequest(chat.id))
                    member_count = channel_full.chats[0].participants_count
                    channel_description = channel_full.full_chat.about
                    username = None
                    megagroup = True
                    group_type = 'chat'
                else:
                    yield result_json
                    continue
                # megagroup: true表示超级群组(官方说法)
                # 实际测试发现(TaiwanNumberOne该群组)，megagroup表示频道或群组，true表示群，false表示频道
                # democracy: 暂时不清楚什么意思
                out = {
                    "id": chat.id,
                    "title": chat.title,
                    "username": username,
                    # 'democracy': channel_full.chats[0].democracy,
                    "megagroup": "channel" if megagroup else "group",
                    "member_count": member_count,
                    "channel_description": channel_description,
                    "is_public": 1 if username else 0,
                    "join_date": chat.date.strftime("%Y-%m-%d %H:%M:%S+%Z"),
                    "unread_count": dialog.unread_count,
                    'group_type': group_type
                }
                result_json["data"] = out
                yield result_json

    async def get_person_dialog_list(self):
        """
        获取个人聊天
        :return: 返回json, {'data': [], 'result': 'success/failed', 'reason':''}
        data: list类型，
        """
        result = []
        async for dialog in self.client.iter_dialogs():
            # 确保每次数据的准确性
            chat = dialog.entity
            # if isinstance(chat, Chat):
            #     channel_full = await self.client(GetFullChatRequest(chat.id))
            #     member_count = channel_full.chats[0].participants_count
            #     # channel_description = channel_full.full_chat.about
            #     channel_description = ""
            #     username = None
            #     megagroup = True
            if isinstance(chat, User):
                channel_full = await self.client(GetFullUserRequest(chat.id))
                username = channel_full.users[0].username or ''
                user_id = channel_full.users[0].id
            else:
                continue
            # megagroup: true表示超级群组(官方说法)
            # 实际测试发现(TaiwanNumberOne该群组)，megagroup表示频道或群组，true表示群，false表示频道
            # democracy: 暂时不清楚什么意思
            out = {
                "id": chat.id,
                "username": username,
                "user_id": user_id,
                "unread_count": dialog.unread_count,
            }
            result.append(out)
        return result

    async def get_dialog(self, chat_id, is_more=False):
        """
        方法一：通过遍历的方式获取chat对象，当chat_id相等时，返回
        方法二：对于已经加入的频道/群组，可以直接使用get_entity方法
        :param chat_id: 群组/频道 ID
        :param is_more: 默认为False，不使用遍历的方式
        :return: chat对象，用于后续操作
        """
        # 方法一
        if is_more:
            chat = None
            async for dialog in self.client.iter_dialogs():
                if dialog.entity.id == chat_id:
                    chat = dialog.entity
                    break
        # 方法二
        else:
            chat = await self.client.get_entity(chat_id)

        return chat

    async def scan_message(self, chat, **kwargs):
        """
        遍历消息
        :param chat:
        :param kwargs:
        """
        tick = 0
        waterline = randint(5, 20)
        limit = kwargs["limit"]
        min_id = kwargs["last_message_id"]
        # 默认只能从最远开始爬取
        offset_date = kwargs.get("offset_date", None)
        count = 0
        image_path = os.path.join(app.static_folder, 'images')
        os.makedirs(image_path, exist_ok=True)
        document_path = os.path.join(app.static_folder, 'document')
        os.makedirs(document_path, exist_ok=True)
        async for message in self.client.iter_messages(
                chat,
                limit=limit,
                offset_date=offset_date,
                offset_id=min_id,
                wait_time=1,
                reverse=False,
        ):

            if isinstance(message, Message):
                content = ""
                try:
                    content = message.message
                except Exception as e:
                    print(e)
                m = dict()
                m["message_id"] = message.id
                m["user_id"] = 0
                m["user_name"] = ""
                m["nick_name"] = ""
                m["reply_to_msg_id"] = 0
                m["from_name"] = ""
                m["from_time"] = datetime.datetime.fromtimestamp(657224281)
                if message.sender:
                    m["user_id"] = message.sender.id
                    if isinstance(message.sender, ChannelForbidden):
                        username = ""
                    else:
                        username = message.sender.username
                        username = username if username else ""
                    m["user_name"] = username
                    if isinstance(message.sender, Channel) or isinstance(
                            message.sender, ChannelForbidden
                    ):
                        first_name = message.sender.title
                        last_name = ""
                    else:
                        first_name = message.sender.first_name
                        last_name = message.sender.last_name
                        first_name = first_name if first_name else ""
                        last_name = " " + last_name if last_name else ""
                    m["nick_name"] = "{0}{1}".format(first_name, last_name)
                if message.is_reply:
                    m["reply_to_msg_id"] = message.reply_to_msg_id
                if message.forward:
                    m["from_name"] = message.forward.from_name
                    m["from_time"] = message.forward.date
                m["chat_id"] = chat.id
                # m['postal_time'] = message.date.strftime('%Y-%m-%d %H:%M:%S')
                m["postal_time"] = message.date
                m["message"] = content
                photo = message.photo
                m['photo'] = {}
                if photo:
                    file_name = f'{image_path}/{str(photo.id)}.jpg'
                    m['photo'] = {
                        'photo_id': photo.id,
                        'access_hash': photo.access_hash,
                        'file_path': f'images/{str(photo.id)}.jpg'
                    }
                    static_path = os.path.join(app.static_folder, m['photo']['file_path'])
                    if not os.path.exists(static_path):
                        await self.client.download_media(message=message, file=file_name, thumb=-1)
                document = message.document
                m['document'] = {}
                if document and document.attributes:
                    file_name = ''
                    for attr in document.attributes:
                        if isinstance(attr, DocumentAttributeFilename):
                            file_name = attr.file_name
                            break
                    if file_name:
                        file_path = f'{document_path}/{file_name}'
                        m['document'] = {
                            'document_id': document.id,
                            'file_name': file_name,
                            'file_ext': file_name.split('.')[-1],
                            'access_hash': document.access_hash,
                            'file_path': f'document/{file_name}'
                        }
                        static_path = os.path.join(app.static_folder, m['document']['file_path'])
                        if not os.path.exists(static_path):
                            await self.client.download_media(message=message, file=file_path)
                tick += 1
                if tick >= waterline:
                    tick = 0
                    waterline = randint(5, 10)
                    time.sleep(waterline)
                count += 1
                yield m
        print("total: %d" % count)

    async def scan_message_photo(self, chat, **kwargs):
        """
        遍历消息
        :param chat:
        :param kwargs:
        """
        tick = 0
        waterline = randint(5, 20)
        limit = kwargs["limit"]
        min_id = kwargs["last_message_id"]
        # 默认只能从最远开始爬取
        offset_date = None
        if 0 and kwargs["offset_date"]:
            offset_date = datetime.datetime.strptime(
                kwargs["offset_date"], "%Y-%m-%d %H:%M:%S"
            )
        count = 0
        async for message in self.client.iter_messages(
                chat,
                limit=limit,
                offset_date=offset_date,
                offset_id=min_id,
                wait_time=1,
                reverse=True,
                filter=InputMessagesFilterPhotos):

            if isinstance(message, Message):
                content = ""
                try:
                    content = message.message
                except Exception as e:
                    print(e)
                if content == "":
                    continue
                m = dict()
                m["message_id"] = message.id
                m["user_id"] = 0
                m["user_name"] = ""
                m["nick_name"] = ""
                m["reply_to_msg_id"] = 0
                m["from_name"] = ""
                m["from_time"] = datetime.datetime.fromtimestamp(657224281)
                if message.sender:
                    m["user_id"] = message.sender.id
                    if isinstance(message.sender, ChannelForbidden):
                        username = ""
                    else:
                        username = message.sender.username
                        username = username if username else ""
                    m["user_name"] = username
                    if isinstance(message.sender, Channel) or isinstance(
                            message.sender, ChannelForbidden
                    ):
                        first_name = message.sender.title
                        last_name = ""
                    else:
                        first_name = message.sender.first_name
                        last_name = message.sender.last_name
                        first_name = first_name if first_name else ""
                        last_name = " " + last_name if last_name else ""
                    m["nick_name"] = "{0}{1}".format(first_name, last_name)
                if message.is_reply:
                    m["reply_to_msg_id"] = message.reply_to_msg_id
                if message.forward:
                    m["from_name"] = message.forward.from_name
                    m["from_time"] = message.forward.date
                m["chat_id"] = chat.id
                # m['postal_time'] = message.date.strftime('%Y-%m-%d %H:%M:%S')
                m["postal_time"] = message.date
                m["message"] = content
                m['photo'] = message.photo
                tick += 1
                if tick >= waterline:
                    tick = 0
                    waterline = randint(5, 10)
                    time.sleep(waterline)
                count += 1
                yield m
        print("total: %d" % count)

    async def get_chatroom_user_info(self, chat_id, nick_name):
        chat = await self.get_dialog(chat_id)
        result = []
        try:
            participants = await self.client(
                GetParticipantsRequest(
                    chat,
                    filter=ChannelParticipantsSearch(nick_name),
                    offset=0,
                    limit=randint(5, 10),
                    hash=0,
                )
            )
        except Exception as e:
            print("查找《{}》用户失败，失败原因：{}".format(nick_name, str(e)))
            return []

        if not participants.users:
            print("未找到《{}》用户。".format(nick_name))
            return []

        for entity in participants.users:
            user_info = entity.to_dict()
            result.append({'user_id': user_info['id'],
                           'username': user_info['username'],
                           'first_name': user_info['first_name'],
                           'last_name': user_info['last_name']})
            print(f'{nick_name}:{user_info}')

        return result

    async def get_chatroom_all_user_info(self, chat_id):
        chat = await self.get_dialog(chat_id)
        result = []
        try:
            participants = await self.client(
                GetParticipantsRequest(
                    chat,
                    filter=ChannelParticipantsRecent(),
                    offset=0,
                    limit=50,
                    hash=0,
                )
            )
        except Exception as e:
            print("查找《{}》用户失败，失败原因：{}".format(chat_id, str(e)))
            return []

        if not participants.users:
            print("未找到《{}》用户。".format(chat_id))
            return []

        for entity in participants.users:
            user_info = entity.to_dict()
            result.append({'user_id': user_info['id'],
                           'username': user_info['username'],
                           'first_name': user_info['first_name'],
                           'last_name': user_info['last_name']})

        return result

    async def get_full_channel(self, chat_id):
        chat = await self.get_dialog(chat_id)
        if not chat:
            return {}
        channel_full = await self.client(GetFullChannelRequest(chat))
        if not channel_full:
            return {}
        member_count = channel_full.full_chat.participants_count
        channel_description = channel_full.full_chat.about
        username = channel_full.chats[0].username
        megagroup = channel_full.chats[0].megagroup
        out = {
            "id": chat.id,
            "title": chat.title,
            "username": username,
            "megagroup": "channel" if megagroup else "group",
            "member_count": member_count,
            "channel_description": channel_description,
            "is_public": 1 if username else 0,
            "join_date": chat.date.strftime("%Y-%m-%d %H:%M:%S+%Z"),
        }
        return out


def test_tg_spider():
    spider = TelegramSpider()
    url_list = ['https://t.me/feixingmeiluo', 'https://t.me/huaxuerou', 'https://t.me/ppo995']
    for url in url_list:
        data = spider.search_query(url)
        if data:
            if '@' in data['account']:
                print(f'个人账户：{url}, data:{data}')
            elif 'subscribers' in data['account']:
                print(f'群组账户：{url}, data:{data}')
            else:
                print(f'其他账户：{url}, data:{data}')
        else:
            print(f'{url}, 无数据')


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    tg = TelegramAPIs()
    config_js = app.config['TG_CONFIG']
    session_name = f'{app.static_folder}/utils/{config_js.get("web_session_name")}'
    api_id = config_js.get("api_id")
    api_hash = config_js.get("api_hash")
    proxy = config_js.get("proxy", {})
    clash_proxy = None
    # 配置代理
    # if proxy:
    #     protocal = proxy.get("protocal", "socks5")
    #     proxy_ip = proxy.get("ip", "127.0.0.1")
    #     proxy_port = proxy.get("port", 7890)
    #     clash_proxy = (protocal, proxy_ip, proxy_port)
    tg.init_client(
        session_name=session_name, api_id=api_id, api_hash=api_hash, proxy=clash_proxy
    )


    # async def get_me():
    #     me = await tg.get_me()
    #     print(f'me: {me}')

    # async def get_group_list():
    #     """
    #     group_list: [{'result': 'success', 'reason': 'ok', 'data': {'id': 1610505522, 'title': '巴域商业中心超市', 'username': 'chaoshi99999', 'megagroup': 'channel', 'member_count': 4184, 'channel_description': '', 'is_public': 1, 'join_date': '2024-08-01 06:38:37+UTC', 'unread_count': 4425}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1857812395, 'title': '钉钉接码🌏京东接码💗美团接码🌏陌陌接码 @Qk66678 @ppo995@J5333@karamsang@truetrueaccbobi@qq5914 @maihao99bot@tuitehaocc8tuitehaocc8tuitehaocc@karams', 'username': 'kef43433', 'megagroup': 'group', 'member_count': 12478, 'channel_description': '', 'is_public': 1, 'join_date': '2024-08-01 06:34:43+UTC', 'unread_count': 34}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1270985546, 'title': '大咕咕咕鸡', 'username': 'dagudu', 'megagroup': 'group', 'member_count': 1955, 'channel_description': '大咕咕咕鸡，微博知名博主，叙事诗人，当代严肃文学特师，月入2300，代表作有《黄浦江有话讲》《一次突如其来的性生活》等，他的文章风格独特，自成一派，值得一看。\n\n特师文集： mindfucking.gitbook.io/daguguguji\n\n人间动物园： @renjiandongwuyuan\n\n频道维护猫： @lidamao_bot\n\n感谢 @RSStT_Bot 提供支持', 'is_public': 1, 'join_date': '2024-08-02 12:45:36+UTC', 'unread_count': 9}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1076212650, 'title': '@zhongwen 中文语言安装包🅥汉化翻译', 'username': None, 'megagroup': 'group', 'member_count': 258534, 'channel_description': '【华人在外】广告介绍 @Guanggao\n华人百万社群 @huaren\n50万人供需发布频道 @daifa\n91国产社区 @gaoqing\n广告自助发布 @C4bot\n🔍AV搜片群 @AVpian\n🔎搜群神器 @sosuo\n吃瓜搞笑爆料 @Chigua\n开车频道群组 @kaiche\n招聘频道 @zhaopin\n求职甩人 @qiuzhi\n免费群管机器人 @qunbot\n✅中文安装 @zhongwen\n\n☎️唯一广告负责联系人 @DDDDDD', 'is_public': 0, 'join_date': '2024-07-31 05:42:26+UTC', 'unread_count': 3}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1825747029, 'title': '玩偶姐姐 𝙃𝙤𝙣𝙜𝙆𝙤𝙣𝙜𝘿𝙤𝙡𝙡_𝙏𝙑', 'username': 'HongKongDoll_Public', 'megagroup': 'group', 'member_count': 11701, 'channel_description': '', 'is_public': 1, 'join_date': '2024-08-06 13:32:15+UTC', 'unread_count': 0}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1905420033, 'title': '上头电子烟原料 依托咪酯 依托终结者 化学交流', 'username': 'ulae4888', 'megagroup': 'group', 'member_count': 318, 'channel_description': '上头电子烟原料 依托咪酯 依托终结者 化学交流', 'is_public': 1, 'join_date': '2024-08-06 13:31:51+UTC', 'unread_count': 0}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1872484668, 'title': '海外引流 | 海外获客丨FB引流丨脸书广告丨@liubifafa @XNZ6625 @nk52020@dj9400 @duo788@uup99887 @ppo995@xone88@xincheng8887@kka995', 'username': 'dnaslkdas', 'megagroup': 'group', 'member_count': 30134, 'channel_description': '', 'is_public': 1, 'join_date': '2024-08-01 06:35:26+UTC', 'unread_count': 0}}, {'result': 'success', 'reason': 'ok', 'data': {'id': 1195428755, 'title': 'ShadowsocksVPN', 'username': 'vpnshadowsocks', 'megagroup': 'group', 'member_count': 1537, 'channel_description': 'Простой канал без всяких дополнительных данных. Только VPN. И приятное оформление для глаз\n\n💬 Наш чатик: @vpnShadowsockss\nReklama \n📢 По поводу вп писать сюда: \n@Creator_mann \n\n❤﷽Aใhล๓dนใเใใลh﷽❤', 'is_public': 1, 'join_date': '2024-08-01 06:37:29+UTC', 'unread_count': 0}}]
    #
    #     :return:
    #     """
    #     result = []
    #     async for group in tg.get_dialog_list():
    #         result.append(group)
    #     print('group_list:', result)


    #

    # async def join_group():
    #     # group_name = 'bajiebest'
    #     group_name = 'chaoshi99999'
    #     result = await tg.join_conversation(group_name)
    #     print(result)

    #

    async def scan_message_photo():
        params = {
            "limit": 20,
            # "offset_date": datetime.datetime.now() - datetime.timedelta(hours=8) - datetime.timedelta(minutes=20),
            "last_message_id": -1,
        }
        group_id = 777000
        chat = await tg.get_dialog(group_id)
        print(chat)
        history = tg.scan_message(chat, **params)
        async for message in history:
            print(message)
    #
    #

    # async def get_group_users():
    #     group_id = 1610505522
    #     result = await tg.get_chatroom_all_user_info(group_id)
    #     print(result)

    # async def get_group_users():
    #     group_id = 1610505522
    #     result = await tg.get_chatroom_user_info(group_id, '小胖')
    #     print(result)

    # async def get_chat(chat_id):
    #     chat = await tg.get_dialog(chat_id)
    #     channel_full = await tg.client(GetFullChannelRequest(chat))
    #
    #     print(channel_full)

    async def get_person_dialog_list():
        result = await tg.get_person_dialog_list()
        print(result)


    with tg.client:
        tg.client.loop.run_until_complete(scan_message_photo())
