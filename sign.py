import importlib
import os

import requests
import yaml

if __name__ == '__main__':

    try:
        user_env = os.environ.get('GHUSERNAME').split(',')
        pass_env = os.environ.get('GHPASSWORD').split(',')
        sendkey_env = os.environ.get('GHSENDKEY').split(',')
    except:
        pass

    with open('./config.yml', 'r') as f:
        opts = yaml.load_all(f.read(), yaml.FullLoader)

    for i, opt in enumerate(opts):
        if opt['env']:
            try:
                opt['user'] = user_env[i]
                opt['pass'] = pass_env[i]
                opt['sendkey'] = sendkey_env[i]
            except:
                raise RuntimeError('Define user error')
        M = importlib.import_module('scheme.' + opt['scheme']).__dict__.get(
            opt['scheme']
        )

        m = M(opt)
        if not m():
            if opt['sendkey']:
                with open('log/{}.log'.format(m.logger.name), 'r') as f:
                    log = ''
                    for l in f.readlines():
                        log = log + l
                msg = '# Failed to report for user {}\n```\n{}\n```'.format(
                    opt['user'], log
                )
                try:
                    r = requests.get(
                        'http://www.pushplus.plus/send',
                        params=dict(
                            token=opt['sendkey'],
                            template="markdown",
                            title='GoodHealth goes wrong!',
                            content=msg,
                        ),
                    )
                    if not r.status_code == 200:
                        raise Exception()
                except:
                    m.logger.error('Send message error.')
            exit(444)
