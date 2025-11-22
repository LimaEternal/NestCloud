from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField


class UploadForm(FlaskForm):
    file = FileField(
        "Файл",
        validators=[
            FileRequired(message="Пожалуйста, выберите файл"),
        ],
    )
    submit = SubmitField("Загрузить")
