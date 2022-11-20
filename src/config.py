from configparser import ConfigParser


CONFIG = {}


def read_config():

    global CONFIG

    config = ConfigParser()
    config.read('config.ini')

    CONFIG['api_key'] = config['credentials']['api_key']
    CONFIG['api_key_secret'] = config['credentials']['api_key_secret']
    CONFIG['access_token'] = config['credentials']['access_token']
    CONFIG['access_token_secret'] = config['credentials']['access_token_secret']

    CONFIG['url_pred'] = config['url']['url_pred']