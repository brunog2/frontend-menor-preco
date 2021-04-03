from functools import wraps
from flask import abort
from flask_login import current_user
from flask import redirect

def admin_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not current_user.is_administrator:
            return redirect("/")
            
        return f(*args, **kwargs)
   
    return wrap