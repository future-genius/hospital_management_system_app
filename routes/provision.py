from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Provider, TimeSlot, Session, ClinicalNote
from functools import wraps
from datetime import datetime

provision_bp = Blueprint('provision', __name__)


def provider_only(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.access_tier.tier_name != 'provider':
            flash('Provider access required.', 'error')
            return redirect(url_for('home'))
        return fn(*args, **kwargs)
    return decorated


@provision_bp.route('/hub')
@login_required
@provider_only
def hub():
    provider_profile = Provider.query.filter_by(provider_id=current_user.account_id).first()
    if not provider_profile:
        flash('Provider profile missing.', 'error')
        return redirect(url_for('home'))

    scheduled_sessions = Session.query.filter_by(provider_id=current_user.account_id).all()
    available_slots = TimeSlot.query.filter_by(
        provider_id=current_user.account_id,
        slot_available=True
    ).count()

    return render_template(
        'provision/dashboard.html',
        provider=provider_profile,
        sessions=scheduled_sessions,
        available_slot_count=available_slots
    )


@provision_bp.route('/availability')
@login_required
@provider_only
def manage_availability():
    slots = TimeSlot.query.filter_by(provider_id=current_user.account_id).all()
    return render_template('provision/availability.html', time_slots=slots)


@provision_bp.route('/availability/add', methods=['GET', 'POST'])
@login_required
@provider_only
def add_availability():
    if request.method == 'POST':
        start_datetime_str = request.form.get('starts_at')
        duration_str = request.form.get('duration_mins')

        try:
            start_dt = datetime.fromisoformat(start_datetime_str)
            duration = int(duration_str)
        except (ValueError, TypeError):
            flash('Invalid date/time or duration.', 'error')
            return redirect(url_for('provision.add_availability'))

        new_slot = TimeSlot(
            provider_id=current_user.account_id,
            starts_at=start_dt,
            duration_mins=duration,
            slot_available=True
        )
        db.session.add(new_slot)
        db.session.commit()

        flash('Availability slot added.', 'success')
        return redirect(url_for('provision.manage_availability'))

    return render_template('provision/add_slot_form.html')


@provision_bp.route('/sessions')
@login_required
@provider_only
def view_sessions():
    sessions = Session.query.filter_by(provider_id=current_user.account_id).order_by(
        Session.booked_timestamp.desc()
    ).all()
    return render_template('provision/sessions.html', sessions=sessions)


@provision_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
@login_required
@provider_only
def mark_completed(session_id):
    sess = Session.query.get_or_404(session_id)
    if sess.provider_id != current_user.account_id:
        flash('Access denied.', 'error')
        return redirect(url_for('provision.view_sessions'))

    sess.session_state = 'completed'
    db.session.commit()

    flash('Session marked as completed.', 'success')
    return redirect(url_for('provision.view_sessions'))


@provision_bp.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
@provider_only
def mark_cancelled(session_id):
    sess = Session.query.get_or_404(session_id)
    if sess.provider_id != current_user.account_id:
        flash('Access denied.', 'error')
        return redirect(url_for('provision.view_sessions'))

    sess.session_state = 'cancelled'
    db.session.commit()

    flash('Session marked as cancelled.', 'success')
    return redirect(url_for('provision.view_sessions'))


@provision_bp.route('/sessions/<int:session_id>/clinical', methods=['GET', 'POST'])
@login_required
@provider_only
def add_clinical_record(session_id):
    sess = Session.query.get_or_404(session_id)
    if sess.provider_id != current_user.account_id:
        flash('Access denied.', 'error')
        return redirect(url_for('provision.view_sessions'))

    if request.method == 'POST':
        findings_text = request.form.get('findings')
        treatment_txt = request.form.get('treatment_plan')

        note = ClinicalNote(
            session_id=session_id,
            recipient_id=sess.recipient_id,
            provider_id=current_user.account_id,
            findings=findings_text,
            treatment_plan=treatment_txt
        )
        db.session.add(note)
        db.session.commit()

        flash('Clinical note recorded.', 'success')
        return redirect(url_for('provision.view_sessions'))

    return render_template('provision/clinical_form.html', session=sess)


@provision_bp.route('/recipients/<int:recipient_id>/history')
@login_required
@provider_only
def view_recipient_history(recipient_id):
    from models import Recipient, ClinicalNote
    recipient = Recipient.query.get_or_404(recipient_id)
    history_records = ClinicalNote.query.filter_by(
        recipient_id=recipient_id
    ).order_by(ClinicalNote.noted_on.desc()).all()

    return render_template(
        'provision/recipient_history.html',
        recipient=recipient,
        records=history_records
    )
