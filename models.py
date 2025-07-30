from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='employee')  # admin, hod, approver, employee
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hod_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hod = db.relationship('User', backref='managed_departments')

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    department = db.relationship('Department', backref='employees')
    user = db.relationship('User', backref='employee_profile')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office = db.Column(db.String(100), nullable=False)
    room_store = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.office} - {self.room_store}"

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    make = db.Column(db.String(100))
    variant = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StockEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    quantity_procured = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    remarks = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Item', backref='stock_entries')
    location = db.relationship('Location', backref='stock_entries')
    creator = db.relationship('User', backref='created_stock_entries')

class StockIssueRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, pending, approved, rejected, issued
    approval_flow = db.Column(db.String(20), default='regular')  # regular, alternate
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # for alternate flow
    hod_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    hod_approved_at = db.Column(db.DateTime, nullable=True)
    conditional_approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    conditional_approved_at = db.Column(db.DateTime, nullable=True)
    issued_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    issued_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    requester = db.relationship('Employee', backref='stock_requests')
    department = db.relationship('Department', backref='stock_requests')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='alternate_approvals')
    hod_approver = db.relationship('User', foreign_keys=[hod_approved_by], backref='hod_approvals')
    conditional_approver = db.relationship('User', foreign_keys=[conditional_approved_by], backref='conditional_approvals')
    issuer = db.relationship('User', foreign_keys=[issued_by], backref='issued_requests')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_requests')

class StockIssueItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('stock_issue_request.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    quantity_requested = db.Column(db.Integer, nullable=False)
    quantity_issued = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    
    request = db.relationship('StockIssueRequest', backref='items')
    item = db.relationship('Item', backref='issue_items')
    location = db.relationship('Location', backref='issue_items')

class StockBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    balance = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    item = db.relationship('Item', backref='balances')
    location = db.relationship('Location', backref='balances')
    
    __table_args__ = (db.UniqueConstraint('item_id', 'location_id'),)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    old_values = db.Column(db.Text)  # JSON string
    new_values = db.Column(db.Text)  # JSON string
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='audit_logs')

# Helper function to get stock balance
def get_stock_balance(item_id, location_id):
    balance = StockBalance.query.filter_by(item_id=item_id, location_id=location_id).first()
    return balance.balance if balance else 0

# Helper function to update stock balance
def update_stock_balance(item_id, location_id, quantity_change):
    balance = StockBalance.query.filter_by(item_id=item_id, location_id=location_id).first()
    if not balance:
        balance = StockBalance(item_id=item_id, location_id=location_id, balance=0)
        db.session.add(balance)
    
    balance.balance += quantity_change
    balance.updated_at = datetime.utcnow()
    db.session.commit()
    return balance.balance
