from flask import jsonify, request
from settings import BaseConfig
from yacut import app, db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, is_valid_url

MAIN_URL = BaseConfig.BASE_URL


@app.route('/api/id/<short_id>/', methods=['GET'], endpoint='api_get_original_url')
def get_original_url(short_id):
    url = URLMap.query.filter_by(
        short=MAIN_URL.rstrip('/') + '/' + short_id).first()
    if not url:
        return jsonify({"message": "Указанный id не найден"})
    return jsonify({"url": url.original})


@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data:
        return (jsonify({"message": "Отсутствует тело запроса"}), 400)
    if not data.get('url'):
        return (
            jsonify({"message": "\"url\" является обязательным полем!"}),
            400
        )
    if data.get('custom_id'):
        if URLMap.query.filter_by(short=data['custom_id']).first():
            return (
                jsonify(
                    {"message": "Предложенный вариант короткой ссылки уже "
                     "существует."}
                ),
                400
            )
        if not is_valid_url(data['custom_id']):
            return (
                jsonify(
                    {"message": "Указано недопустимое имя для короткой ссылки"}
                ),
                400
            )
        short = data['custom_id']
    else:
        short = MAIN_URL.rstrip('/') + '/' + get_unique_short_id()
    url = URLMap(original=data['url'], short=short)
    db.session.add(url)
    db.session.commit()
    return jsonify({
        "url": url.original,
        "short_link": url.short
    }), 201