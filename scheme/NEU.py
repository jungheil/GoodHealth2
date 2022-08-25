import datetime
import json
import re
import time

import pytz
import requests
from GoodHealth import GoodHealth


class NEU(GoodHealth):
    def __init__(self, opt):
        super().__init__(opt)
        requests.packages.urllib3.disable_warnings()
        self.__headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/7.0.4 Mobile/16B91 Safari/605.1.15'
        }

        self.__session = requests.Session()

        opt['user'] = str(opt['user'])
        if self.opt['vpn']:
            self.hack_ip()

    def __del__(self):
        self.__session.close()

    def __NEU_login(self, url):
        info = self.__session.get(url)
        info.raise_for_status()
        lt = re.findall("name=\"lt\" value=\"(.*?)\" />", info.text)[0]
        execution = re.findall(
            "name=\"execution\" value=\"(.*?)\" />", info.text)[0]
        post_data = {
            'rsa': self.opt['user'] + self.opt['pass'] + lt,
            'ul': len(self.opt['user']),
            'pl': len(self.opt['pass']),
            'lt': lt,
            'execution': execution,
            '_eventId': 'submit',
        }
        ret = self.__session.post(url, headers=self.__headers, data=post_data)
        ret.raise_for_status
        return ret

    def normal_ip(self):
        self.opt['vpn'] = False

    def hack_ip(self):
        login_post = self.__NEU_login(
            r'https://pass.neu.edu.cn/tpass/login?service=https%3A%2F%2Fwebvpn.neu.edu.cn%2Flogin%3Fcas_login%3Dtrue'
        )
        if login_post.url == 'https://webvpn.neu.edu.cn/':
            self.opt['vpn'] = True
            self.logger.info('Successful login the webvpn.')
        else:
            raise RuntimeError('Failed to login the webvpn.')

    def login(self):
        login_post = self.__NEU_login(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421e0f6528f693e6d45300d8db9d6562d/tpass/login'
            if self.opt['vpn']
            else r'https://pass.neu.edu.cn/tpass/login'
        )
        if 'tp_up' in login_post.url:
            self.logger.info('Successful login the portal.')
        else:
            raise RuntimeError('Failed to login the portal.')

    def get_status(self, date=None):
        """Check whether your info have reported.
        Args:
            date (string): The date you want to check. Defaults to today.
                            ex. '2022-01-18'
        Returns:
            bool: Whether your info have reported.
        """
        if not date:
            date = datetime.datetime.fromtimestamp(
                int(time.time()), pytz.timezone('Asia/Shanghai')
            ).strftime('%Y-%m-%d')
        status_page = self.__session.get(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes'
            if self.opt['vpn']
            else r'https://e-report.neu.edu.cn/api/notes',
            verify=False,
        )
        status_page.raise_for_status()
        status = json.loads(status_page.text)['data']
        status.reverse()
        for i in status:
            if i['created_on'] == date:
                return True
        return False

    def report(self):
        """Post your state of health.
        Args:
            location_ch (dict): The location you changed. Defaults to None i.e. the location is not changed.
                                ex. {
                                    'country': "中国",
                                    'province': "辽宁省",
                                    'city': "沈阳市"
                                }
            force (bool): Force running even if it has been reported today.
        Raises:
            RuntimeError: post or validate failed.
        """

        start_page = self.__session.get(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/mobile/notes/create'
            if self.opt['vpn']
            else r'https://e-report.neu.edu.cn/mobile/notes/create',
            verify=False,
        )
        start_page.raise_for_status()
        get_profiles = self.__session.get(
            (
                r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/profiles/'
                if self.opt['vpn']
                else r'https://e-report.neu.edu.cn/api/profiles/'
            )
            + self.opt['user']
        )
        get_profiles.raise_for_status()
        prof_dict = json.loads(get_profiles.text)
        if self.opt['location']:
            data = {
                '_token': re.findall(
                    "\"csrf-token\" content=\"(.*?)\">", start_page.text
                )[0],
                'jibenxinxi_shifoubenrenshangbao': '1',
                'profile[xuegonghao]': self.opt['user'],
                'profile[xingming]': prof_dict['data']['xingming'],
                'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
                'jiankangxinxi_muqianshentizhuangkuang': '正常',
                'xingchengxinxi_weizhishifouyoubianhua': '1',
                'xingchengxinxi_guojia': self.opt['location']['country'],
                'xingchengxinxi_shengfen': self.opt['location']['province'],
                'xingchengxinxi_chengshi': self.opt['location']['city'],
                'cross_city': '无',
                'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
                'credits': '1',
                'travels': [],
            }
        else:
            data = {
                '_token': re.findall(
                    "\"csrf-token\" content=\"(.*?)\">", start_page.text
                )[0],
                'jibenxinxi_shifoubenrenshangbao': '1',
                'profile[xuegonghao]': self.opt['user'],
                'profile[xingming]': prof_dict['data']['xingming'],
                'profile[suoshubanji]': prof_dict['data']['suoshubanji'],
                'jiankangxinxi_muqianshentizhuangkuang': '正常',
                'xingchengxinxi_weizhishifouyoubianhua': '0',
                'cross_city': '无',
                'qitashixiang_qitaxuyaoshuomingdeshixiang': '',
                'credits': '1',
                'travels': [],
            }

        post_notes = self.__session.post(
            r'https://webvpn.neu.edu.cn/http/77726476706e69737468656265737421f5ba5399373f7a4430068cb9d6502720645809/api/notes'
            if self.opt['vpn']
            else r'https://e-report.neu.edu.cn/api/notes',
            data=data,
            verify=False,
        )
        post_notes.raise_for_status()
        if post_notes.text == '':
            self.logger.info('Post successful.')
        else:
            self.logger.info(post_notes.text)
            raise RuntimeError('Post failure.')

        if self.get_status():
            self.logger.info('All done!')
            return
        else:
            raise RuntimeError('No record was detected')
