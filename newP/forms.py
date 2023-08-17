from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired


class SignupForm(FlaskForm):
    fullname = StringField("Fullname",validators=[DataRequired(message="Your Fullname is required")])
    email = StringField("Email",validators=[Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[EqualTo('password',message="Confirm Password must be equal to Password!")])
    btn = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email",validators=[Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    btn = SubmitField("Login") 
  

class PetProfileForm(FlaskForm):
    pname = StringField("Pet Name",validators=[DataRequired(message="Your Fullname is required")])
    ptype = FileField("Display Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    pgender = StringField("Gender", validators=[DataRequired(message="This field is required is required")]) 
    pcolor = StringField("Pet Color", validators=[DataRequired(message="This field is required is required")]) 
    pwieght = StringField("Display Picture", validators=[DataRequired(message="This field is required is required")]) 
    pdob = StringField("Pet DOB", validators=[DataRequired(message="This field is required is required")]) 
    pix = FileField("Display Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    btn = SubmitField("Update Profile")


class UserProfileForm(FlaskForm):
    fullname = StringField("Your Fullname",validators=[DataRequired(message="Your Fullname is required")])
    address = StringField("Address", validators=[DataRequired(message="This field is required")]) 
    pix = FileField("Display Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    gender = StringField("Gender", validators=[DataRequired(message="This field is required")]) 
    bio = StringField("Bio", validators=[DataRequired(message="Optional")]) 
    btn = SubmitField("Update Profile")


