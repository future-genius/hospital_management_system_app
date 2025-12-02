from app import app
from models import db, AccessLevel, Account, Clinic
from werkzeug.security import generate_password_hash


def setup_database():
    """
    Initializes the database with default roles, admin user,
    and a predefined list of hospital departments.
    """

    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()

        # ---------------------------
        # Create access levels
        # ---------------------------
        default_roles = ["admin", "provider", "patient"]
        for role in default_roles:
            exists = AccessLevel.query.filter_by(tier_name=role).first()
            if not exists:
                new_role = AccessLevel(tier_name=role)
                new_role.persist()

        # ---------------------------
        # Create default admin user
        # ---------------------------
        admin_email = "admin@hospital.com"
        admin_password = "Admin@123"

        admin_exists = Account.query.filter_by(email_address=admin_email).first()
        if not admin_exists:
            admin_role = AccessLevel.query.filter_by(tier_name="admin").first()

            admin_user = Account(
                email_address=admin_email,
                credential_hash=generate_password_hash(admin_password),
                given_name="System",
                surname="Administrator",
                access_tier=admin_role
            )
            admin_user.persist()

        # ---------------------------
        # Add medical departments
        # ---------------------------
        department_names = [
            "General Medicine", "Internal Medicine", "Family Medicine",
            "Emergency Medicine", "Trauma Care", "ICU", "CCU", "NICU", "PICU",
            "General Surgery", "Cardiothoracic Surgery", "Neurosurgery",
            "Orthopedic Surgery", "Plastic & Reconstructive Surgery",
            "Pediatric Surgery", "Vascular Surgery", "Bariatric Surgery",
            "Urology (Surgical)", "ENT Surgery", "Ophthalmic Surgery",
            "Cardiology", "Interventional Cardiology", "Neurology",
            "Neuro-Rehabilitation", "Orthopedics", "Sports Medicine",
            "Joint Replacement", "Physiotherapy & Rehabilitation",
            "Obstetrics", "Gynecology", "Pediatrics", "Neonatology",
            "Radiology & Imaging", "CT Scan", "MRI", "Ultrasound", "X-Ray",
            "Pathology / Laboratory Medicine", "Blood Bank",
            "Oncology", "Medical Oncology", "Radiation Oncology",
            "Surgical Oncology", "ENT", "Audiology", "Speech Therapy",
            "Gastroenterology", "Hepatology", "Gastrointestinal Surgery",
            "Nephrology", "Urology", "Pulmonology", "Respiratory Therapy",
            "Dermatology", "Cosmetology", "Venereology",
            "Psychiatry", "Psychology", "Counseling",
            "Endocrinology", "Diabetes Clinic",
            "Hematology", "Immunology", "Rheumatology",
            "Dentistry", "Oral & Maxillofacial Surgery",
            "Physiotherapy", "Occupational Therapy",
            "Rehabilitation Medicine", "Anesthesiology",
            "Palliative Care", "Pain Management",
            "Infectious Diseases", "Nuclear Medicine"
        ]

        for name in department_names:
            exists = Clinic.query.filter_by(clinic_title=name).first()
            if not exists:
                dept = Clinic(clinic_title=name, clinic_notes="")
                dept.persist()

        print("Database setup completed successfully.")


if __name__ == "__main__":
    setup_database()
