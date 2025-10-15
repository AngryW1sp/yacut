from flask_wtf import FlaskForm
from wtforms import URLField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional


class URLMapForm(FlaskForm):
    original_link = URLField('Введите оригинальную ссылку',
                             validators=[DataRequired(message='Обязательное поле'), Length(1, 256)],)
    custom_id = URLField('Введите желаемую короткую ссылку(опционально)',
                         validators=[Optional(), Length(1, 256)],)


class URLFileForm(FlaskForm):
    files = MultipleFileField(
        validators=[DataRequired(message='Обязательное поле')])