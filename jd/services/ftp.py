import datetime
import json
import logging
import os
import time
from ftplib import FTP

from jd import app
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo

logger = logging.getLogger(__name__)


class FtpService:
    ftp = None

    @classmethod
    def init_ftp(cls):
        try:
            if cls.ftp is None:
                cls.ftp = FTP()
                cls.ftp.connect('120.224.39.232', 21)
                cls.ftp.login(user='rzx_syldry', passwd='rzx_syldry')
                cls.ftp.encoding = 'utf-8'
                logger.info('ftp connect success')
                print('ftp connect success')
                return True
        except Exception as e:
            logger.error(f'ftp connect error: {e}')
        return False

    @classmethod
    def close_ftp(cls):
        if cls.ftp is not None:
            cls.ftp.quit()
            cls.ftp = None
            logger.info('ftp disconnect success')
            print('ftp disconnect success')

    @classmethod
    def _send_file(cls, file_path, max_retries=3):
        if not cls.ftp:
            return
        logger.info(f'ftp send file: {file_path}')
        file_name = file_path.split('/')[-1]
        file_ext = file_path.split('.')[-1]
        if file_path.startswith(f'{app.static_folder}/document'):
            # 除光闸兼容的格式外，其他格式改成doc
            if file_ext not in ['png', 'jpg', 'doc', 'docx', 'xls', 'xlsx', 'txt']:
                file_name = file_name.replace(file_ext, 'doc')
            file_name = f'JD-TG-file-documents-{file_ext}-{file_name}'
        elif file_path.startswith(f'{app.static_folder}/images/avatar'):
            file_name = f'JD-TG-file-avatar-{file_ext}-{file_name}'
        elif file_path.startswith(f'{app.static_folder}/images'):
            file_name = f'JD-TG-file-images-{file_ext}-{file_name}'
        file_name = file_name.encode('utf-8').decode('utf-8')
        for attempt in range(max_retries + 1):
            try:
                with open(file_path, 'rb') as file:
                    cls.ftp.storbinary(f'STOR {file_name}', file)
                logger.info(f'ftp send success: {file_path}, file_name:{file_name}')
                if file_ext == 'json':
                    os.remove(file_path)
                print(f'ftp send success: {file_path}, file_name:{file_name}')
                break
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f'ftp send failed, retrying ({attempt + 1}/{max_retries}): {file_path}, file_name:{file_name}, {e}')
                else:
                    logger.error(f'ftp send error: {file_path}, file_name:{file_name}, {e}')
                time.sleep(0.5)

    @classmethod
    def _save_local_file(cls, data, file_path):
        logger.info(f'ftp save_local_file: {file_path}')
        try:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(data)
            logger.info(f'save_local_file success: {file_path}')
            return True
        except Exception as e:
            logger.error(f'save_local_file fail | file path:{file_path} error:{e}')
        return False

    @classmethod
    def send_file_by_file_path(cls, file_path_list):
        if not file_path_list:
            return
        if not cls.init_ftp():
            return
        for file_path in file_path_list:
            if not os.path.exists(file_path):
                continue
            cls._send_file(file_path)
        cls.close_ftp()

    @classmethod
    def save_local_file_from_db(cls, db_data: list, table_name: str, file_type: str, deal_else_file=False):
        """
        :param deal_else_file:
        :param db_data:
        :param table_name:
        :param file_type: new-新增 update-更新
        :return:
        """
        tg_group_dir = os.path.join(os.path.join(app.static_folder, 'send_file'), table_name)
        os.makedirs(tg_group_dir, exist_ok=True)
        data = []
        else_file_path_list = []
        file_path = ''

        def can_append(fp):
            if not fp:
                return False
            # file_ext = fp.split('.')[-1]
            # if file_ext in ['tnl', 'webm', 'webp']:
            #     return False
            return True

        for row in db_data:
            d = row.to_dict()
            data.append(d)
            if not deal_else_file:
                continue
            if isinstance(row, TgGroup):
                if can_append(row.avatar_path):
                    else_file_path_list.append(os.path.join(app.static_folder, row.avatar_path))
            elif isinstance(row, TgGroupChatHistory):
                if can_append(row.photo_path):
                    else_file_path_list.append(os.path.join(app.static_folder, row.photo_path))
                if can_append(row.document_path):
                    else_file_path_list.append(os.path.join(app.static_folder, row.document_path))
            elif isinstance(row, TgGroupUserInfo):
                if can_append(row.avatar_path):
                    else_file_path_list.append(os.path.join(app.static_folder, row.avatar_path))
        if data:
            str_data = json.dumps(data, ensure_ascii=False)
            now_time = int(datetime.datetime.now().timestamp())
            file_path = os.path.join(tg_group_dir, f'JD-TG-{table_name}-{file_type}-{now_time}.json')
            if not cls._save_local_file(str_data, file_path):
                return '', else_file_path_list
        else_file_path_list = list(set(else_file_path_list))
        return file_path, else_file_path_list
