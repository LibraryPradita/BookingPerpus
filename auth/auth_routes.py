from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import get_db, Admin

admin_auth = Blueprint("admin_auth", __name__)

@admin_auth.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        with get_db() as db:
            admin = db.query(Admin).filter_by(email=email).first()
            
            if admin and check_password_hash(admin.password, password):
                session["admin_logged_in"] = True
                session["admin_email"] = admin.email
                flash("Login berhasil!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Email atau password salah!", "danger")
                
    return render_template("admin_login.html")

@admin_auth.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_email", None)
    flash("Logout berhasil!", "success")
    return redirect(url_for("admin_login"))
