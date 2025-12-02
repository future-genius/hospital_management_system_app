from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Account, AccessLevel, Provider, Clinic, Session, Recipient
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import datetime

governance_bp = Blueprint('governance', __name__)


def administrator_only(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.access_tier.tier_name != 'admin':
            flash('Administrative access required.', 'error')
            return redirect(url_for('home'))
        return fn(*args, **kwargs)
    return decorated


@governance_bp.route('/hub')
@login_required
@administrator_only
def hub():
    # Count providers, recipients, sessions and clinics directly from their models
    total_providers = Provider.query.count()
    total_recipients = Recipient.query.count()
    total_sessions = Session.query.count()
    total_clinics = Clinic.query.count()

    latest_sessions = Session.query.order_by(Session.booked_timestamp.desc()).limit(5).all()

    return render_template(
        'governance/dashboard.html',
        provider_count=total_providers,
        recipient_count=total_recipients,
        session_count=total_sessions,
        clinic_count=total_clinics,
        recent_sessions=latest_sessions
    )


@governance_bp.route('/providers')
@login_required
@administrator_only
def list_providers():
    providers = Provider.query.all()
    return render_template('governance/providers_list.html', providers=providers)


@governance_bp.route('/providers/create', methods=['GET', 'POST'])
@login_required
@administrator_only
def create_provider():
    clinics = Clinic.query.all()

    if request.method == 'POST':
        email_addr = request.form.get('email_address')
        password_input = request.form.get('credential')
        given_n = request.form.get('given_name')
        last_n = request.form.get('surname')
        clinic_id_input = request.form.get('clinic_id')
        expertise_field = request.form.get('expertise')

        # Basic validation
        if not email_addr or not password_input:
            flash('Email and password are required.', 'error')
            return redirect(url_for('governance.create_provider'))

        existing = Account.query.filter_by(email_address=email_addr).first()
        if existing:
            flash('Email already in use.', 'error')
            return redirect(url_for('governance.create_provider'))

        provider_tier = AccessLevel.query.filter_by(tier_name='provider').first()

        # Use the local helper already imported at the top
        acct = Account(
            email_address=email_addr,
            credential_hash=generate_password_hash(password_input),
            given_name=given_n,
            surname=last_n,
            access_tier=provider_tier
        )

        db.session.add(acct)
        db.session.flush()

        # Convert clinic id to integer when provided
        try:
            clinic_id_val = int(clinic_id_input) if clinic_id_input else None
        except (TypeError, ValueError):
            clinic_id_val = None

        provider_record = Provider(
            provider_id=acct.account_id,
            clinic_id=clinic_id_val,
            expertise=expertise_field
        )
        db.session.add(provider_record)
        db.session.flush()

        # Generate unique doctor ID based on department
        provider_record.generate_doctor_id()
        db.session.commit()

        flash(f'Provider {given_n} {last_n} registered with ID: {provider_record.doctor_unique_id}.', 'success')
        return redirect(url_for('governance.list_providers'))

    return render_template('governance/provider_form.html', clinics=clinics)


@governance_bp.route('/providers/<int:provider_id>/edit', methods=['GET', 'POST'])
@login_required
@administrator_only
def edit_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    clinics = Clinic.query.all()

    if request.method == 'POST':
        given_n = request.form.get('given_name')
        last_n = request.form.get('surname')
        email_addr = request.form.get('email_address')
        expertise_field = request.form.get('expertise')
        clinic_id_input = request.form.get('clinic_id')

        # Validate new email is not already taken by another account
        if email_addr != provider.account_link.email_address:
            existing = Account.query.filter_by(email_address=email_addr).first()
            if existing:
                flash('Email already in use.', 'error')
                return redirect(url_for('governance.edit_provider', provider_id=provider_id))

        # Update Account details
        provider.account_link.given_name = given_n
        provider.account_link.surname = last_n
        provider.account_link.email_address = email_addr

        # Update Provider details
        try:
            clinic_id_val = int(clinic_id_input) if clinic_id_input else None
        except (TypeError, ValueError):
            clinic_id_val = None

        provider.clinic_id = clinic_id_val
        provider.expertise = expertise_field

        db.session.commit()

        flash(f'Doctor {given_n} {last_n} updated successfully.', 'success')
        return redirect(url_for('governance.list_providers'))

    return render_template('governance/provider_edit.html', provider=provider, clinics=clinics)


@governance_bp.route('/providers/<int:provider_id>/delete', methods=['POST'])
@login_required
@administrator_only
def delete_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    account = provider.account_link
    doctor_name = account.full_name

    try:
        # Delete related sessions first (to maintain referential integrity)
        Session.query.filter_by(provider_id=provider_id).delete()

        # Delete provider record
        Provider.query.filter_by(provider_id=provider_id).delete()

        # Delete account record
        Account.query.filter_by(account_id=account.account_id).delete()

        db.session.commit()
        flash(f'Doctor {doctor_name} and all associated data have been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting doctor: {str(e)}', 'error')

    return redirect(url_for('governance.list_providers'))


@governance_bp.route('/recipients')
@login_required
@administrator_only
def list_recipients():
    recipients = Recipient.query.all()
    return render_template('governance/recipients_list.html', recipients=recipients)


@governance_bp.route('/patients/new', methods=['GET', 'POST'])
@login_required
@administrator_only
def create_patient():
    clinics = Clinic.query.all()

    if request.method == 'POST':
        email_addr = request.form.get('email_address')
        password_input = request.form.get('credential')
        password_confirm = request.form.get('credential_confirm')
        first_name = request.form.get('given_name')
        last_name = request.form.get('surname')
        clinic_id_input = request.form.get('clinic_id')

        # Validate email not already used
        existing_account = Account.query.filter_by(email_address=email_addr).first()
        if existing_account:
            flash('Email address is already registered.', 'error')
            return redirect(url_for('governance.create_patient'))

        # Validate passwords match
        if password_input != password_confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('governance.create_patient'))

        # Convert and validate clinic id
        try:
            clinic_id_val = int(clinic_id_input) if clinic_id_input else None
        except (TypeError, ValueError):
            flash('Selected department is invalid.', 'error')
            return redirect(url_for('governance.create_patient'))

        clinic_check = Clinic.query.filter_by(clinic_id=clinic_id_val).first()
        if not clinic_check:
            flash('Selected department is invalid.', 'error')
            return redirect(url_for('governance.create_patient'))

        # Get patient access level
        patient_tier = AccessLevel.query.filter_by(tier_name='patient').first()

        # Create new account
        new_account = Account(
            email_address=email_addr,
            credential_hash=generate_password_hash(password_input),
            given_name=first_name,
            surname=last_name,
            access_tier=patient_tier
        )

        db.session.add(new_account)
        db.session.flush()

        # Create patient profile with clinic assignment
        new_patient = Recipient(
            recipient_id=new_account.account_id,
            clinic_id=clinic_id_val
        )

        db.session.add(new_patient)
        db.session.flush()

        # Patient ID will be generated when booking an appointment (after appointment date is known)
        db.session.commit()

        flash(f'Patient {first_name} {last_name} has been successfully registered.', 'success')
        return redirect(url_for('governance.list_recipients'))

    return render_template('governance/patient_form.html', clinics=clinics)


@governance_bp.route('/clinics')
@login_required
@administrator_only
def list_clinics():
    clinics = Clinic.query.all()
    return render_template('governance/clinics_list.html', clinics=clinics)


@governance_bp.route('/clinics/create', methods=['GET', 'POST'])
@login_required
@administrator_only
def create_clinic():
    if request.method == 'POST':
        clinic_name = request.form.get('clinic_title')
        clinic_desc = request.form.get('clinic_notes')

        existing = Clinic.query.filter_by(clinic_title=clinic_name).first()
        if existing:
            flash('Clinic name already exists.', 'error')
            return redirect(url_for('governance.create_clinic'))

        new_clinic = Clinic(
            clinic_title=clinic_name,
            clinic_notes=clinic_desc
        )
        db.session.add(new_clinic)
        db.session.commit()

        flash(f'Clinic {clinic_name} created.', 'success')
        return redirect(url_for('governance.list_clinics'))

    return render_template('governance/clinic_form.html')


@governance_bp.route('/sessions')
@login_required
@administrator_only
def list_sessions():
    sessions = Session.query.order_by(Session.booked_timestamp.desc()).all()
    return render_template('governance/sessions_list.html', sessions=sessions)


@governance_bp.route('/sessions/create', methods=['GET', 'POST'])
@login_required
@administrator_only
def create_session():
    providers = Provider.query.all()
    recipients = Recipient.query.all()
    
    if request.method == 'POST':
        provider_id_raw = request.form.get('provider_id')
        recipient_id_raw = request.form.get('recipient_id')
        appointment_time = request.form.get('appointment_time')
        
        # Validate inputs
        if not provider_id_raw or not recipient_id_raw or not appointment_time:
            flash('All fields are required.', 'error')
            return redirect(url_for('governance.create_session'))

        # Parse IDs
        try:
            provider_id = int(provider_id_raw)
            recipient_id = int(recipient_id_raw)
        except (TypeError, ValueError):
            flash('Invalid provider or recipient selection.', 'error')
            return redirect(url_for('governance.create_session'))
        
        # Validate provider and recipient exist
        provider_check = Provider.query.filter_by(provider_id=provider_id).first()
        recipient_check = Recipient.query.filter_by(recipient_id=recipient_id).first()
        
        if not provider_check or not recipient_check:
            flash('Invalid provider or recipient selected.', 'error')
            return redirect(url_for('governance.create_session'))
        
        try:
            from datetime import datetime
            booked_time = datetime.fromisoformat(appointment_time)
            
            new_session = Session(
                provider_id=provider_id,
                recipient_id=recipient_id,
                booked_timestamp=booked_time,
                session_state='scheduled'
            )
            
            # Fetch the recipient to generate patient ID based on appointment date and department
            patient = Recipient.query.get(recipient_id)
            if patient and not patient.patient_unique_id:
                # Generate unique patient ID based on appointment date and clinic
                patient.generate_patient_id(booked_time.date())
            
            # Generate unique appointment code if available on the model
            if hasattr(new_session, 'generate_appointment_code') and callable(new_session.generate_appointment_code):
                new_session.generate_appointment_code()
            
            db.session.add(new_session)
            db.session.commit()
            
            flash('Appointment created successfully.', 'success')
            return redirect(url_for('governance.list_sessions'))
        except ValueError:
            flash('Invalid date/time format.', 'error')
            return redirect(url_for('governance.create_session'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating appointment: {str(e)}', 'error')
            return redirect(url_for('governance.create_session'))
    
    return render_template('governance/session_form.html', providers=providers, recipients=recipients)


@governance_bp.route('/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
@administrator_only
def delete_session(session_id):
    session_obj = Session.query.get_or_404(session_id)
    
    try:
        db.session.delete(session_obj)
        db.session.commit()
        flash('Appointment deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting appointment: {str(e)}', 'error')
    
    return redirect(url_for('governance.list_sessions'))
