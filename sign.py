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
        M = importlib.import_module('scheme.'+opt['scheme']).__dict__.get(opt['scheme'])

        m = M(opt)
        if not m() and opt['sendkey']:
            with open('log/{}.log'.format(m.logger.name), 'r') as f:
                log = ''
                for l in f.readlines():
                    log = log+l
            msg = '# Failed to report for user {}\n```\n{}\n```'.format(
                opt['user'], log)
            try:
                r = requests.get(
                    'https://sctapi.ftqq.com/' + opt['sendkey'] + '.send',
                    params=dict(title='GoodHealth goes wrong!', desp=msg),
                )
            except:
                m.logger.error('Send message error.')
