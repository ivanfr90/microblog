import json

import requests
from flask_babel import _

from app import app


def translate(text, src_language, dest_language):
    if 'YANDEX_API_KEY' not in app.config or not app.config['YANDEX_API_KEY']:
        return _('ERROR - Translation service is not configured')
    r = requests.get(f'{app.config["YANDEX_ENDPOINT"]}'
                     f'?key={app.config["YANDEX_API_KEY"]}'
                     f'&text={text}'
                     f'&lang={src_language}-{dest_language}')
    if r.status_code != 200:
        return _('ERROR - Translation service failed')
    return json.loads(r.content.decode(('utf-8-sig')))['text'][0]
