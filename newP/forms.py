from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,TextAreaField, PasswordField, DateField, IntegerField
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


class EditPetProfileForm(FlaskForm):
    pet_name = StringField("Pet Name",validators=[DataRequired(message="Your Fullname is required")])
    #status = StringField("Status",validators=[DataRequired(message="This field is required")])
    breed = StringField("Breed",validators=[DataRequired(message="This field is required")])
    descript = TextAreaField("About Your Pet",validators=[DataRequired(message="This field is optional")])
    likes = TextAreaField("Likes",validators=[DataRequired(message="This field is optional")])
    dislikes = TextAreaField("Dislikes",validators=[DataRequired(message="This field is optional")])
    pic = FileField("Upload a Pet Cover Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    btn = SubmitField("Update Profile")


class UserProfileForm(FlaskForm):
    fullname = StringField("Your Fullname",validators=[DataRequired(message="Your Fullname is required")])
    address = StringField("Address", validators=[DataRequired(message="This field is required")]) 
    email = StringField("Email", validators=[DataRequired(message="This field is required")]) 
    pix = FileField("Display Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    gender = StringField("Gender", validators=[DataRequired(message="This field is required")]) 
    bio = StringField("Bio", validators=[DataRequired(message="Optional")]) 
    btn = SubmitField("Update Profile")


class VetProfileForm(FlaskForm):
    fullname = StringField("Your Fullname",validators=[DataRequired(message="Your Fullname is required")])
    address = StringField("Address", validators=[DataRequired(message="This field is required")]) 
    email = StringField("Email", validators=[DataRequired(message="This field is required")]) 
    pix = FileField("Display Picture", validators=[FileRequired(), FileAllowed(["jpg", "png"], 'Images Only') ])
    gender = StringField("Gender", validators=[DataRequired(message="This field is required")]) 
    bio = TextAreaField("Bio", validators=[DataRequired(message="Optional")]) 
    btn = SubmitField("Update Profile")


class AppointmentForm(FlaskForm):
    comments = TextAreaField("Anything we should know?",validators=[DataRequired(message="This field is required")])
    date = DateField("Pick a Date", validators=[DataRequired(message="This field is required")]) 
    btn = SubmitField("Submit")
 

class TreatmentForm(FlaskForm):
    currentWeight = StringField("Pet Current Weight", validators=[DataRequired(message="This field is required")]) 
    symptoms = StringField("Symptoms", validators=[DataRequired(message="This field is required")]) 
    prescription = StringField("Prescription", validators=[DataRequired(message="This field is required")]) 
    remark = StringField("Remark", validators=[DataRequired(message="This field is required")]) 
    btn = SubmitField("Update Profile")


class BillForm(FlaskForm):
    amount = IntegerField("Amount", validators=[DataRequired(message="This field is required")]) 
    deadline = DateField("Deadline", validators=[DataRequired(message="This field is required")]) 
    bills_reference_number = StringField("Ref Number", validators=[DataRequired(message="This field is required")]) 
    btn = SubmitField("Create Bill")
    