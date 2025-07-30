from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import (Item, Department, Employee, Location, StockEntry, 
                   StockIssueRequest, StockIssueItem, StockBalance, AuditLog,
                   get_stock_balance, update_stock_balance)
from forms import (ItemForm, DepartmentForm, EmployeeForm, LocationForm, 
                  StockEntryForm, StockIssueRequestForm, StockIssueItemForm, ApprovalForm)
from datetime import datetime
import json
from sqlalchemy import or_, and_

main_bp = Blueprint('main', __name__)

def log_audit(table_name, record_id, action, old_values=None, new_values=None):
    """Helper function to log audit trail"""
    if current_user.is_authenticated:
        audit = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            user_id=current_user.id
        )
        db.session.add(audit)

@main_bp.route('/')
@login_required
def dashboard():
    # Get summary statistics
    total_items = Item.query.filter_by(is_active=True).count()
    total_locations = Location.query.filter_by(is_active=True).count()
    pending_requests = StockIssueRequest.query.filter_by(status='pending').count()
    
    # Get recent activities
    recent_entries = StockEntry.query.order_by(StockEntry.created_at.desc()).limit(5).all()
    recent_requests = StockIssueRequest.query.order_by(StockIssueRequest.created_at.desc()).limit(5).all()
    
    # Get low stock items (items with balance <= 5)
    low_stock = db.session.query(StockBalance, Item, Location).join(Item).join(Location).filter(StockBalance.balance <= 5).all()
    
    return render_template('dashboard.html', 
                         total_items=total_items,
                         total_locations=total_locations,
                         pending_requests=pending_requests,
                         recent_entries=recent_entries,
                         recent_requests=recent_requests,
                         low_stock=low_stock)

# Item Master Routes
@main_bp.route('/masters/items')
@login_required
def items():
    search = request.args.get('search', '')
    items = Item.query.filter_by(is_active=True)
    if search:
        items = items.filter(or_(Item.code.contains(search), Item.name.contains(search)))
    items = items.all()
    return render_template('masters/items.html', items=items, search=search)

@main_bp.route('/masters/items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if current_user.role not in ['admin']:
        flash('You do not have permission to add items.', 'error')
        return redirect(url_for('main.items'))
    
    form = ItemForm()
    if form.validate_on_submit():
        # Check for duplicate code
        existing = Item.query.filter_by(code=form.code.data).first()
        if existing:
            flash('Item code already exists.', 'error')
        else:
            item = Item(
                code=form.code.data,
                name=form.name.data,
                make=form.make.data,
                variant=form.variant.data,
                description=form.description.data
            )
            db.session.add(item)
            db.session.commit()
            log_audit('item', item.id, 'CREATE', new_values=form.data)
            flash('Item added successfully.', 'success')
            return redirect(url_for('main.items'))
    
    return render_template('masters/items.html', form=form, mode='add')

@main_bp.route('/masters/items/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_item(id):
    if current_user.role not in ['admin']:
        flash('You do not have permission to edit items.', 'error')
        return redirect(url_for('main.items'))
    
    item = Item.query.get_or_404(id)
    form = ItemForm(obj=item)
    
    if form.validate_on_submit():
        # Check for duplicate code (excluding current item)
        existing = Item.query.filter(Item.code == form.code.data, Item.id != id).first()
        if existing:
            flash('Item code already exists.', 'error')
        else:
            old_values = {
                'code': item.code,
                'name': item.name,
                'make': item.make,
                'variant': item.variant,
                'description': item.description
            }
            
            item.code = form.code.data
            item.name = form.name.data
            item.make = form.make.data
            item.variant = form.variant.data
            item.description = form.description.data
            
            db.session.commit()
            log_audit('item', item.id, 'UPDATE', old_values=old_values, new_values=form.data)
            flash('Item updated successfully.', 'success')
            return redirect(url_for('main.items'))
    
    return render_template('masters/items.html', form=form, item=item, mode='edit')

@main_bp.route('/masters/items/delete/<int:id>')
@login_required
def delete_item(id):
    if current_user.role not in ['admin']:
        flash('You do not have permission to delete items.', 'error')
        return redirect(url_for('main.items'))
    
    item = Item.query.get_or_404(id)
    
    # Check if item has stock entries or issues
    has_entries = StockEntry.query.filter_by(item_id=id).first()
    has_issues = StockIssueItem.query.filter_by(item_id=id).first()
    
    if has_entries or has_issues:
        flash('Cannot delete item - it has stock entries or issues.', 'error')
    else:
        old_values = {
            'code': item.code,
            'name': item.name,
            'make': item.make,
            'variant': item.variant,
            'description': item.description
        }
        item.is_active = False
        db.session.commit()
        log_audit('item', item.id, 'DELETE', old_values=old_values)
        flash('Item deleted successfully.', 'success')
    
    return redirect(url_for('main.items'))

# Department Master Routes
@main_bp.route('/masters/departments')
@login_required
def departments():
    search = request.args.get('search', '')
    departments = Department.query.filter_by(is_active=True)
    if search:
        departments = departments.filter(or_(Department.code.contains(search), Department.name.contains(search)))
    departments = departments.all()
    return render_template('masters/departments.html', departments=departments, search=search)

@main_bp.route('/masters/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    if current_user.role not in ['admin']:
        flash('You do not have permission to add departments.', 'error')
        return redirect(url_for('main.departments'))
    
    form = DepartmentForm()
    if form.validate_on_submit():
        existing = Department.query.filter_by(code=form.code.data).first()
        if existing:
            flash('Department code already exists.', 'error')
        else:
            department = Department(
                code=form.code.data,
                name=form.name.data,
                hod_id=form.hod_id.data if form.hod_id.data != 0 else None
            )
            db.session.add(department)
            db.session.commit()
            log_audit('department', department.id, 'CREATE', new_values=form.data)
            flash('Department added successfully.', 'success')
            return redirect(url_for('main.departments'))
    
    return render_template('masters/departments.html', form=form, mode='add')

# Employee Master Routes
@main_bp.route('/masters/employees')
@login_required
def employees():
    search = request.args.get('search', '')
    employees = Employee.query.filter_by(is_active=True)
    if search:
        employees = employees.filter(or_(Employee.emp_id.contains(search), Employee.name.contains(search)))
    employees = employees.all()
    return render_template('masters/employees.html', employees=employees, search=search)

@main_bp.route('/masters/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.role not in ['admin']:
        flash('You do not have permission to add employees.', 'error')
        return redirect(url_for('main.employees'))
    
    form = EmployeeForm()
    if form.validate_on_submit():
        existing = Employee.query.filter_by(emp_id=form.emp_id.data).first()
        if existing:
            flash('Employee ID already exists.', 'error')
        else:
            employee = Employee(
                emp_id=form.emp_id.data,
                name=form.name.data,
                department_id=form.department_id.data,
                user_id=form.user_id.data if form.user_id.data != 0 else None
            )
            db.session.add(employee)
            db.session.commit()
            log_audit('employee', employee.id, 'CREATE', new_values=form.data)
            flash('Employee added successfully.', 'success')
            return redirect(url_for('main.employees'))
    
    return render_template('masters/employees.html', form=form, mode='add')

# Location Master Routes
@main_bp.route('/masters/locations')
@login_required
def locations():
    search = request.args.get('search', '')
    locations = Location.query.filter_by(is_active=True)
    if search:
        locations = locations.filter(or_(Location.office.contains(search), Location.room_store.contains(search)))
    locations = locations.all()
    return render_template('masters/locations.html', locations=locations, search=search)

@main_bp.route('/masters/locations/add', methods=['GET', 'POST'])
@login_required
def add_location():
    if current_user.role not in ['admin']:
        flash('You do not have permission to add locations.', 'error')
        return redirect(url_for('main.locations'))
    
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(
            office=form.office.data,
            room_store=form.room_store.data
        )
        db.session.add(location)
        db.session.commit()
        log_audit('location', location.id, 'CREATE', new_values=form.data)
        flash('Location added successfully.', 'success')
        return redirect(url_for('main.locations'))
    
    return render_template('masters/locations.html', form=form, mode='add')

# Stock Entry Routes
@main_bp.route('/stock/entries')
@login_required
def stock_entries():
    entries = StockEntry.query.order_by(StockEntry.created_at.desc()).all()
    return render_template('stock/entry.html', entries=entries)

@main_bp.route('/stock/entries/add', methods=['GET', 'POST'])
@login_required
def add_stock_entry():
    form = StockEntryForm()
    if form.validate_on_submit():
        entry = StockEntry(
            item_id=form.item_id.data,
            location_id=form.location_id.data,
            quantity_procured=form.quantity_procured.data,
            description=form.description.data,
            remarks=form.remarks.data,
            created_by=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        
        # Update stock balance
        update_stock_balance(form.item_id.data, form.location_id.data, form.quantity_procured.data)
        
        log_audit('stock_entry', entry.id, 'CREATE', new_values=form.data)
        flash('Stock entry added successfully.', 'success')
        return redirect(url_for('main.stock_entries'))
    
    return render_template('stock/entry.html', form=form, mode='add')

# Stock Issue Routes
@main_bp.route('/stock/issues')
@login_required
def stock_issues():
    if current_user.role == 'admin':
        requests = StockIssueRequest.query.order_by(StockIssueRequest.created_at.desc()).all()
    elif current_user.role == 'hod':
        # HODs see requests from their departments
        hod_departments = Department.query.filter_by(hod_id=current_user.id).all()
        dept_ids = [d.id for d in hod_departments]
        requests = StockIssueRequest.query.filter(StockIssueRequest.department_id.in_(dept_ids)).order_by(StockIssueRequest.created_at.desc()).all()
    else:
        # Regular users see only their requests
        requests = StockIssueRequest.query.filter_by(created_by=current_user.id).order_by(StockIssueRequest.created_at.desc()).all()
    
    return render_template('stock/issue.html', requests=requests)

@main_bp.route('/stock/issues/add', methods=['GET', 'POST'])
@login_required
def add_stock_issue():
    form = StockIssueRequestForm()
    if form.validate_on_submit():
        # Generate request number
        import uuid
        request_number = f"REQ-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        request_obj = StockIssueRequest(
            request_number=request_number,
            requester_id=form.requester_id.data,
            department_id=form.department_id.data,
            purpose=form.purpose.data,
            approval_flow=form.approval_flow.data,
            approver_id=form.approver_id.data if form.approval_flow.data == 'alternate' and form.approver_id.data != 0 else None,
            created_by=current_user.id
        )
        db.session.add(request_obj)
        db.session.commit()
        
        log_audit('stock_issue_request', request_obj.id, 'CREATE', new_values=form.data)
        flash('Stock issue request created successfully.', 'success')
        return redirect(url_for('main.stock_issue_detail', id=request_obj.id))
    
    return render_template('stock/issue.html', form=form, mode='add')

@main_bp.route('/stock/issues/<int:id>')
@login_required
def stock_issue_detail(id):
    request_obj = StockIssueRequest.query.get_or_404(id)
    
    # Check permissions
    if current_user.role not in ['admin'] and request_obj.created_by != current_user.id:
        if current_user.role == 'hod':
            # Check if HOD manages this department
            hod_departments = Department.query.filter_by(hod_id=current_user.id).all()
            if request_obj.department_id not in [d.id for d in hod_departments]:
                flash('You do not have permission to view this request.', 'error')
                return redirect(url_for('main.stock_issues'))
        else:
            flash('You do not have permission to view this request.', 'error')
            return redirect(url_for('main.stock_issues'))
    
    item_form = StockIssueItemForm()
    approval_form = ApprovalForm()
    
    return render_template('stock/issue_detail.html', 
                         request=request_obj, 
                         item_form=item_form,
                         approval_form=approval_form)

@main_bp.route('/stock/issues/<int:id>/add_item', methods=['POST'])
@login_required
def add_issue_item(id):
    request_obj = StockIssueRequest.query.get_or_404(id)
    
    if request_obj.status not in ['draft']:
        flash('Cannot add items to this request.', 'error')
        return redirect(url_for('main.stock_issue_detail', id=id))
    
    form = StockIssueItemForm()
    if form.validate_on_submit():
        # Check available stock
        available = get_stock_balance(form.item_id.data, form.location_id.data)
        if available < form.quantity_requested.data:
            flash(f'Insufficient stock. Available: {available}', 'error')
        else:
            issue_item = StockIssueItem(
                request_id=id,
                item_id=form.item_id.data,
                location_id=form.location_id.data,
                quantity_requested=form.quantity_requested.data,
                description=form.description.data
            )
            db.session.add(issue_item)
            db.session.commit()
            flash('Item added to request.', 'success')
    
    return redirect(url_for('main.stock_issue_detail', id=id))

@main_bp.route('/stock/issues/<int:id>/submit')
@login_required
def submit_issue_request(id):
    request_obj = StockIssueRequest.query.get_or_404(id)
    
    if request_obj.status != 'draft' or request_obj.created_by != current_user.id:
        flash('Cannot submit this request.', 'error')
        return redirect(url_for('main.stock_issue_detail', id=id))
    
    if not request_obj.items:
        flash('Cannot submit request without items.', 'error')
        return redirect(url_for('main.stock_issue_detail', id=id))
    
    request_obj.status = 'pending'
    db.session.commit()
    
    log_audit('stock_issue_request', request_obj.id, 'UPDATE', 
              old_values={'status': 'draft'}, 
              new_values={'status': 'pending'})
    
    flash('Request submitted for approval.', 'success')
    return redirect(url_for('main.stock_issue_detail', id=id))

@main_bp.route('/stock/issues/<int:id>/approve', methods=['POST'])
@login_required
def approve_issue_request(id):
    request_obj = StockIssueRequest.query.get_or_404(id)
    form = ApprovalForm()
    
    if form.validate_on_submit():
        action = form.action.data
        
        if action == 'approve':
            if current_user.role == 'hod' or (current_user.role == 'approver' and request_obj.approver_id == current_user.id):
                if request_obj.approval_flow == 'alternate' and current_user.role == 'approver':
                    # Conditional approval
                    request_obj.conditional_approved_by = current_user.id
                    request_obj.conditional_approved_at = datetime.utcnow()
                    request_obj.status = 'conditional_approved'
                    flash('Request conditionally approved and forwarded to HOD.', 'success')
                else:
                    # Final approval
                    request_obj.hod_approved_by = current_user.id
                    request_obj.hod_approved_at = datetime.utcnow()
                    request_obj.status = 'approved'
                    flash('Request approved successfully.', 'success')
                
                db.session.commit()
                log_audit('stock_issue_request', request_obj.id, 'APPROVE')
            else:
                flash('You do not have permission to approve this request.', 'error')
        
        elif action == 'reject':
            request_obj.status = 'rejected'
            request_obj.rejection_reason = form.rejection_reason.data
            db.session.commit()
            log_audit('stock_issue_request', request_obj.id, 'REJECT')
            flash('Request rejected.', 'success')
    
    return redirect(url_for('main.stock_issue_detail', id=id))

@main_bp.route('/stock/issues/<int:id>/issue')
@login_required
def issue_stock(id):
    if current_user.role != 'admin':
        flash('You do not have permission to issue stock.', 'error')
        return redirect(url_for('main.stock_issue_detail', id=id))
    
    request_obj = StockIssueRequest.query.get_or_404(id)
    
    if request_obj.status != 'approved':
        flash('Request must be approved before issuing stock.', 'error')
        return redirect(url_for('main.stock_issue_detail', id=id))
    
    # Check and update stock for each item
    for item in request_obj.items:
        available = get_stock_balance(item.item_id, item.location_id)
        if available < item.quantity_requested:
            flash(f'Insufficient stock for {item.item.name}. Available: {available}', 'error')
            return redirect(url_for('main.stock_issue_detail', id=id))
    
    # Issue all items
    for item in request_obj.items:
        update_stock_balance(item.item_id, item.location_id, -item.quantity_requested)
        item.quantity_issued = item.quantity_requested
    
    request_obj.status = 'issued'
    request_obj.issued_by = current_user.id
    request_obj.issued_at = datetime.utcnow()
    
    db.session.commit()
    log_audit('stock_issue_request', request_obj.id, 'ISSUE')
    
    flash('Stock issued successfully.', 'success')
    return redirect(url_for('main.stock_issue_detail', id=id))

# Approval Routes
@main_bp.route('/approvals/pending')
@login_required
def pending_approvals():
    if current_user.role == 'hod':
        # HOD sees requests from their departments
        hod_departments = Department.query.filter_by(hod_id=current_user.id).all()
        dept_ids = [d.id for d in hod_departments]
        requests = StockIssueRequest.query.filter(
            and_(
                StockIssueRequest.department_id.in_(dept_ids),
                or_(
                    StockIssueRequest.status == 'pending',
                    StockIssueRequest.status == 'conditional_approved'
                )
            )
        ).all()
    elif current_user.role == 'approver':
        # Approvers see their assigned requests
        requests = StockIssueRequest.query.filter(
            and_(
                StockIssueRequest.approver_id == current_user.id,
                StockIssueRequest.status == 'pending'
            )
        ).all()
    else:
        requests = []
    
    return render_template('approval/pending.html', requests=requests)

# Reports Routes
@main_bp.route('/reports/stock')
@login_required
def stock_report():
    item_filter = request.args.get('item', '')
    location_filter = request.args.get('location', '')
    
    query = db.session.query(StockBalance, Item, Location).join(Item).join(Location)
    
    if item_filter:
        query = query.filter(Item.name.contains(item_filter))
    if location_filter:
        query = query.filter(Location.office.contains(location_filter))
    
    stock_data = query.all()
    
    # Get filter options
    items = Item.query.filter_by(is_active=True).all()
    locations = Location.query.filter_by(is_active=True).all()
    
    return render_template('reports/stock_report.html', 
                         stock_data=stock_data,
                         items=items,
                         locations=locations,
                         item_filter=item_filter,
                         location_filter=location_filter)

# API Endpoints for AJAX
@main_bp.route('/api/stock_balance/<int:item_id>/<int:location_id>')
@login_required
def api_stock_balance(item_id, location_id):
    balance = get_stock_balance(item_id, location_id)
    return jsonify({'balance': balance})

@main_bp.route('/api/items_by_location/<int:location_id>')
@login_required
def api_items_by_location(location_id):
    # Get items that have stock in this location
    balances = StockBalance.query.filter(
        StockBalance.location_id == location_id,
        StockBalance.balance > 0
    ).all()
    
    items = []
    for balance in balances:
        items.append({
            'id': balance.item.id,
            'code': balance.item.code,
            'name': balance.item.name,
            'balance': balance.balance
        })
    
    return jsonify(items)
