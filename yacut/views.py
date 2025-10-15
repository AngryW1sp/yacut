from flask import abort, flash, redirect, render_template
from settings import BaseConfig
from yacut.forms import URLFileForm, URLMapForm
from models import URLMap
from yacut import app, db
from yacut.utils import get_unique_short_id, async_upload_to_yandex

MAIN_URL = BaseConfig.BASE_URL


@app.route('/<url>', methods=['GET'])
def redirect_view(url):
    url_query = URLMap.query.filter_by(
        short=MAIN_URL.rstrip('/') + '/' + url).first()
    if url_query:
        original_url = url_query.original
        return redirect(original_url)
    else:
        abort(404)


@app.route('/download', methods=['GET', 'POST'])
async def download_view():
    form = URLFileForm()
    uploaded = {}
    if form.validate_on_submit():
        urls = await async_upload_to_yandex(form.files.data)
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


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        if form.custom_id.data:
            if URLMap.query.filter_by(short=form.custom_id.data).first() is not None:
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
                short=MAIN_URL.rstrip('/') + '/' + get_unique_short_id()
            )
            db.session.add(url)
            db.session.commit()
            return render_template('main.html', form=form, urlmap=url)
    return render_template('main.html', form=form)