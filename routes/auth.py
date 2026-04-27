from flask import render_template, request, redirect, session, url_for
from database.models import db, User

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
            return redirect("/login")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            user = User.query.filter_by(email=email).first()
            if not user:
                return "User does not exist"
            if user.password_hash != password:
                return "Wrong password"
            session["user_id"] = user.id
            session["email"] = user.email
            return redirect("/dashboard")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")