from datetime import datetime
import json
import os
from urllib.parse import unquote, urlparse
import requests
import random
from dotenv import load_dotenv
import string
from flask import Flask, abort, flash, redirect, render_template, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional

load_dotenv()

MAIN_URL = 'http://127.0.0.1:5000/'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SECRET_KEY'] = 'MY SECRET KEY'
db = SQLAlchemy(app)
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
DISK_INFO_URL = f'{API_HOST}{API_VERSION}/disk/'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DISK_TOKEN = os.environ.get('DISK_TOKEN')
AUTH_HEADERS = {
    'Authorization': f'OAuth {DISK_TOKEN}'
}
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(128), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class URLMapForm(FlaskForm):
    original_link = URLField('Введите оригинальную ссылку',
                             validators=[DataRequired(message='Обязательное поле'), Length(1, 256)],)
    custom_id = URLField('Введите желаемую короткую ссылку(опционально)',
                         validators=[Optional(), Length(1, 256)],)


class URLFileForm(FlaskForm):
    files = MultipleFileField(
        validators=[DataRequired(message='Обязательное поле')])


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_download_url(location):
    link = requests.get(
        headers=AUTH_HEADERS,
        url=DOWNLOAD_LINK_URL,
        params={'path': f'{location}'}, timeout=5000
    ).json()['href']
    print(link)
    return link


def upload_and_get(files):
    urls = {}
    for file in files:
        payload = {
            'path': f'app:/{file.filename}',
            'overwrite': 'True'
        }
        upload_url = requests.get(
            headers=AUTH_HEADERS,
            params=payload,
            url=REQUEST_UPLOAD_URL, timeout=5000
        ).json()['href']
        location = unquote(requests.put(
            data=file,
            url=upload_url,
            timeout=5000).headers['Location']).replace('/disk', '')
        print(location)
        urls[file.filename] = [get_download_url(
            location), MAIN_URL + get_unique_short_id()]
    return urls


@app.route('/<url>', methods=['GET'])
def redirect_view(url):
    url_query = URLMap().query.filter_by(short=MAIN_URL + url).first()
    if url_query:
        original_url = url_query.original
        return redirect(f'{original_url}')
    else:
        return abort(404)


def get_unique_short_id():
    new_url = ''.join(random.choice(string.ascii_letters + string.digits)
                      for x in range(12))
    if not URLMap.query.filter_by(short=new_url).first():
        return new_url
    else:
        return get_unique_short_id()


@app.route('/download', methods=['GET', 'POST'])
def download_view():

    form = URLFileForm()
    uploaded = {}
    if form.validate_on_submit():
        urls = upload_and_get(form.files.data)
        for name, urls_collect in urls.items():
            url = URLMap(
                original=urls_collect[0],
                short=urls_collect[1]
            )
            db.session.add(url)
            uploaded[name] = urls_collect[1]
        db.session.commit()
        return render_template('download.html', form=form, uploaded=uploaded)
    return render_template('download.html', form=form)


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    url = URLMap.query.filter_by(short=short_id).first()
    if not url:
        return jsonify({
            "message": "Указанный id не найден"
        })
    return jsonify({"url": url.original})


@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Отсутствует тело запроса"}), 400
    if not data.get('url'):
        return jsonify({"message": "\"url\" является обязательным полем!"}), 400

    if data.get('custom_id'):
        if URLMap.query.filter_by(short=data['custom_id']).first():
            return jsonify({"message": "Предложенный вариант короткой ссылки уже существует."}), 400
        if not is_valid_url(data['custom_id']):
            return jsonify({"message": "Указано недопустимое имя для короткой ссылки"}), 400
        short = data['custom_id']
    else:
        short = MAIN_URL + get_unique_short_id()

    url = URLMap(original=data['url'], short=short)
    db.session.add(url)
    db.session.commit()

    return jsonify({
        "url": url.original,
        "short_link": url.short
    }), 201


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():

        if form.custom_id.data:
            if URLMap().query.filter_by(short=form.custom_id.data).first() is not None:
                flash('Такая ссылка уже существует!')
                return render_template('main.html', form=form)

            else:
                url = URLMap(
                    original=form.original_link.data,
                    short=form.custom_id.data,
                )
                db.session.add(url)
                db.session.commit()
                return render_template('main.html', form=form, urlmap=url)
        else:
            url = URLMap(
                original=form.original_link.data,
                short=MAIN_URL + get_unique_short_id())
            db.session.add(url)
            db.session.commit()
            return render_template('main.html', form=form, urlmap=url)
    return render_template('main.html', form=form)


if __name__ == '__main__':
    app.run()
