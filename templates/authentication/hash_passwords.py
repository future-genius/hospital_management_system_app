from werkzeug.security import generate_password_hash
from models import db, Account

# WARNING: This will overwrite the existing password field!
# Make sure you have a backup of your database first.

def hash_all_passwords():
    accounts = Account.query.all()
    updated = 0

    for user in accounts:
        plain_pwd = user.credential_hash  # assuming current value is plain text
        if not plain_pwd.startswith("pbkdf2:sha256"):  # only hash un-hashed passwords
            user.credential_hash = generate_password_hash(plain_pwd)
            updated += 1

    db.session.commit()
    print(f"Updated {updated} user(s) with hashed passwords.")

if __name__ == "__main__":
    hash_all_passwords()
