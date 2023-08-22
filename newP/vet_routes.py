import re,random,os, json
from flask import render_template, request,redirect, flash, make_response, session, url_for
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash


from newP import app, csrf
from newP.models import db, Pet_owner, Vet, Pet, Category
from newP.forms import SignupForm, LoginForm



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

