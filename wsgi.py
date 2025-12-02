from app import app, db, orchestrate_initial_setup

# This block runs only when the app is imported by a WSGI server
if __name__ != "__main__":
    with app.app_context():
        db.create_all()

        # Run initial setup if possible
        try:
            orchestrate_initial_setup()
        except Exception as e:
            # Ignore setup errors in production environments
            print(f"Setup initialization error: {e}")
            pass

# Expose the Flask app as "application" for WSGI servers
application = app
