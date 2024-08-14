import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def run():
    driver = webdriver.Chrome()
    url = 'https://my.telegram.org/auth'
    driver.get(url)
    time.sleep(3)
    # 填手机号
    phone = '+56990552148'
    send_form = driver.find_element(By.ID, "my_send_form")
    phone_input = send_form.find_element(By.ID, "my_login_phone")
    phone_input.send_keys(phone)
    time.sleep(0.5)
    next_button = send_form.find_element(By.XPATH, '//button[@type="submit"]')
    next_button.click()
    time.sleep(1)


    password = ''
    for i in range(10):
        password = input('Enter your password: ')
        if password:
            break
        time.sleep(1)
    if not password:
        driver.quit()
        return
    login_form = driver.find_element(By.ID, "my_login_form")
    password_input = login_form.find_element(By.NAME, "password")
    password_input.send_keys(password)
    time.sleep(0.5)
    submit_button = login_form.find_element(By.XPATH, '//button[@type="submit"]')
    submit_button.click()
    time.sleep(1)

    driver.quit()


if __name__ == '__main__':
    run()