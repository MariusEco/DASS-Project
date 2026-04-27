from flask import session, redirect

def dashboard_routes(app):
    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect("/login")
        return f"""
        <h1>Welcome, {session.get('email')}</h1>
        <br>
        <a href="/logout">Logout</a>
        """