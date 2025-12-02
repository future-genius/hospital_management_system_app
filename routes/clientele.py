from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Recipient, Provider, TimeSlot, Session, Clinic, ClinicalNote
from functools import wraps
from datetime import datetime

clientele_bp = Blueprint('clientele', __name__)


# Allow only users with the "patient" role to access certain pages
def recipient_only(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.access_tier.tier_name != 'patient':
            flash('Patient access required.', 'error')
            return redirect(url_for('home'))
        return view_func(*args, **kwargs)
    return wrapper


@clientele_bp.route('/hub')
@login_required
@recipient_only
def hub():
    # Load recipient profile for the logged-in user
    recipient = Recipient.query.filter_by(recipient_id=current_user.account_id).first()
    if not recipient:
        flash('Recipient profile missing.', 'error')
        return redirect(url_for('home'))

    # Upcoming and past sessions
    upcoming_sessions = Session.query.filter_by(
        recipient_id=current_user.account_id,
        session_state='scheduled'
    ).all()

    past_sessions = Session.query.filter_by(
        recipient_id=current_user.account_id
    ).filter(
        Session.session_state.in_(['completed', 'cancelled'])
    ).all()

    return render_template(
        'clientele/dashboard.html',
        recipient=recipient,
        upcoming=upcoming_sessions,
        history=past_sessions
    )


@clientele_bp.route('/clinics')
@login_required
@recipient_only
def browse_clinics():
    clinics = Clinic.query.all()
    return render_template('clientele/browse_clinics.html', clinics=clinics)


@clientele_bp.route('/clinics/<int:clinic_id>/providers')
@login_required
@recipient_only
def search_providers(clinic_id):
    clinic = Clinic.query.get_or_404(clinic_id)
    providers = Provider.query.filter_by(clinic_id=clinic_id).all()
    return render_template(
        'clientele/search_providers.html',
        clinic=clinic,
        providers=providers
    )


@clientele_bp.route('/providers/<int:provider_id>')
@login_required
@recipient_only
def view_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    slots = TimeSlot.query.filter_by(provider_id=provider_id, slot_available=True).all()
    return render_template(
        'clientele/provider_detail.html',
        provider=provider,
        slots=slots
    )


@clientele_bp.route('/book', methods=['GET', 'POST'])
@login_required
@recipient_only
def book_session():
    if request.method == 'POST':
        slot_id = request.form.get('slot_id')
        provider_id = request.form.get('provider_id')

        slot = TimeSlot.query.get_or_404(slot_id)

        # Prevent booking unavailable slots
        if not slot.slot_available:
            flash('Selected slot is no longer available.', 'error')
            return redirect(url_for('clientele.book_session'))

        # Avoid double booking
        if Session.query.filter_by(slot_id=slot_id).first():
            flash('Slot already booked.', 'error')
            return redirect(url_for('clientele.book_session'))

        new_session = Session(
            recipient_id=current_user.account_id,
            provider_id=provider_id,
            booked_timestamp=datetime.utcnow(),
            slot_id=slot_id,
            session_state='scheduled'
        )

        db.session.add(new_session)
        slot.slot_available = False
        db.session.commit()

        flash('Session booked successfully.', 'success')
        return redirect(url_for('clientele.hub'))

    return render_template('clientele/book_form.html')


@clientele_bp.route('/sessions')
@login_required
@recipient_only
def view_sessions():
    sessions = Session.query.filter_by(
        recipient_id=current_user.account_id
    ).order_by(
        Session.booked_timestamp.desc()
    ).all()

    return render_template('clientele/sessions.html', sessions=sessions)


@clientele_bp.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
@recipient_only
def cancel_session(session_id):
    session_obj = Session.query.get_or_404(session_id)

    # Ensure user owns the session
    if session_obj.recipient_id != current_user.account_id:
        flash('Access denied.', 'error')
        return redirect(url_for('clientele.view_sessions'))

    # Only scheduled sessions can be cancelled
    if session_obj.session_state != 'scheduled':
        flash('Only scheduled sessions can be cancelled.', 'error')
        return redirect(url_for('clientele.view_sessions'))

    session_obj.session_state = 'cancelled'

    # Free the time slot for future bookings
    if session_obj.slot_id:
        slot = TimeSlot.query.get(session_obj.slot_id)
        if slot:
            slot.slot_available = True

    db.session.commit()

    flash('Session cancelled.', 'success')
    return redirect(url_for('clientele.view_sessions'))


@clientele_bp.route('/treatment-history')
@login_required
@recipient_only
def treatment_history():
    records = ClinicalNote.query.filter_by(
        recipient_id=current_user.account_id
    ).order_by(
        ClinicalNote.noted_on.desc()
    ).all()

    return render_template('clientele/treatment_history.html', records=records)
