from flask import session, redirect, request, render_template
from database.models import db, Ticket
from utils.security import create_audit_log
from sqlalchemy import or_

def dashboard_routes(app):
    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect("/login")
        user_id = session.get("user_id")
        tickets = Ticket.query.filter_by(owner_id=user_id).all()
        return render_template("dashboard.html", email=session.get("email"), tickets=tickets)

    @app.route("/create-ticket", methods=["GET", "POST"])
    def create_ticket():
        if "user_id" not in session:
            return redirect("/login")

        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            severity = request.form.get("severity")
            ticket = Ticket(title=title, description=description, severity=severity, 
                            owner_id=session.get("user_id"))
            db.session.add(ticket)
            db.session.commit()
            create_audit_log(user_id=session.get("user_id"), action="CREATE_TICKET", resource="ticket",
                             resource_id=str(ticket.id), ip_address=request.remote_addr)
            return redirect("/dashboard")
        return render_template("create_ticket.html")
    
    @app.route("/edit-ticket/<int:ticket_id>", methods=["GET", "POST"])
    def edit_ticket(ticket_id):
        if "user_id" not in session:
            return redirect("/login")
        ticket = Ticket.query.get(ticket_id)

        if not ticket:
            return "Ticket not found"
        
        user_id = session.get("user_id")
        user_role = session.get("role", "USER")
        
        if ticket.owner_id != user_id:
            create_audit_log(user_id=user_id, action="UNAUTHORIZED_EDIT_ATTEMPT", resource="ticket", 
                             resource_id=str(ticket.id), ip_address=request.remote_addr)
            return "Access denied"

        if request.method == "POST":
            ticket.title = request.form.get("title")
            ticket.description = request.form.get("description")
            ticket.severity = request.form.get("severity")
            ticket.status = request.form.get("status")
            db.session.commit()
            create_audit_log(user_id=session.get("user_id"), action="EDIT_TICKET", resource="ticket",
                             resource_id=str(ticket.id), ip_address=request.remote_addr)
            return redirect("/dashboard")

        return render_template("edit_ticket.html", ticket=ticket)
    
    @app.route("/search-tickets", methods=["GET"])
    def search_tickets():
        if "user_id" not in session:
            return redirect("/login")

        query = request.args.get("q", "")
        user_id = session.get("user_id")
        tickets = Ticket.query.filter(Ticket.owner_id == user_id, 
                                      or_(Ticket.title.ilike(f"%{query}%"),
                                          Ticket.description.ilike(f"%{query}%"))).all()
        ticket_ids = ",".join([str(ticket.id) for ticket in tickets])
        create_audit_log(user_id=user_id, action="SEARCH_TICKETS", resource="ticket", 
                         resource_id=ticket_ids, ip_address=request.remote_addr)
        return render_template("dashboard.html", email=session.get("email"), tickets=tickets)