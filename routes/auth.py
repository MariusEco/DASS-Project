import random
from flask import render_template, request, redirect, session, url_for
from database.models import db, User
from utils.security import create_audit_log

def register_routes(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return "User already exists"
            new_user = User(email=email, password_hash=password,role="USER")
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
                return "User does not exist"
            if user.password_hash != password:
                create_audit_log(user_id=user.id, action="LOGIN_FAILED", resource="auth", 
                                 resource_id=None, ip_address=request.remote_addr)
                return "Wrong password"
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
        return redirect("/login")
    
    reset_tokens = {}

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = request.form.get("email")
            user = User.query.filter_by(email=email).first()
            if not user:
                create_audit_log(user_id=None, action="FORGOT_PASSWORD_FAILED", resource="auth", 
                                 resource_id=None, ip_address=request.remote_addr)
                return "User does not exist"
            token = str(random.randint(1000, 9999))
            reset_tokens[email] = token
            create_audit_log(user_id=user.id,action="FORGOT_PASSWORD", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
            return f"Reset link: /reset-password/{token}"
        return render_template("forgot_password.html")
    
    @app.route("/reset-password/<token>", methods=["GET", "POST"])
    def reset_password(token):
        email = None
        for k, v in reset_tokens.items():
            if v == token:
                email = k
                break
        if not email:
            return "Invalid token"
        if request.method == "POST":
            new_password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            user.password_hash = new_password
            db.session.commit()
            create_audit_log(user_id=user.id, action="RESET_PASSWORD", resource="auth", 
                             resource_id=None, ip_address=request.remote_addr)
            return "Password changed successfully"
        return render_template("reset_password.html")