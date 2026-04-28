import re
from database.models import db, AuditLog

def create_audit_log(user_id, action, resource, resource_id=None, ip_address=None):
    log = AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id,
                   ip_address=ip_address)
    db.session.add(log)
    db.session.commit()

def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!_@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True