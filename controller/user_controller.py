from flask import render_template, Blueprint, request, redirect
from model.user import User, Role
from flask_login.utils import login_required
from login.decorators import admin_login_required

TEMPLATE = './templates'
STATIC = './static'

user_controller = Blueprint('users', __name__, static_url_path='', template_folder=TEMPLATE, static_folder=STATIC)

@user_controller.route("/userForm")
@login_required
def userForm():
  return render_template("users/user.html", roles=Role.query.all())

@user_controller.route("/users")
@login_required
def users():
  users = User.query.all()
  return render_template("users/users.html", users=users)

@user_controller.route("/users", methods=['POST'])
@login_required
def add_user():
  name = request.form.get('name')
  email = request.form.get('email')
  jobTitle = request.form.get('jobTitle')
  password = request.form.get('password')
  roles = request.form.get('roles')
  
  user = User(email, name, jobTitle, password, [Role.query.filter_by(id=roles[0]).first()])
  user.save()

  return redirect("/users")

@user_controller.route("/roles", methods=['POST'])
@login_required
def add_role():
  name = request.form.get('name')
  description = request.form.get('description')
  
  role = Role(name, description)
  role.save()

  return redirect("/roles")

@user_controller.route("/roles")
@login_required
def roles():
  roles = Role.query.all()
  return render_template("users/roles.html", roles=roles)

@user_controller.route("/roleForm")
@login_required
def roleForm():
  return render_template("users/role.html")