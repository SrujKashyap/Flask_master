from registration_module.app import create_app
from registration_module.app.extensions import db
import os

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
