from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime

from models import (
    db, Account, AccessLevel, Clinic,
    Provider, Recipient, TimeSlot,
    Session, ClinicalNote
)

# --------------------------------------------------------
# App Setup
# --------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --------------------------------------------------------
# Login Manager Configuration
# --------------------------------------------------------
login_mgr = LoginManager()
login_mgr.login_view = 'identity.signin'
login_mgr.init_app(app)


@login_mgr.user_loader
def load_user(user_id):
    """Return account object by user id."""
    try:
        return Account.query.get(int(user_id))
    except:
        return None


# --------------------------------------------------------
# Blueprint Registration
# --------------------------------------------------------
from routes.identity import identity_bp
from routes.governance import governance_bp
from routes.provision import provision_bp
from routes.clientele import clientele_bp

app.register_blueprint(identity_bp)
app.register_blueprint(governance_bp, url_prefix='/governance')
app.register_blueprint(provision_bp, url_prefix='/provision')
app.register_blueprint(clientele_bp, url_prefix='/clientele')


# --------------------------------------------------------
# Routes
# --------------------------------------------------------
@app.route('/')
def home():
    """Redirect users to their respective dashboards."""
    if current_user.is_authenticated:
        role = getattr(current_user.access_tier, 'tier_name', None)

        if role == 'admin':
            return redirect(url_for('governance.hub'))
        elif role == 'provider':
            return redirect(url_for('provision.hub'))
        elif role == 'patient':
            return redirect(url_for('clientele.hub'))

    return render_template('landing.html')


# --------------------------------------------------------
# Initial Setup: Create Roles, Admin, and Departments
# --------------------------------------------------------
def initial_setup():
    """Populate initial roles, admin account, and clinic departments."""
    default_admin_email = 'admin@facilities.local'
    default_admin_pass = 'admin123'

    # --- Create Access Roles ---
    roles = ['admin', 'provider', 'patient']
    for role in roles:
        if not AccessLevel.query.filter_by(tier_name=role).first():
            db.session.add(AccessLevel(tier_name=role))
    db.session.commit()

    # --- Department List ---
    departments = [
        'General Medicine', 'Internal Medicine', 'Family Medicine',
        'Emergency Medicine', 'Trauma Care', 'ICU', 'CCU', 'NICU', 'PICU',
        'General Surgery', 'Cardiothoracic Surgery', 'Neurosurgery',
        'Orthopedic Surgery', 'Plastic & Reconstructive Surgery',
        'Pediatric Surgery', 'Vascular Surgery', 'Bariatric Surgery',
        'Urology (Surgical)', 'ENT Surgery', 'Ophthalmic Surgery',
        'Cardiology', 'Interventional Cardiology', 'Neurology',
        'Neuro-Rehabilitation', 'Orthopedics', 'Sports Medicine',
        'Joint Replacement', 'Physiotherapy & Rehabilitation',
        'Obstetrics', 'Gynecology', 'Pediatrics', 'Neonatology',
        'Radiology & Imaging', 'CT Scan', 'MRI', 'Ultrasound', 'X-Ray',
        'Pathology / Laboratory Medicine', 'Blood Bank',
        'Oncology', 'Medical Oncology', 'Radiation Oncology',
        'Surgical Oncology', 'ENT', 'Audiology', 'Speech Therapy',
        'Gastroenterology', 'Hepatology', 'Gastrointestinal Surgery',
        'Nephrology', 'Urology', 'Pulmonology', 'Respiratory Therapy',
        'Dermatology', 'Cosmetology', 'Venereology',
        'Psychiatry', 'Psychology', 'Counseling',
        'Endocrinology', 'Diabetes Clinic',
        'Hematology', 'Immunology', 'Rheumatology',
        'Dentistry', 'Oral & Maxillofacial Surgery',
        'Physiotherapy', 'Occupational Therapy',
        'Rehabilitation Medicine', 'Anesthesiology',
        'Palliative Care', 'Pain Management',
        'Infectious Diseases', 'Nuclear Medicine'
    ]

    # Add each department if missing
    for name in departments:
        exists = Clinic.query.filter_by(clinic_title=name).first()
        if not exists:
            db.session.add(Clinic(clinic_title=name, clinic_notes=''))
    db.session.commit()

    # --- Create Default Admin ---
    admin_account = Account.query.filter_by(email_address=default_admin_email).first()

    if not admin_account:
        admin_role = AccessLevel.query.filter_by(tier_name='admin').first()
        new_admin = Account(
            email_address=default_admin_email,
            credential_hash=generate_password_hash(default_admin_pass),
            given_name='System',
            surname='Administrator',
            access_tier=admin_role
        )
        db.session.add(new_admin)
        db.session.commit()


# --------------------------------------------------------
# App Runner
# --------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initial_setup()
    app.run(debug=True)
