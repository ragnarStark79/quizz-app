#!/usr/bin/env python
"""
seedadmin.py – Create or promote an admin user for the QuizOasis application.

Usage:
    python seedadmin.py
    python seedadmin.py --username admin --email admin@example.com --password MySecurePass123
"""

import argparse
import sys
import os

# Make sure we're in the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def seed_admin(username: str, email: str, password: str) -> None:
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()

        if user:
            if user.is_admin:
                print(f"✅  '{user.username}' is already an admin. Nothing to do.")
            else:
                user.is_admin = True
                db.session.commit()
                print(f"✅  Promoted existing user '{user.username}' to admin.")
        else:
            # Also check by username
            user = User.query.filter_by(username=username).first()
            if user:
                user.is_admin = True
                db.session.commit()
                print(f"✅  Promoted existing user '{user.username}' to admin.")
            else:
                new_admin = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    is_admin=True
                )
                db.session.add(new_admin)
                db.session.commit()
                print(f"🎉  Created new admin user '{username}' ({email})")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed an admin user into the QuizOasis database.')
    parser.add_argument('--username', default='admin',        help='Admin username (default: admin)')
    parser.add_argument('--email',    default='admin@quizz.app', help='Admin email')
    parser.add_argument('--password', default='Admin@12345',  help='Admin password')
    args = parser.parse_args()

    print(f"📋 Seeding admin: username={args.username}, email={args.email}")
    seed_admin(args.username, args.email, args.password)
