from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

# Initialize the SQLAlchemy database object
db = SQLAlchemy()


# -------------------------------------------------------------
# Access Level Model
# -------------------------------------------------------------
class AccessLevel(db.Model):
    __tablename__ = "access_level"

    tier_id = db.Column(db.Integer, primary_key=True)
    tier_name = db.Column(db.String(40), unique=True, nullable=False)
    tier_description = db.Column(db.String(255))

    def persist(self):
        """Save the current object to the database."""
        db.session.add(self)
        db.session.commit()


# -------------------------------------------------------------
# Account / User Model
# -------------------------------------------------------------
class Account(db.Model, UserMixin):
    __tablename__ = "account"

    account_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    credential_hash = db.Column(db.String(255))
    given_name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    tier_id = db.Column(db.Integer, db.ForeignKey("access_level.tier_id"))

    is_enabled = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    access_tier = db.relationship("AccessLevel")

    def get_id(self):
        """Flask-Login uses this to fetch user ID."""
        return str(self.account_id)

    @property
    def full_name(self):
        """Combine first and last name neatly."""
        return f"{self.given_name or ''} {self.surname or ''}".strip()

    def persist(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def create_new(email_address, credential, given_name="", surname=""):
        """Helper function to create new patient accounts."""
        patient_tier = AccessLevel.query.filter_by(tier_name="patient").first()

        new_account = Account(
            email_address=email_address,
            credential_hash=generate_password_hash(credential),
            given_name=given_name,
            surname=surname,
            access_tier=patient_tier
        )
        db.session.add(new_account)
        db.session.commit()
        return new_account


# -------------------------------------------------------------
# Clinic / Department Model
# -------------------------------------------------------------
class Clinic(db.Model):
    __tablename__ = "clinic"

    clinic_id = db.Column(db.Integer, primary_key=True)
    clinic_title = db.Column(db.String(120), unique=True, nullable=False)
    clinic_notes = db.Column(db.Text)

    def persist(self):
        db.session.add(self)
        db.session.commit()


# -------------------------------------------------------------
# Provider Model (Doctors)
# -------------------------------------------------------------
class Provider(db.Model):
    __tablename__ = "provider"

    provider_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinic.clinic_id"))
    expertise = db.Column(db.String(120))
    biography = db.Column(db.Text)
    doctor_unique_id = db.Column(db.String(32), unique=True, nullable=True)

    account_link = db.relationship(
        "Account",
        backref=db.backref("provider_profile", uselist=False)
    )
    clinic_link = db.relationship("Clinic")

    @property
    def display_name(self):
        return self.account_link.full_name

    def generate_doctor_id(self):
        """
        Generate a unique doctor ID based on department.
        Format: DEPT-NNN where DEPT is clinic initials and NNN is sequence number.
        Example: CARD-001 for Cardiology, first doctor in that department.
        """
        if not self.clinic_id:
            return None
        
        clinic = self.clinic_link
        if not clinic:
            return None
        
        # Extract department initials (first 3-4 chars, uppercase)
        dept_code = ''.join(word[0].upper() for word in clinic.clinic_title.split() if word)
        dept_code = dept_code[:4]  # Limit to 4 chars
        
        # Count doctors in this clinic before this one
        count_in_clinic = Provider.query.filter_by(clinic_id=self.clinic_id).count()
        sequence = str(count_in_clinic + 1).zfill(3)
        
        unique_id = f"{dept_code}-{sequence}"
        self.doctor_unique_id = unique_id
        return unique_id


# -------------------------------------------------------------
# Recipient Model (Patients)
# -------------------------------------------------------------
class Recipient(db.Model):
    __tablename__ = "recipient"

    recipient_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinic.clinic_id"), nullable=True)
    patient_unique_id = db.Column(db.String(32), unique=True, nullable=True)
    appointment_date = db.Column(db.Date, nullable=True)

    account_link = db.relationship(
        "Account",
        backref=db.backref("recipient_profile", uselist=False)
    )
    clinic_link = db.relationship("Clinic")

    def generate_patient_id(self, appointment_date=None):
        """
        Generate a unique patient ID based on appointment date and department.
        Format: DEPT-DDMMYY-NNN where DEPT is clinic code, DDMMYY is appointment date,
        and NNN is sequence number for that clinic on that date.
        Example: CARD-290125-001 for Cardiology, Jan 29, 2025, first patient.
        """
        if not self.clinic_id or not appointment_date:
            return None
        
        clinic = self.clinic_link
        if not clinic:
            return None
        
        # Extract department initials (first 3-4 chars, uppercase)
        dept_code = ''.join(word[0].upper() for word in clinic.clinic_title.split() if word)
        dept_code = dept_code[:4]
        
        # Format date as DDMMYY
        date_str = appointment_date.strftime("%d%m%y")
        
        # Count patients for this clinic on this date
        from datetime import date as date_type
        if isinstance(appointment_date, date_type):
            count_on_date = Recipient.query.filter(
                Recipient.clinic_id == self.clinic_id,
                Recipient.appointment_date == appointment_date
            ).count()
        else:
            count_on_date = 0
        
        sequence = str(count_on_date + 1).zfill(3)
        
        unique_id = f"{dept_code}-{date_str}-{sequence}"
        self.patient_unique_id = unique_id
        self.appointment_date = appointment_date
        return unique_id


# -------------------------------------------------------------
# Appointment Time Slot Model
# -------------------------------------------------------------
class TimeSlot(db.Model):
    __tablename__ = "time_slot"

    slot_id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    starts_at = db.Column(db.DateTime, nullable=False)
    duration_mins = db.Column(db.Integer, default=60)
    slot_available = db.Column(db.Boolean, default=True)

    provider_link = db.relationship(
        "Provider",
        backref=db.backref("time_slots", lazy="dynamic")
    )

    def persist(self):
        db.session.add(self)
        db.session.commit()


# -------------------------------------------------------------
# Session / Appointment Model
# -------------------------------------------------------------
class Session(db.Model):
    __tablename__ = "session"

    session_id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipient.recipient_id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))
    unique_appointment_code = db.Column(db.String(32), unique=True, nullable=True, default=None)

    booked_timestamp = db.Column(db.DateTime, nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("time_slot.slot_id"), nullable=True)

    session_state = db.Column(db.String(32), default="scheduled")

    recipient_link = db.relationship("Recipient")
    provider_link = db.relationship("Provider")

    def generate_appointment_code(self):
        """Generate unique appointment code based on department, date, and patient."""
        # Get clinic from recipient
        clinic = self.recipient_link.clinic_link
        clinic_code = str(clinic.clinic_id).zfill(2) if clinic else "00"
        
        # Get date in format DDMM
        appointment_date = self.booked_timestamp.strftime("%d%m")
        
        # Get patient ID with padding
        patient_code = str(self.recipient_id).zfill(5)
        
        # Get appointment time in format HHMM
        time_code = self.booked_timestamp.strftime("%H%M")
        
        # Combine into unique code: CLINIC-DDMM-PATIENT-HHMM
        unique_code = f"APT{clinic_code}{appointment_date}{patient_code}{time_code}"
        self.unique_appointment_code = unique_code
        return unique_code

    def persist(self):
        db.session.add(self)
        db.session.commit()


# -------------------------------------------------------------
# Clinical Note Model
# -------------------------------------------------------------
class ClinicalNote(db.Model):
    __tablename__ = "clinical_note"

    note_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("session.session_id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipient.recipient_id"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider.provider_id"))

    findings = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    noted_on = db.Column(db.DateTime, default=datetime.utcnow)

    def persist(self):
        db.session.add(self)
        db.session.commit()
