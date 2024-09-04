import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from jCelery import celery
from jd import app, db
from jd.models.tg_account import TgAccount
from jd.services.proxy import OxylabsProxy, create_proxyauth_extension


@celery.task
def tg_app_init(phone):
    with app.app_context():
        # 设置代理服务器
        proxyauth_plugin_path = create_proxyauth_extension(
            proxy_host=app.config['OXYLABS_HOST'],
            proxy_port=app.config['OXYLABS_PORT'],
            proxy_username=app.config['OXYLABS_USERNAME'],
            proxy_password=app.config['OXYLABS_PASSWORD']
        )

        chrome_options = Options()
        chrome_options.add_extension(proxyauth_plugin_path)

        chrome_options.add_argument('--headless')  # 启动无头模式
        chrome_options.add_argument('--disable-gpu')  # 一些系统可能需要禁用 GPU 加速
        chrome_options.add_argument('--no-sandbox')  # Bypass OS
        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://my.telegram.org/auth'
        # url = 'https://httpbin.org/ip'  # 请求当前使用的ip
        try:
            driver.get(url)
        except Exception as e:
            print(f'请求不通该url:{url}')
            driver.quit()
            return
        page_source = driver.page_source
        print(f'url:{url}, page:{page_source}')
        time.sleep(1)
        send_form = driver.find_element(By.ID, "my_send_form")
        phone_input = send_form.find_element(By.ID, "my_login_phone")
        phone_input.send_keys(phone)
        time.sleep(0.5)
        next_button = send_form.find_element(By.XPATH, '//button[@type="submit"]')
        next_button.click()
        time.sleep(1)
        code = ''
        for i in range(60):
            obj = TgAccount.query.filter_by(phone=phone).first()
            print(f'第{i + 1}次获取验证码...')
            if obj.api_code:
                code = obj.api_code
                break
            db.session.commit()
            time.sleep(1)
        if not code:
            driver.quit()
            return
        login_form = driver.find_element(By.ID, "my_login_form")
        code_input = login_form.find_element(By.ID, "my_password")
        code_input.send_keys(code)
        time.sleep(0.5)
        support_submit_div = login_form.find_element(By.CLASS_NAME, 'support_submit')
        submit_button = support_submit_div.find_element(By.TAG_NAME, 'button')
        submit_button.click()
        time.sleep(1)
        my_main_content = driver.find_element(By.CLASS_NAME, "my_main_content")
        ul_element = my_main_content.find_element(By.TAG_NAME, "ul")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        if li_elements:
            first_li = li_elements[0]
            a = first_li.find_element(By.TAG_NAME, "a")
            a.click()
        time.sleep(5)
        driver.save_screenshot('page.png')

        form = driver.find_element(By.ID, "app_edit_form")
        # 分割文本到每一行
        text = form.text
        lines = text.split('\n')
        api_id = lines[2]
        api_hash = lines[4]
        # 遍历每一行并提取关键信息
        driver.quit()
        if not api_id or not api_hash:
            return
        TgAccount.query.filter_by(phone=phone).update({
            TgAccount.api_id: api_id,
            TgAccount.api_hash: api_hash
        })
        db.session.commit()


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=False)
    tg_app_init('+573001824960')
