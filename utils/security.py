from database.models import db, AuditLog

def create_audit_log(user_id, action, resource, resource_id=None, ip_address=None):
    log = AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id,
                   ip_address=ip_address)
    db.session.add(log)
    db.session.commit()