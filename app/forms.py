from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    FloatField, FileField
)
from wtforms.validators import (
    DataRequired, EqualTo, Length, Email, NumberRange, Optional
)

# ✅ Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# ✅ Registration Form
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# ✅ Employee Form (Updated)
class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    position = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Add Employee')

# ✅ Add Employee Form (RESTORED)
class AddEmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    submit = SubmitField('Add Employee')

# ✅ Profile Form (Added Optional Validator)
class ProfileForm(FlaskForm):
    phone = StringField('Phone', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional()])
    submit = SubmitField('Update Profile')

# ✅ Goal Form (Progress Range Limited)
class GoalForm(FlaskForm):
    description = StringField('Goal Description', validators=[DataRequired()])
    progress = FloatField('Progress', validators=[NumberRange(min=0, max=100)], default=0.0)
    submit = SubmitField('Add Goal')

# ✅ Course Form
class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired()])
    description = TextAreaField('Course Description')
    submit = SubmitField('Add Course')

# ✅ Reset Password Request Form (Email Validation Added)
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

# ✅ Upload Form (Updated to Allow Multiple Files)
class UploadForm(FlaskForm):
    files = FileField('Upload Files', validators=[DataRequired()], render_kw={"multiple": True})
    submit = SubmitField('Upload')

# ✅ Post Update Form (For Admin Updates)
class PostUpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post Update')
