import random
import secrets
from flask import render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import db, User
from utils.security import create_audit_log, is_strong_password
from datetime import datetime, timedelta

def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            if not is_strong_password(password):
                return "Password must contain at least 8 characters, uppercase, lowercase, " \
                        "number and special character"
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return "User already exists"
            new_user = User(email=email, password_hash=generate_password_hash(password), role="USER")
            db.session.add(new_user)
            db.session.commit()
            create_audit_log(user_id=new_user.id, action="REGISTER", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
            return redirect("/login")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if not user:
                create_audit_log(user_id=None, action="LOGIN_FAILED", resource="auth", 
                                 resource_id=None, ip_address=request.remote_addr)
                return "Invalid credentials"
            if user.lock_until and user.lock_until > datetime.now():
                create_audit_log(user_id=user.id, action="LOGIN_BLOCKED", resource="auth",
                                  resource_id=None, ip_address=request.remote_addr)
                return "Account temporarily locked. Try again later."
        
            if not check_password_hash(user.password_hash, password):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.lock_until = datetime.now() + timedelta(minutes=15)
                    user.locked = True
                db.session.commit()
                create_audit_log(user_id=user.id, action="LOGIN_FAILED", resource="auth", 
                                 resource_id=None, ip_address=request.remote_addr)
                return "Invalid credentials"
            
            user.failed_login_attempts = 0
            user.lock_until = None
            user.locked = False
            db.session.commit()

            session.clear()
            session.permanent = True
            session["user_id"] = user.id
            session["email"] = user.email
            session["role"] = user.role
            create_audit_log(user_id=user.id, action="LOGIN", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
            return redirect("/dashboard")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        create_audit_log(user_id=session.get("user_id"), action="LOGOUT", resource="auth", 
                         resource_id=None, ip_address=request.remote_addr)
        session.clear()
        response = redirect("/login")
        response.delete_cookie("session")

        return response
    
    reset_tokens = {}

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if user:
                token = secrets.token_urlsafe(32)
                reset_tokens[token] = { "email": email, "expires_at": datetime.now() + timedelta(minutes=15)}
                create_audit_log(user_id=user.id,action="FORGOT_PASSWORD", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
                return f"Reset link: /reset-password/{token}"
        
            return "If the account exists, a reset link has been generated."
        
        return render_template("forgot_password.html")
    
    @app.route("/reset-password/<token>", methods=["GET", "POST"])
    def reset_password(token):
        token_data = reset_tokens.get(token)
        if not token_data:
            return "Invalid or expired token"
        
        if token_data["expires_at"] < datetime.now():
            del reset_tokens[token]
            return "Invalid or expired token"
        
        email = token_data["email"]
        if request.method == "POST":
            new_password = request.form.get("password")
            if not is_strong_password(new_password):
                return "Password does not meet security requirements"
            user = User.query.filter_by(email=email).first()
            if not user:
                del reset_tokens[token]
                return "Invalid request"
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            del reset_tokens[token]
            create_audit_log(user_id=user.id, action="RESET_PASSWORD", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
            return "Password changed successfully"
        return render_template("reset_password.html")