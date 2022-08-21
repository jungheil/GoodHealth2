import logging
import os
import time


def retry(max_attempt_times=3, wait_s=0, ext=Exception, logger=None):

    def inner(f):

        def wrapper(*args, **kwargs):
            for i in range(max_attempt_times):
                try:
                    if logger and i != 0:
                        logger.info(
                            '[retry] Function "{}" attempt No.{}'.format(
                                f.__name__, i + 1))
                    args = args if args else list()
                    kwargs = kwargs if kwargs else dict()
                    return f(*args, **kwargs)
                except ext as e:

                    if logger:
                        logger.warning(
                            '[retry] Function "{}" exits unexpectedly. {}'.
                            format(f.__name__, str(e)))
                    if i + 1 == max_attempt_times:
                        if logger:
                            logger.error('[retry] Abandon and throw an error.')
                        raise e
                    time.sleep(wait_s)

        return wrapper

    return inner


class GoodHealth:

    def __init__(self, opt):
        self.opt = opt

        os.makedirs('log', exist_ok=True)
        logger_name = '{}-{}'.format(time.strftime('%Y-%m-%d-%H-%M-%S'),
                                     self.opt['user'])
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        sh = logging.StreamHandler()
        # sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)
        fh = logging.FileHandler('log/' + logger_name + '.log',
                                 encoding="utf-8")
        # fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def __call__(self) -> bool:
        r = retry(max_attempt_times=self.opt['max_retry_times'],
                  wait_s=self.opt['retry_wait_s'],
                  logger=self.logger)
        try:
            self.logger.info('Log in as user {}'.format(self.opt['user']))
            r(self.login)()
            self.logger.info('Get report status of user {}'.format(
                self.opt['user']))
            if r(self.get_status)():
                self.logger.info("User {} have reported.".format(
                    self.opt['user']))
                if (self.opt['force_report']):
                    self.logger.warning("Force report for user {}.".format(
                        self.opt['user']))
                else:
                    return True
            r(self.report)()
            return True

        except Exception as e:
            self.logger.error('Failed to report for user {}. {}'.format(
                self.opt['user'], str(e)))
            return False

    def get_status(self, date=None) -> bool:
        self.logger.info('Ignore getting status.')
        return False
