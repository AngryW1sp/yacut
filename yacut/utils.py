import asyncio
import aiohttp
import random
import string
from urllib.parse import unquote, urlparse

from aiohttp import FormData
from settings import BaseConfig
from yacut.models import URLMap

MAIN_URL = BaseConfig.BASE_URL
REQUEST_UPLOAD_URL = BaseConfig.REQUEST_UPLOAD_URL
DOWNLOAD_LINK_URL = BaseConfig.DOWNLOAD_LINK_URL
AUTH_HEADERS = {'Authorization': f'OAuth {BaseConfig.DISK_TOKEN}'}


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


async def async_upload_to_yandex(files):
    if files is not None:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for file in files:
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_url(session, file)
                    )
                )
            urls_list = await asyncio.gather(*tasks)
        merged_urls = {}
        for d in urls_list:
            merged_urls.update(d)
        return merged_urls


def get_download_url(location):
    pass


async def upload_file_and_get_url(session, file):
    result = {}
    payload = {
        'path': f'app:/{file.filename}',
        'overwrite': 'True'
    }
    async with session.get(
        headers=AUTH_HEADERS,
        params=payload,
        url=REQUEST_UPLOAD_URL
    ) as resp:
        upload_data = await resp.json()
        upload_url = upload_data['href']

    form = FormData()
    form.add_field('file',
                   file.stream,
                   filename=file.filename,
                   content_type=file.content_type)
    async with session.put(
        data=form,
        url=upload_url
    ) as resp:
        loc_header = resp.headers['Location']
        loc = unquote(loc_header).replace('/disk', '')

    async with session.get(
        headers=AUTH_HEADERS,
        url=DOWNLOAD_LINK_URL,
        params={'path': loc}
    ) as resp:
        download_data = await resp.json()
        link = download_data['href']

    result[file.filename] = [
        link, MAIN_URL.rstrip('/') + '/' + get_unique_short_id()
    ]
    return result


def get_unique_short_id():
    new_url = ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(12)
    )
    if not URLMap.query.filter_by(short=new_url).first():
        return new_url
    return get_unique_short_id()