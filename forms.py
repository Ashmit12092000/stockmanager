from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional
from wtforms.widgets import TextArea
from models import Department, Employee, Location, Item, User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])

class ItemForm(FlaskForm):
    code = StringField('Item Code', validators=[DataRequired(), Length(max=50)])
    name = StringField('Item Name', validators=[DataRequired(), Length(max=200)])
    make = StringField('Make', validators=[Optional(), Length(max=100)])
    variant = StringField('Variant', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])

class DepartmentForm(FlaskForm):
    code = StringField('Department Code', validators=[DataRequired(), Length(max=20)])
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    hod_id = SelectField('Head of Department', coerce=int, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.hod_id.choices = [(0, 'Select HOD')] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(role='hod').all()]

class EmployeeForm(FlaskForm):
    emp_id = StringField('Employee ID', validators=[DataRequired(), Length(max=20)])
    name = StringField('Employee Name', validators=[DataRequired(), Length(max=100)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    user_id = SelectField('User Account', coerce=int, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.department_id.choices = [(d.id, f"{d.code} - {d.name}") for d in Department.query.filter_by(is_active=True).all()]
        self.user_id.choices = [(0, 'No User Account')] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(is_active=True).all()]

class LocationForm(FlaskForm):
    office = StringField('Office', validators=[DataRequired(), Length(max=100)])
    room_store = StringField('Room/Store', validators=[DataRequired(), Length(max=100)])

class StockEntryForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    location_id = SelectField('Location', coerce=int, validators=[DataRequired()])
    quantity_procured = IntegerField('Quantity Procured', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Description', validators=[Optional()])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(StockEntryForm, self).__init__(*args, **kwargs)
        self.item_id.choices = [(i.id, f"{i.code} - {i.name}") for i in Item.query.filter_by(is_active=True).all()]
        self.location_id.choices = [(l.id, str(l)) for l in Location.query.filter_by(is_active=True).all()]

class StockIssueRequestForm(FlaskForm):
    requester_id = SelectField('Requester', coerce=int, validators=[DataRequired()])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    purpose = TextAreaField('Purpose', validators=[DataRequired()])
    approval_flow = SelectField('Approval Flow', choices=[('regular', 'Regular (HOD)'), ('alternate', 'Alternate (Conditional Approver)')], default='regular')
    approver_id = SelectField('Conditional Approver', coerce=int, validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(StockIssueRequestForm, self).__init__(*args, **kwargs)
        self.requester_id.choices = [(e.id, f"{e.emp_id} - {e.name}") for e in Employee.query.filter_by(is_active=True).all()]
        self.department_id.choices = [(d.id, f"{d.code} - {d.name}") for d in Department.query.filter_by(is_active=True).all()]
        self.approver_id.choices = [(0, 'Select Approver')] + [(u.id, f"{u.username} ({u.email})") for u in User.query.filter_by(role='approver').all()]

class StockIssueItemForm(FlaskForm):
    item_id = SelectField('Item', coerce=int, validators=[DataRequired()])
    location_id = SelectField('Location', coerce=int, validators=[DataRequired()])
    quantity_requested = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    description = TextAreaField('Description', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(StockIssueItemForm, self).__init__(*args, **kwargs)
        self.item_id.choices = [(i.id, f"{i.code} - {i.name}") for i in Item.query.filter_by(is_active=True).all()]
        self.location_id.choices = [(l.id, str(l)) for l in Location.query.filter_by(is_active=True).all()]

class ApprovalForm(FlaskForm):
    action = HiddenField('Action')
    rejection_reason = TextAreaField('Rejection Reason', validators=[Optional()])
