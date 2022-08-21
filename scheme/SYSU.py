import time

import ddddocr
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from GoodHealth import GoodHealth


class SYSU(GoodHealth):
    def __init__(self, opt):
        super().__init__(opt)
        options = webdriver.FirefoxOptions()
        options.headless = True
        self.handle = webdriver.Firefox(
            executable_path='./geckodriver', options=options)
        self.handle.set_script_timeout(self.opt['request_timeout'])
        self.handle.set_page_load_timeout(self.opt['request_timeout'])

    def __del__(self):
        self.handle.close()

    def login(self):
        try:
            self.handle.get('https://cas.sysu.edu.cn/cas/login')
        except Exception as e:
            self.logger.error(
                'Failed to login. Can not load cas page.', str(e))
            raise e

        self.handle.find_element(
            'xpath', '//*[@id="username"]').send_keys(self.opt['user'])
        self.handle.find_element(
            'xpath', '//*[@id="password"]').send_keys(self.opt['pass'])

        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"}
        cookies = {}
        for i in self.handle.get_cookies():
            cookies[i['name']] = i['value']
        captcha_img = requests.get(
            'https://cas.sysu.edu.cn/cas/captcha.jsp', headers=header, cookies=cookies).content
        ocr = ddddocr.DdddOcr()
        captcha = ocr.classification(captcha_img)
        self.handle.find_element(
            'xpath', '//*[@id="captcha"]').send_keys(captcha)

        self.handle.find_element(
            'xpath', '//*[@id="fm1"]/section[2]/input[4]').click()

        try:
            self.handle.find_element(
                'xpath', '//*[@id="cas"]/div/div[1]/div/div/h2').text
            self.logger.info('Login successfully.')
        except:
            msg = self.handle.find_element(
                'xpath', '//*[@id="fm1"]/div[1]/span').text
            self.logger.error('Failed to login.', msg)
            raise RuntimeError('Failed to login')

    def report(self):
        try:
            self.handle.get(
                "http://jksb.sysu.edu.cn/infoplus/form/XNYQSB/start")
        except Exception as e:
            self.logger.error(
                'Failed to report. Can not load report page', str(e))
            raise e

        wait = WebDriverWait(self.handle, 30)
        try:
            wait.until(expected_conditions.element_to_be_clickable(
                (By.XPATH, "//*[@id='form_command_bar']/li[1]/a")))
        except Exception as e:
            self.logger.error('Failed to open the page.', str(e))
            raise e

        url = self.handle.current_url
        self.handle.find_element(
            'xpath', '//*[@id="form_command_bar"]/li[1]/a').click()

        wait.until(expected_conditions.invisibility_of_element_located((By.XPATH,
                                                                        '//div[@class="blockUI blockOverlay"]')))
        wait.until(expected_conditions.element_to_be_clickable(
            (By.XPATH, "//*[@id='form_command_bar']/li[1]/a")))

        self.handle.find_element(
            'xpath', '//*[@id="form_command_bar"]/li[1]/a').click()

        try:
            wait.until(expected_conditions.visibility_of_element_located(
                (By.XPATH, '//div[@class="dialog display"]')))
        except:
            time.sleep(5)

        self.handle.get(url)
        self.handle.get(
            'http://jksb.sysu.edu.cn/infoplus/form/54592318/render')
        wait.until(expected_conditions.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="title_content"]/nobr'), '健康信息'),)

        try:
            a = self.handle.find_element(
                'xpath', '//*[@id="form_command_bar"]/li[2]')
            assert a.value_of_css_property('Color') == 'rgb(0, 153, 102)'
            self.logger.info(
                'User {} report successfully.'.format(self.opt['user']))
            self.logger.info(
                'More detail: {}'.format(url)
            )
        except Exception as e:
            self.logger.error('Report failure.', str(e))
            raise RuntimeError('Report failure')
