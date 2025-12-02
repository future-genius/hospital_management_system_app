from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from models import db, Account, AccessLevel, Recipient, Provider, Clinic

# Blueprint for login, signup, and profile-related actions
identity_bp = Blueprint("identity", __name__)


# ---------------------------------------------------------
# Sign In
# ---------------------------------------------------------
@identity_bp.route("/signin", methods=["GET", "POST"])
def signin():
    """Authenticate the user and redirect based on their role."""

    # If user is already logged in, redirect based on role
    if current_user.is_authenticated:
        role_map = {
            "admin": "governance",
            "provider": "provision",
            "patient": "clientele"
        }
        blueprint = role_map.get(current_user.access_tier.tier_name)
        return redirect(url_for(f"{blueprint}.hub")) if blueprint else redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email_address")
        password = request.form.get("credential")

        user = Account.query.filter_by(email_address=email).first()

        if user and check_password_hash(user.credential_hash, password):
            login_user(user)
            flash("Logged in successfully.", "success")

            role_map = {
                "admin": "governance",
                "provider": "provision",
                "patient": "clientele"
            }
            blueprint = role_map.get(user.access_tier.tier_name)
            return redirect(url_for(f"{blueprint}.hub")) if blueprint else redirect(url_for("home"))
        else:
            flash("Incorrect email or password.", "error")

    return render_template("authentication/signin.html")


# ---------------------------------------------------------
# Sign Up
# ---------------------------------------------------------
@identity_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a new patient account with clinic selection."""

    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email_address")
        pwd1 = request.form.get("credential")
        pwd2 = request.form.get("credential_confirm")
        fname = request.form.get("given_name")
        lname = request.form.get("surname")
        clinic_id = request.form.get("clinic_id")

        # Basic validation
        if not email or not pwd1:
            flash("Email and password cannot be empty.", "error")
            return redirect(url_for("identity.signup"))

        if pwd1 != pwd2:
            flash("Passwords do not match.", "error")
            return redirect(url_for("identity.signup"))

        if not clinic_id:
            flash("Please select a department.", "error")
            return redirect(url_for("identity.signup"))

        if Account.query.filter_by(email_address=email).first():
            flash("This email is already in use.", "error")
            return redirect(url_for("identity.signup"))

        # Verify clinic exists
        clinic = Clinic.query.filter_by(clinic_id=clinic_id).first()
        if not clinic:
            flash("Selected department is invalid.", "error")
            return redirect(url_for("identity.signup"))

        # Create patient account
        patient_role = AccessLevel.query.filter_by(tier_name="patient").first()
        new_user = Account(
            email_address=email,
            credential_hash=generate_password_hash(pwd1),
            given_name=fname,
            surname=lname,
            access_tier=patient_role
        )
        db.session.add(new_user)
        db.session.flush()  # Get the ID before commit

        # Link patient record with clinic selection
        patient_profile = Recipient(
            recipient_id=new_user.account_id,
            clinic_id=clinic_id
        )
        db.session.add(patient_profile)
        db.session.commit()

        flash("Your account has been created. Please log in.", "success")
        return redirect(url_for("identity.signin"))

    # GET request: fetch all clinics to display in dropdown
    clinics = Clinic.query.all()
    return render_template("authentication/signup.html", clinics=clinics)


# ---------------------------------------------------------
# Sign Out
# ---------------------------------------------------------
@identity_bp.route("/signout")
@login_required
def signout():
    """Logout the user and redirect to homepage."""
    logout_user()
    flash("You have logged out.", "success")
    return redirect(url_for("home"))  # Fixed from 'welcome' to 'home'


# ---------------------------------------------------------
# View Profile
# ---------------------------------------------------------
@identity_bp.route("/profile")
@login_required
def profile_view():
    """Render profile page."""
    return render_template("authentication/profile_view.html", account=current_user)


# ---------------------------------------------------------
# Update Profile Information
# ---------------------------------------------------------
@identity_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    """Update user's name."""
    current_user.given_name = request.form.get("given_name")
    current_user.surname = request.form.get("surname")
    db.session.commit()

    flash("Profile updated successfully.", "success")
    return redirect(url_for("identity.profile_view"))


# ---------------------------------------------------------
# Change Password
# ---------------------------------------------------------
@identity_bp.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    """Update user's password."""
    old_pwd = request.form.get("old_credential")
    new_pwd = request.form.get("new_credential")
    confirm_pwd = request.form.get("confirm_credential")

    # Check old password
    if not check_password_hash(current_user.credential_hash, old_pwd):
        flash("Your current password is incorrect.", "error")
        return redirect(url_for("identity.profile_view"))

    if new_pwd != confirm_pwd:
        flash("New passwords do not match.", "error")
        return redirect(url_for("identity.profile_view"))

    current_user.credential_hash = generate_password_hash(new_pwd)
    db.session.commit()

    flash("Password changed successfully.", "success")
    return redirect(url_for("identity.profile_view"))
