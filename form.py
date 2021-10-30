from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')



class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember =BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddGPUForm(FlaskForm):
    name  = StringField('name', validators=[DataRequired()])
    manufacturer = StringField('manufacturer', validators=[DataRequired()])
    dateissued = StringField('dateissued', validators=[DataRequired()])
    geometryshader = BooleanField('geometryshader')
    tesselationShader = BooleanField('tesselationShader')
    shaderInt16 = BooleanField('shaderInt16')
    sparseBinding = BooleanField('sparseBinding')
    texturecompressionETC2 = BooleanField('texturecompressionETC2')
    vertexPipelineStoresAndAtomics = BooleanField('vertexPipelineStoresAndAtomics')
    submit = SubmitField('Submit')
