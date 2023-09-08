import re, random, os, json, random
from flask import render_template, request,redirect, flash, make_response, session, url_for
from sqlalchemy.sql import text
from sqlalchemy.orm import joinedload

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps




from newP import app, csrf
from newP.models import db, Pet_owner, Treatment, Vet, Pet, Category, Appointment, Bills
from newP.forms import SignupForm, LoginForm, VetProfileForm, TreatmentForm, BillForm


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
def vet_home():
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
def vet_login():
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
    

@app.route("/view_pet_details/<int:pet_id>")
@login_required
def view_pet_details(pet_id):
    if session.get("vet_loggedin") != None:
        pet = db.session.query(Pet).get(pet_id)
        return render_template("vet/pet_details.html", pets=[pet]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/vet/login")  
    

@app.route("/vet_appointments")
@login_required
def view_vet_appointments():
    if session.get("vet_loggedin") != None:
        vet_id = session.get("vetid")
    
        appointment = db.session.query(Appointment).filter_by(vet_id=vet_id).all()

        return render_template("vet/vet_appointments.html", appointments=appointment) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/vet/dashboard")  


@app.route("/accept_appointment/<int:appointment_id>")
def accept_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.appointment_status = 'Accepted'

    db.session.commit()
    return redirect("/vet_appointments")


@app.route("/reject_appointment/<int:appointment_id>")
def reject_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.appointment_status = 'Rejected'
    
    db.session.commit()
    return redirect("/vet_appointments")


@app.route("/in_progress_appointment/<int:appointment_id>")
def inprogress_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.appointment_status = 'In-progress'

    db.session.commit()
    return redirect("/vet_appointments")


@app.route("/completed_appointment/<int:appointment_id>")
def concluded_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    appointment.appointment_status = 'Completed'

    db.session.commit()
    return redirect("/vet_appointments")


@app.route("/treatment/<int:appointment_id>", methods = ["POST","GET"])
@login_required
def treatment(appointment_id):
    if session.get("vet_loggedin") == None:
        flash("Access Denied")
        return redirect("vet/login")
    
    appointment = db.session.query(Appointment).get(appointment_id)

    if request.method == "GET":

        treatment_form = TreatmentForm()
        
        return render_template("vet/treatment.html",appointment=appointment,treatment_form=treatment_form)
    
    else:
        currentWeight = request.form.get("currentWeight")
        symptoms = request.form.get("symptoms")
        prescription = request.form.get("prescription")
        remark = request.form.get("remark")

        #validatioins / insert

        if Treatment:
            T = Treatment(pet_current_weight=currentWeight,symptoms=symptoms,vet_remark=remark,prescription=prescription,appointment_id=appointment_id)

            db.session.add(T) 

            appointment.appointment_status = 'Treated'

            db.session.commit()

            flash("All inputed Treatment fields have been submitted Doc!")
            return redirect("/vet_appointments")

        else:
             flash("Opps, something went wrong! Please try again..")
             return redirect("/view_pet_details")



@app.route("/billing/<int:appointment_id>", methods=["GET","POST"])
@login_required
def create_bill(appointment_id):

    appointment = db.session.query(Appointment).get(appointment_id)

    # join the appropriate tables so I can access the names of the vet and pet owner that are involed in this session
    pet_owner = (
        db.session.query(Pet_owner).join(Appointment, Pet_owner.user_id == Appointment.user_id).filter(Appointment.appointment_id == appointment_id).first()
    )

    vet = (
        db.session.query(Vet).join(Appointment, Vet.vet_id == Appointment.vet_id).filter(Appointment.appointment_id == appointment_id).first()
    )

    # Create a payment ref number by collecting the first 2 letters from pet owner and vet name
    pet_owner_fullname = pet_owner.user_fullname
    vet_name = vet.vet_fullname

    first_two_letters_pet_owner_fullname = pet_owner_fullname[:2]
    first_two_letters_vet_name = vet_name[:2]

    # Generate three random integers between 1 and 100
    random_figures = [random.randint(1, 100) for _ in range(3)]

    # Convert the list of random generated numbers to a string
    random_figures_str = "".join(map(str, random_figures))

    # Convert the ref number variables to a list
    ref_no_list = [first_two_letters_pet_owner_fullname, first_two_letters_vet_name, random_figures_str]

    # Convert to the list of ref number variables to string
    ref_no_string = '_'.join(ref_no_list)


    if request.method == "GET":
        
        bill_form = BillForm()

        return render_template("vet/create_bill.html",appointment=appointment,bill_form=bill_form,pet_owner=pet_owner, ref_no_string=ref_no_string)
    
    else:
        amount = request.form.get("amount")
        deadline = request.form.get("deadline")
                                

        # validations
        if Bills:
            B = Bills(bills_amount=amount,bills_deadline=deadline,appointment_id=appointment_id,bills_reference_number=ref_no_string)

            db.session.add(B)
            appointment.appointment_status = 'Billed'
            db.session.commit()

            flash("Billing has been created successfully." )
            return redirect("/vet_appointments")
        else:
            flash("Opps Sorry... something went wrong. Please try again")
            return render_template("/billing/<int:appointment_id>")
        


@app.route("/view_treatment/<int:treatment_id>", methods=["POST", "GET"])
@login_required
def view_treatment(treatment_id):
    if session.get("vet_loggedin") != None:
        
        treatment = db.session.query(Treatment).get(treatment_id)
        return render_template("vet/view_treatment.html", treatments=[treatment]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/vet/login")  
    

@app.route("/view_bill/<int:bills_id>", methods=["POST", "GET"])
@login_required
def view_bill(bills_id):
    
    if session.get("vet_loggedin") != None:
        bill = db.session.query(Bills).get(bills_id)

        return render_template("vet/view_bill.html", bills=[bill]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/vet/login") 
   