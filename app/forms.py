from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import EqualTo, Length
from wtforms.validators import Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('LOGIN')


class PersonForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[], validators=[DataRequired()])
    person_type = SelectField(
        'Person Type',
        choices=[
            ('Member', 'Member'),
            ('Visitor', 'Visitor'),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField('ADD PERSON')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from .models.category import Category
            categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
            self.category.choices = [(cat.name, cat.name) for cat in categories] or [
                ('Ladies', 'Ladies'),
                ('Men', 'Men'),
                ('Young People', 'Young People'),
                ('Young Professionals', 'Young Professionals'),
            ]
        except Exception:
            self.category.choices = [
                ('Ladies', 'Ladies'),
                ('Men', 'Men'),
                ('Young People', 'Young People'),
                ('Young Professionals', 'Young Professionals'),
            ]


class ChangeEmailForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_email = StringField('New email', validators=[DataRequired(), Length(min=3, max=128)])
    confirm_email = StringField('Confirm new email', validators=[DataRequired(), EqualTo('new_email', message='Emails must match')])
    submit = SubmitField('Change Email')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm new password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')
