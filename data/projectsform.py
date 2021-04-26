from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddProject(FlaskForm):
    """
    форма загрузки проекта на сервер
    """
    project_name = StringField('Название проекта', validators=[DataRequired()])
    text = TextAreaField('Описание программы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')