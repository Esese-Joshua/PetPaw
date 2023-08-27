import re,random,os, json
from flask import render_template, request,redirect, flash, make_response, session, url_for
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps




from newP import app, csrf
from newP.models import db, Pet_owner, Vet, Pet, Category
from newP.forms import SignupForm, LoginForm, VetProfileForm


def login_required(f):
    @wraps(f)
    def login_decorator(*args,**kwargs):
        if session.get("vetid") and session.get("vet_loggedin"):
            return f(*args,**kwargs)
        else:
            flash("Access Denied, Please Login")
            return redirect("/vet/login")
    return login_decorator


@app.route("/vet/dashboard")
def vethome():
        if session.get("vet_loggedin") != None:
            return render_template("vet/vet_dashboard.html")
        else:
            flash("Access Denied", category='danger')
            return redirect("/vet/login")


@app.route("/vet/register", methods=["GET","POST"])
def registers():
    signupform = SignupForm()
    if request.method =="GET":
        return render_template("vet/signup.html", signupform=signupform)
    else:
        if signupform.validate_on_submit():

            vetpass = request.form.get('password')
            v = Vet(vet_fullname=request.form.get('fullname'), 
                     vet_email=request.form.get('email'), 
                     vet_pwd=generate_password_hash(vetpass)
                     )
            
            db.session.add(v)
            db.session.commit()

            session["vet_id"] = v.vet_id
            session["vet_loggedin"] = True

            flash("Account created successfully, you may login" )
            return redirect("/vet/login")
        else:
            flash("Account creation unsuccessful")
            return render_template("vet/signup.html",signupform=signupform)
    
    
@app.route("/vet/login", methods=["GET","POST"])
def vetlogin():
    loginform = LoginForm()
    if request.method =="GET":
        return render_template("vet/login.html", loginform=loginform)
    else:
        email= request.form.get('email')
        pwd=request.form.get('password')
        vet_data = db.session.query(Vet).filter(Vet.vet_email==email).first()

        if vet_data:
            hashedpwd = vet_data.vet_pwd
            check_pwd = check_password_hash(hashedpwd,pwd)

            if check_pwd:
                session["vet_loggedin"] = True
                session["vetid"] = vet_data.vet_id
                return redirect("/vet/dashboard")
            else:
                flash("Incorrect credentials")
                return redirect("/vet/login")
        else:
            flash("Incorrect credentials")
            return redirect("/vet/login")


@app.route("/vet/logout")
def vet_logout():
    if session.get("vet_loggedin"):
        session.pop("vet_loggedin",None)
        flash("You have logged out successfully")
    return redirect("/pet_owner/signup")


@app.route("/edit_vet_profile", methods = ["POST","GET"])
@login_required
def edit_vet_profile():
    vform = VetProfileForm()
    vet_id = session.get("vetid")
    vet_details = db.session.query(Vet).get(vet_id)
    
    if request.method == "POST": 
        try:
            vet_details.vet_address = request.form["address"]
            vet_details.vet_fullname = request.form["fullname"]
            vet_details.vet_email = request.form["email"]
            vet_details.vet_bio = request.form["bio"]
            vet_details.last_updated = datetime.utcnow()

            db.session.commit()
            flash("Profile Updated!")
            return redirect("/vet_profile")
        
        except:
            flash("Opps... Ensure you fill out the form correctly, thank you.")
            return redirect("/edit_vet_profile")
    else:
        return render_template("/vet/edit_vet_profile.html", vform=vform, vet_details=vet_details)
    

@app.route("/vet_profile", methods = ["POST","GET"])
@login_required
def vet_profile():
    if session.get("vet_loggedin") != None:
        vet_id = session["vetid"]
        vet = db.session.query(Vet).get(vet_id)

        return render_template("vet/vet_profile.html", vets=[vet]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/vet/login")
    

