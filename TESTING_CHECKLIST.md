# Testing Checklist - New Patient Registration Features

## Pre-Testing Requirements
- [ ] Application running on `http://localhost:5000` (or your configured port)
- [ ] Database initialized with clinic data
- [ ] Admin user account exists and verified

---

## 1. PUBLIC PATIENT SIGNUP TESTING

### 1.1 Access Signup Page
- [ ] Navigate to `http://localhost:5000/signup`
- [ ] Page loads without errors
- [ ] Form title displays "Create Account"
- [ ] All form fields visible

### 1.2 Clinic Dropdown Functionality
- [ ] Clinic dropdown is visible
- [ ] Dropdown contains all clinics from database
- [ ] Default option shows "-- Select a department --"
- [ ] Can select each clinic option
- [ ] Selected value persists on form submission (if validation fails)

### 1.3 Form Validation - Missing Clinic
- [ ] Leave clinic dropdown on default value
- [ ] Fill all other fields correctly
- [ ] Click "Create Account"
- [ ] See error message: "Please select a department."
- [ ] Form remains populated with entered data
- [ ] User can select clinic and resubmit

### 1.4 Form Validation - Email Issues
- [ ] Try registering with invalid email format
- [ ] Try registering with existing email
- [ ] Verify appropriate error messages
- [ ] Form preserves other data on error

### 1.5 Form Validation - Password Issues
- [ ] Try mismatched passwords
- [ ] Try empty password field
- [ ] Verify error messages display
- [ ] Password visibility toggle works

### 1.6 Successful Registration
- [ ] Fill form completely:
  - Email: `testpatient@example.com`
  - First name: `John`
  - Last name: `Doe`
  - Department: Select any clinic
  - Password: `SecurePass123`
  - Confirm: `SecurePass123`
- [ ] Click "Create Account"
- [ ] See success message: "Your account has been created. Please log in."
- [ ] Redirected to signin page
- [ ] Can login with new credentials

### 1.7 Database Verification - Patient Registration
Run query:
```sql
SELECT r.recipient_id, a.email_address, a.given_name, a.surname, c.clinic_title
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
LEFT JOIN clinic c ON r.clinic_id = c.clinic_id
WHERE a.email_address = 'testpatient@example.com';
```
- [ ] Result shows patient record
- [ ] clinic_id is NOT NULL
- [ ] clinic_title matches selected department

---

## 2. ADMIN PATIENT REGISTRATION TESTING

### 2.1 Access Admin Page (Authentication)
- [ ] Login as regular patient
- [ ] Try accessing `/governance/patients/new`
- [ ] See error: "Administrative access required."
- [ ] Logout and login as admin
- [ ] Navigate to `/governance/patients/new`
- [ ] Page loads successfully

### 2.2 Admin Form Presentation
- [ ] Form title: "Register New Patient"
- [ ] Subtitle: "Add a patient account through admin panel"
- [ ] All fields visible: Email, First Name, Last Name, Department, Password, Confirm Password
- [ ] Required fields marked with red asterisk (*)
- [ ] Helper text visible under each field
- [ ] Action buttons: "Create Patient" and "Cancel"

### 2.3 Clinic Dropdown in Admin Form
- [ ] Clinic dropdown populated with all departments
- [ ] Can select any clinic
- [ ] Pre-selected value shows on validation error

### 2.4 Admin Form Validation - Missing Fields
- [ ] Try submitting empty form
- [ ] Client-side alert: "Email address is required."
- [ ] Fill email, try again
- [ ] Alert: "Please select a department for this patient."
- [ ] Select clinic, try again
- [ ] Alert: "Password fields cannot be empty."

### 2.5 Admin Form Validation - Password Issues
- [ ] Enter non-matching passwords
- [ ] Alert: "Passwords do not match."
- [ ] Enter password less than 6 characters
- [ ] Alert: "Password must be at least 6 characters long."
- [ ] Enter matching passwords (6+ chars)
- [ ] Submit succeeds

### 2.6 Admin Form Validation - Email Uniqueness
- [ ] Try registering with email of existing patient
- [ ] Submit form
- [ ] See error: "Email address is already registered."
- [ ] Form data preserved
- [ ] Can change email and resubmit

### 2.7 Successful Admin Patient Creation
- [ ] Fill form:
  - Email: `adminpatient@example.com`
  - First Name: `Jane`
  - Last Name: `Smith`
  - Department: Select clinic (e.g., "Cardiology")
  - Password: `AdminPass123`
  - Confirm: `AdminPass123`
- [ ] Click "Create Patient"
- [ ] Success message: "Patient Jane Smith has been successfully registered."
- [ ] Redirected to recipients list
- [ ] New patient visible in list

### 2.8 Cancel Button
- [ ] Click "Cancel" on admin form
- [ ] Redirected to `/governance/recipients`
- [ ] No patient created
- [ ] Form data not saved

### 2.9 Database Verification - Admin Creation
Run query:
```sql
SELECT r.recipient_id, a.email_address, a.given_name, a.surname, 
       c.clinic_title, a.access_tier.tier_name
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
LEFT JOIN clinic c ON r.clinic_id = c.clinic_id
WHERE a.email_address = 'adminpatient@example.com';
```
- [ ] Patient record exists
- [ ] clinic_id is populated
- [ ] clinic_title matches selected department
- [ ] access_level is 'patient'

---

## 3. SECURITY TESTING

### 3.1 Password Hashing
```python
# In Flask shell
from models import Account
user = Account.query.filter_by(email_address='testpatient@example.com').first()
print(user.credential_hash)
print(user.credential_hash.startswith('pbkdf2:sha256'))  # Should be True
```
- [ ] Password is hashed (not stored in plain text)
- [ ] Hash format is werkzeug pbkdf2:sha256
- [ ] Can login with correct password
- [ ] Cannot login with incorrect password

### 3.2 Authorization - Admin Only Route
- [ ] Non-admin user cannot access `/governance/patients/new`
- [ ] Admin user can access route
- [ ] Decorator `@administrator_only` is working

### 3.3 SQL Injection Prevention
- [ ] Try email: `admin@test.com' OR '1'='1`
- [ ] Should treat as literal email string
- [ ] Should not bypass validation

### 3.4 Foreign Key Integrity
- [ ] Try creating patient with non-existent clinic_id via API/curl
- [ ] Should see error: "Selected department is invalid."
- [ ] Database foreign key prevents orphaned records

---

## 4. USER EXPERIENCE TESTING

### 4.1 Form Styling
- [ ] Signup form is centered and properly styled
- [ ] Admin form has professional appearance
- [ ] Bootstrap classes applied correctly
- [ ] Responsive design works on mobile/tablet

### 4.2 Password Visibility Toggle
- [ ] Click eye icon to show password
- [ ] Password becomes visible (type changes to text)
- [ ] Icon changes from eye to eye-slash
- [ ] Click again to hide password
- [ ] Icon changes back to eye
- [ ] Works for both password and confirm password fields

### 4.3 Form Data Persistence
- [ ] After validation error, pre-filled fields remain
- [ ] Email, names, clinic selection all preserved
- [ ] Only empty/invalid fields show error
- [ ] User doesn't have to re-enter correct data

### 4.4 Error Messages
- [ ] Messages are clear and actionable
- [ ] Messages indicate what went wrong
- [ ] Messages help user know what to fix

### 4.5 Success Messages
- [ ] Success message displays briefly
- [ ] Message clearly indicates action completed
- [ ] User redirected to appropriate next page

---

## 5. DATABASE CONSISTENCY TESTING

### 5.1 Clinic Assignment
Run query for all patients with clinics:
```sql
SELECT a.email_address, a.given_name, a.surname, c.clinic_title
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
LEFT JOIN clinic c ON r.clinic_id = c.clinic_id
ORDER BY a.created_on DESC;
```
- [ ] All newly created patients have clinic_id
- [ ] clinic_title matches selected department
- [ ] No orphaned clinic_id references

### 5.2 Account-Recipient Relationship
Run query:
```sql
SELECT COUNT(*) as total_recipients
FROM recipient WHERE recipient_id IS NOT NULL;

SELECT COUNT(*) as total_accounts_with_patient_role
FROM account WHERE tier_id = (SELECT tier_id FROM access_level WHERE tier_name='patient');
```
- [ ] recipient records created for each patient
- [ ] One-to-one relationship maintained
- [ ] No missing recipient profiles

### 5.3 Foreign Key Constraints
- [ ] Database enforces FK on recipient.clinic_id
- [ ] Cannot set clinic_id to non-existent clinic
- [ ] Can set clinic_id to NULL (optional)

---

## 6. EDGE CASE TESTING

### 6.1 Clinic Deletion Impact
- [ ] If clinic is deleted, what happens to patient.clinic_id?
- [ ] Verify behavior is acceptable (FK cascade or preserve)

### 6.2 Multiple Registrations
- [ ] Register 10 patients with different clinics
- [ ] Verify all clinic assignments correct
- [ ] Database remains consistent

### 6.3 Special Characters in Names
- [ ] Register patient with special characters: `José`, `O'Brien`
- [ ] Verify names stored correctly
- [ ] Display correctly in recipient list

### 6.4 Very Long Email Addresses
- [ ] Email field accepts strings up to 120 chars
- [ ] Test with maximum length email
- [ ] Should be stored and retrievable

### 6.5 Empty Optional Fields
- [ ] Register patient without First Name
- [ ] Register patient without Last Name
- [ ] Should still create account
- [ ] Display as "None" or blank appropriately

---

## 7. INTEGRATION TESTING

### 7.1 Patient Can Book Appointment
- [ ] Register new patient via signup
- [ ] Login as new patient
- [ ] Navigate to book appointment
- [ ] Verify clinic pre-selected (if applicable)
- [ ] Complete appointment booking

### 7.2 Admin Can View Patient Clinic
- [ ] Admin creates patient with specific clinic
- [ ] Admin views recipient list
- [ ] Patient's clinic displayed correctly

### 7.3 Provider Can See Patient's Clinic
- [ ] Register patient in specific clinic
- [ ] Provider in that clinic can see patient
- [ ] Patient's preferred clinic is visible

---

## 8. PERFORMANCE TESTING

### 8.1 Clinic Dropdown Load Time
- [ ] Load signup page multiple times
- [ ] Clinic dropdown populates quickly
- [ ] No noticeable delay

### 8.2 Form Submission Time
- [ ] Submit patient registration form
- [ ] Account created within 1-2 seconds
- [ ] User feedback (redirect/message) is immediate

### 8.3 Query Performance
- [ ] Check database logs for slow queries
- [ ] Verify clinic fetch query is optimized
- [ ] Patient creation doesn't cause N+1 queries

---

## 9. REGRESSION TESTING

### 9.1 Existing Features Still Work
- [ ] Patient self-registration without clinic still works (if supported)
- [ ] Admin provider creation still works
- [ ] Clinic management unchanged
- [ ] Appointment booking works
- [ ] Patient login/logout works

### 9.2 Other Routes Unaffected
- [ ] `/signin` works
- [ ] `/profile` works
- [ ] `/governance/hub` works
- [ ] `/governance/providers` works
- [ ] Provider routes unchanged

---

## Test Results Summary

| Test Area | Status | Notes |
|-----------|--------|-------|
| Public Signup | [ ] PASS / [ ] FAIL | |
| Admin Signup | [ ] PASS / [ ] FAIL | |
| Database | [ ] PASS / [ ] FAIL | |
| Security | [ ] PASS / [ ] FAIL | |
| UX | [ ] PASS / [ ] FAIL | |
| Integration | [ ] PASS / [ ] FAIL | |
| Performance | [ ] PASS / [ ] FAIL | |
| Regression | [ ] PASS / [ ] FAIL | |

---

## Known Issues / Notes

- [ ] Issue 1: _______________
- [ ] Issue 2: _______________
- [ ] Issue 3: _______________

---

**Testing Date:** _______________
**Tested By:** _______________
**Overall Result:** [ ] PASS [ ] FAIL

---

**For any failures, create a bug report with:**
1. Steps to reproduce
2. Expected result
3. Actual result
4. Environment (Browser, OS, Python version)
5. Database state (attach query results if relevant)
