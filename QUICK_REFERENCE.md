# Quick Reference Guide - New Features

## Patient Self-Registration (Public)

### URL
`http://localhost:5000/signup`

### What Users See
1. Email address field
2. First & last name fields
3. **NEW: Department selection dropdown**
4. Password & confirm password fields
5. Create Account button

### Validation
- Department must be selected (client + server-side)
- Email must be unique
- Passwords must match
- Both passwords required

### Database Result
- `account` table: New user entry
- `recipient` table: New patient entry with `clinic_id` set

---

## Admin Patient Registration

### URL
`http://localhost:5000/governance/patients/new`
*(Admin login required)*

### Access Requirements
- Must be logged in as admin user
- Check: `access_level.tier_name == 'admin'`

### Form Fields
1. Email Address (must be unique)
2. First Name (optional)
3. Last Name (optional)
4. Department (required dropdown)
5. Temporary Password (required, min 6 chars)
6. Confirm Password (must match)

### Validation
- Email uniqueness check
- Department existence check
- Password length minimum (6 characters)
- Passwords must match

### Success Flow
1. Account created with hashed temporary password
2. Recipient profile created with clinic_id
3. User redirected to recipients list
4. Success message: "Patient [Name] has been successfully registered."

### Error Handling
- Email already in use → User should login or use different email
- Passwords don't match → Re-enter passwords carefully
- Invalid department → Select valid department from dropdown
- Password too short → Use at least 6 characters

---

## Database Queries

### View All Patients with Their Department
```sql
SELECT 
  a.email_address,
  a.given_name,
  a.surname,
  c.clinic_title as department
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
LEFT JOIN clinic c ON r.clinic_id = c.clinic_id
ORDER BY a.created_on DESC;
```

### Find Patients in Specific Department
```sql
SELECT a.email_address, a.given_name, a.surname
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
WHERE r.clinic_id = 1;
```

### Check Unassigned Patients
```sql
SELECT a.email_address, a.given_name
FROM recipient r
JOIN account a ON r.recipient_id = a.account_id
WHERE r.clinic_id IS NULL;
```

---

## Code Navigation

### To Find Patient Registration Code:
- **Public signup form:** `templates/authentication/signup.html`
- **Public signup logic:** `routes/identity.py` → `signup()` function
- **Admin patient form:** `templates/governance/patient_form.html`
- **Admin patient logic:** `routes/governance.py` → `create_patient()` function
- **Patient model:** `models.py` → `Recipient` class

### Key Functions
- `Clinic.query.all()` - Fetch all departments
- `generate_password_hash()` - Secure password hashing
- `Recipient()` - Create patient profile
- `Account()` - Create user account

---

## Common Tasks

### Add a New Patient (as Admin)
1. Login with admin credentials
2. Go to `/governance/patients/new`
3. Fill in email and name
4. Select department from dropdown
5. Enter temporary password (user should change on first login)
6. Click "Create Patient"
7. Verify in recipients list

### View Patient's Department Assignment
```python
patient_account = Account.query.filter_by(email_address='patient@example.com').first()
if patient_account.recipient_profile:
    department = patient_account.recipient_profile.clinic_link
    print(f"Patient is assigned to: {department.clinic_title}")
```

### Change Patient's Department
```python
# Direct database update
patient = Recipient.query.filter_by(recipient_id=user_id).first()
patient.clinic_id = new_clinic_id
db.session.commit()
```

---

## Form Validation Flow

### Client-Side (JavaScript)
- Department dropdown value check
- Password matching verification
- Minimum length validation

### Server-Side (Flask)
- Email uniqueness check
- Clinic existence verification
- Password hash before storage
- Database constraints enforced

---

## Related Routes

### Authentication Routes
- `GET /signin` - User login
- `GET /signup` - **NEW: Patient registration with clinic**
- `GET /signout` - User logout
- `GET /profile` - View profile

### Admin Routes
- `GET /governance/hub` - Admin dashboard
- `GET /governance/recipients` - List all patients
- `POST /governance/patients/new` - **NEW: Create patient manually**
- `GET /governance/providers` - List doctors

---

## Troubleshooting

### Clinic dropdown is empty
- Check: Are there clinics in the `clinic` table?
- Solution: Admin must create departments first at `/governance/clinics/create`

### Patient registration succeeds but clinic not saved
- Check: Is `clinic_id` present in `recipient` table?
- Check database logs for FK constraint errors
- Verify clinic_id value is valid

### "Administrative access required" error
- Check: Is user logged in?
- Check: Does user have admin role (`access_level.tier_name == 'admin'`)?
- Solution: Login with admin account

### Password hashing errors
- Check: Is `werkzeug` installed? (`pip list | grep werkzeug`)
- Check: Is import correct? `from werkzeug.security import generate_password_hash`

---

## File Locations Quick Ref

```
hospital_app_20251127/
├── models.py (Recipient model updated)
├── routes/
│   ├── identity.py (signup route enhanced)
│   └── governance.py (create_patient route added)
├── templates/
│   ├── authentication/
│   │   └── signup.html (clinic dropdown added)
│   └── governance/
│       └── patient_form.html (NEW - admin registration)
└── IMPLEMENTATION_SUMMARY.md (detailed documentation)
```

---

**Last Updated:** November 28, 2025
**Status:** All features implemented and tested
