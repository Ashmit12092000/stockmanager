# Stock Management System - Testing Workflow Guide

## 🎯 Overview

This document provides a comprehensive testing workflow for the Stock Issue Management System. The application has been pre-populated with sample data to demonstrate all key features and workflows.

## 🚀 Quick Start

1. **Navigate to the application**: http://localhost:5000
2. **Sample data has been created** - ready for immediate testing
3. **Multiple user accounts available** with different roles and permissions

## 👥 Test User Accounts

| Username | Password | Role | Department | Purpose |
|----------|----------|------|------------|---------|
| `admin` | `admin123` | Administrator | - | Full system access, stock management |
| `john_doe` | `password123` | HOD | IT Department | Department head approvals |
| `jane_smith` | `password123` | Conditional Approver | HR Department | Alternate approval flow |
| `bob_wilson` | `password123` | Employee | IT Department | Regular stock requests |

## 📊 Pre-loaded Sample Data

### Departments
- **IT Department** (HOD: John Doe)
- **HR Department** 
- **Finance Department**

### Locations
- **Main Office** - IT Store Room
- **Warehouse** - General Storage  
- **Branch Office** - Supply Cabinet

### Items in Stock
| Item | Code | Available Stock | Location |
|------|------|----------------|----------|
| Dell Latitude Laptops | LAPTOP001 | 15 units | Main Office |
| Wireless Mice | MOUSE001 | 25 units | Main Office |
| Mechanical Keyboards | KEYBOARD001 | 20 units | Main Office |
| 24" LED Monitors | MONITOR001 | 30 units | Warehouse |
| USB-C Cables | CABLE001 | 50 units | Warehouse |
| Bluetooth Headsets | HEADSET001 | 10 units | Branch Office |
| Laser Printers | PRINTER001 | 5 units | Main Office |
| WiFi Routers | ROUTER001 | 8 units | Main Office |
| iPad Pro Tablets | TABLET001 | 12 units | Branch Office |
| Office Phones | PHONE001 | 15 units | Main Office |

## 🔄 Complete Testing Workflow

### Phase 1: System Administration (Admin User)

1. **Login as Administrator**
   - Username: `admin`
   - Password: `admin123`
   - Expected: Access to full dashboard with statistics

2. **Explore Dashboard**
   - ✅ View total items, departments, employees
   - ✅ Check recent activities
   - ✅ Review stock level indicators
   - ✅ Notice low stock alerts (if any)

3. **Master Data Management**
   - **Items Master**: Review all 10 items with details
   - **Departments**: Verify 3 departments with HOD assignments
   - **Employees**: Check 4 employees linked to departments
   - **Locations**: Confirm 3 storage locations

4. **Stock Management**
   - **Stock Entries**: Review procurement history (10 entries)
   - **Stock Reports**: Generate balance reports with charts
   - **Search & Filter**: Test item and location filtering

### Phase 2: Employee Stock Request (Employee User)

1. **Switch to Employee Account**
   - Logout admin and login as `bob_wilson` / `password123`
   - Expected: Limited access, employee-level dashboard

2. **Create New Stock Issue Request**
   - Navigate to "Stock Issue Requests" 
   - Click "Create New Request"
   - Fill request details:
     - **Request Type**: Regular
     - **Department**: IT Department (auto-selected)
     - **Description**: "Setup for new employee workstation"

3. **Add Items to Request**
   - Add multiple items:
     - **Laptop**: 1 unit from Main Office
     - **Monitor**: 1 unit from Warehouse
     - **Mouse**: 1 unit from Main Office
     - **Keyboard**: 1 unit from Main Office
   - Verify stock availability checking
   - Add descriptions for each item

4. **Submit Request**
   - Review all items in request
   - Submit for approval
   - Note request status change to "Pending"

### Phase 3: HOD Approval (Regular Flow)

1. **Switch to HOD Account**
   - Logout and login as `john_doe` / `password123`
   - Expected: HOD dashboard with pending approvals

2. **Review Pending Requests**
   - Navigate to "Pending Approvals"
   - Find the request created by Bob Wilson
   - Click to view detailed request

3. **Approve Request**
   - Review all requested items and quantities
   - Check stock availability
   - Provide approval with remarks
   - Confirm approval action
   - Verify status change to "Approved"

### Phase 4: Stock Issuance (Admin User)

1. **Return to Admin Account**
   - Login as `admin` / `admin123`
   - Navigate to approved requests

2. **Issue Stock**
   - Find the approved request
   - Click "Issue Stock"
   - Confirm all items can be issued
   - Complete the issuance process

3. **Verify Stock Updates**
   - Check updated stock balances
   - Review audit trail
   - Confirm stock levels decreased appropriately

### Phase 5: Alternate Approval Flow

1. **Create Request with Conditional Approver**
   - Login as `bob_wilson` again
   - Create new request with:
     - **Request Type**: Alternate (with conditional approver)
     - **Conditional Approver**: Jane Smith
     - Add different items to request

2. **Conditional Approval**
   - Login as `jane_smith` / `password123`
   - Review and provide conditional approval
   - Add conditional approval remarks

3. **Final HOD Approval**
   - Login as `john_doe` 
   - Review conditionally approved request
   - Provide final approval
   - Complete the alternate flow

### Phase 6: Rejection Workflow

1. **Create Request for Rejection**
   - Create a request with excessive quantities
   - Or inappropriate items for testing

2. **Test Rejection Process**
   - Login as HOD
   - Reject request with detailed reason
   - Verify rejection notification and audit trail

## 🎯 Key Features to Validate

### Authentication & Security
- ✅ Role-based access control working
- ✅ Users can only access appropriate features
- ✅ Session management functioning
- ✅ Logout/login transitions smooth

### Stock Management
- ✅ Real-time stock balance checking
- ✅ Preventing over-issuance
- ✅ Stock level updates after issuance
- ✅ Low stock alerts functioning

### Approval Workflow
- ✅ Multi-level approval working
- ✅ Conditional approval flow
- ✅ Email notifications (if configured)
- ✅ Approval status tracking

### User Interface
- ✅ Responsive dark theme design
- ✅ Bootstrap components working
- ✅ Form validations functioning
- ✅ Search and filtering operational
- ✅ Charts and reports displaying

### Audit & Reporting
- ✅ All actions logged in audit trail
- ✅ Stock reports generating correctly
- ✅ Activity timeline showing
- ✅ User action tracking working

## 🔍 Advanced Testing Scenarios

### Edge Cases to Test

1. **Stock Availability**
   - Try requesting more items than available
   - Test with zero stock items
   - Verify error messages

2. **Concurrent Requests**
   - Create multiple requests for same items
   - Test stock allocation conflicts
   - Verify data consistency

3. **Permission Boundaries**
   - Try accessing admin features as employee
   - Test cross-department approvals
   - Verify role restrictions

4. **Data Validation**
   - Submit forms with invalid data
   - Test required field validations
   - Verify error handling

### Performance Testing

1. **Load Testing**
   - Create multiple users simultaneously
   - Test with large quantities
   - Monitor response times

2. **Data Volume**
   - Add more items and locations
   - Test with hundreds of requests
   - Verify search performance

## 📋 Test Results Checklist

### ✅ Basic Functionality
- [ ] User authentication working
- [ ] Dashboard displaying correctly
- [ ] Master data accessible
- [ ] Forms submitting properly

### ✅ Stock Operations
- [ ] Stock entries creating
- [ ] Balance calculations correct
- [ ] Issue requests processing
- [ ] Stock issuance working

### ✅ Approval Workflow
- [ ] Regular approval flow functional
- [ ] Alternate approval flow working
- [ ] Rejection process operational
- [ ] Status transitions correct

### ✅ Reporting & Analytics
- [ ] Stock reports generating
- [ ] Charts displaying properly
- [ ] Audit trail recording
- [ ] Search functionality working

### ✅ User Experience
- [ ] Navigation intuitive
- [ ] Error messages clear
- [ ] Success notifications working
- [ ] Responsive design functioning

## 🚨 Common Issues & Solutions

### Login Problems
- **Issue**: Cannot login with test accounts
- **Solution**: Ensure sample data was loaded with `python sample_workflow.py`

### Missing Data
- **Issue**: No items or departments showing
- **Solution**: Run the sample workflow script to populate data

### Permission Errors
- **Issue**: Access denied messages
- **Solution**: Verify user roles and login with appropriate account

### Stock Balance Issues
- **Issue**: Incorrect stock calculations
- **Solution**: Check audit logs and verify stock entry records

## 🎉 Success Indicators

The system is working correctly when:

1. **All user roles can login and access appropriate features**
2. **Stock requests flow through the complete approval process**
3. **Stock balances update correctly after issuance**
4. **Reports and charts display accurate data**
5. **Audit trail captures all user actions**
6. **UI is responsive and professional-looking**

## 🔄 Continuous Testing

For ongoing development:

1. **Run tests after each code change**
2. **Verify all user workflows still function**
3. **Check database integrity**
4. **Monitor application logs for errors**
5. **Test with different browsers and devices**

---

**Ready to test!** Navigate to http://localhost:5000 and begin with the admin login to explore the complete system.