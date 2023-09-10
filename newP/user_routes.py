import re,random,os, json, requests, sys

from flask import render_template, request, redirect, flash, make_response, session, url_for
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


from newP import app, csrf
from newP.models import db, Pet_owner, Vet, Pet, Bills, Category, Appointment, Treatment, Payment
from newP.forms import SignupForm, UserProfileForm, LoginForm, EditPetProfileForm, AppointmentForm, BillForm


def login_required(f):
    @wraps(f)
    def login_decorator(*args,**kwargs):
        if session.get("userid") and session.get("user_loggedin"):
            return f(*args,**kwargs)
        else:
            flash("Access Denied, Please Login")
            return redirect("/login")
    return login_decorator


@app.route("/")
@app.route("/home")
def home():
    return render_template("pet_owner/index.html")


@app.route("/dashboard/", methods = ["POST","GET"])
@login_required
def dashboard():
    loginform = LoginForm()
    if session.get("user_loggedin") != None:
        useronline = session.get("user_id")
        userdeets = db.session.query(Pet_owner).get(useronline)
        return render_template("pet_owner/dashboard.html", userdeets=userdeets)
    else:
        return render_template("pet_owner/login.html",loginform=loginform)


@app.route("/about")
def about():
    return render_template("pet_owner/about.html")


@app.route("/fullstory")
def fullstory():
    return render_template("pet_owner/fullstory.html")


@app.route("/contactus")
def contact():
    return render_template("pet_owner/contactus.html")


@app.route("/the_whole_story", methods=["GET","POST"])
def story():
    return render_template("pet_owner/fullstory.html")


@app.route("/edit_profile", methods = ["POST","GET"])
@login_required
def edit_profile():
    pform = UserProfileForm()
    user_id = session.get("userid")
    userdeets = db.session.query(Pet_owner).get(user_id)
    
    if request.method == "POST": 
        try:
            userdeets.user_address = request.form["address"]
            userdeets.user_fullname = request.form["fullname"]
            userdeets.user_email = request.form["email"]
            userdeets.user_bio = request.form["bio"]
            userdeets.last_updated = datetime.utcnow()

            db.session.commit()
            flash("Profile Updated!")
            return redirect("/profile")
        
        except:
            flash("Opps!")
            return redirect("/edit_profile")
    else:
        return render_template("pet_owner/edit_profile.html", pform=pform, userdeets=userdeets)
    

@app.route("/profile", methods = ["POST","GET"])
def profile():
    if session.get("user_loggedin") != None:
        user_id = session["userid"]
        user = db.session.query(Pet_owner).get(user_id)
        return render_template("pet_owner/profile.html", users=[user]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/login")  


@app.route("/signup",methods=["POST","GET"])
def signup():
    signupform = SignupForm()
    if request.method=="GET":
        return render_template("pet_owner/signup.html", signupform=signupform)
    else:
        if signupform.validate_on_submit():

            userpass = request.form.get('password')
            p = Pet_owner(user_fullname=request.form.get('fullname'), 
                     user_email=request.form.get('email'), 
                     user_pwd=generate_password_hash(userpass)
                     )
            
            db.session.add(p)
            db.session.commit()

            session["userid"] = p.user_id
            session["user_loggedin"] = True

            flash("Account created successfully, you may login" )
            return redirect("login")
        else:
            flash("Account creation unsuccessful")
            return render_template("pet_owner/signup.html",signupform=signupform)
    


@app.route("/login", methods=['POST','GET'])
def login():
    loginform = LoginForm()
    if request.method=="GET":
        return render_template("pet_owner/login.html", loginform=loginform)
    else:
        username = request.form.get("email")  
        password = request.form.get("password")
        deets = db.session.query(Pet_owner).filter(Pet_owner.user_email == username).first()

        if deets:
              hashedpwd=deets.user_pwd
              chk = check_password_hash(hashedpwd,password)

              if chk:
                    session['user_loggedin']=True
                    session['userid'] = deets.user_id
                    return redirect("/dashboard")
              
              else:
                    flash("Invalid credentials")
                    return redirect("/login")    
        else:
             flash("Invalid credentials")
             return redirect("/login")


@app.route("/signout")
def signout():
    if session.get("userid") or session.get("user_loggedin"):
        session.pop("userid", None)
        session.pop("user_loggedin", None)
        flash("Signed Out Successfully")
    return redirect("/login")


@app.route("/medics", methods = ["POST","GET"])
@login_required
def medical_records():

    if session.get("user_loggedin") != None:
        
        treatment = db.session.query(Treatment).all()
        return render_template("pet_owner/medics.html", treatments=treatment) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/dashboard/")  


@app.route("/mypets")
def view_pets():
    if session.get("user_loggedin") != None:

        pets = db.session.query(Pet).filter_by(user_id=session['userid']).all()
    
        return render_template("pet_owner/mypets.html", pets=pets)
    else:
        flash("Access Denied", category='danger')
        return redirect("/login")
    

@app.route("/deletepet/<id>")
def delete__pet(id):
    if session.get("user_loggedin") == None:
        flash("Access Denied", category="danger")
        return redirect("/login")
    else:
        check = db.session.query(Pet).get_or_404(id)
        os.remove("newP/static/collections/" + check.pet_pic)
        db.session.delete(check)
        db.session.commit()
        flash(f"Pet {check.pet_name} has been deleted!", category="success")
        return redirect("/mypets")
    

@app.route("/addpet", methods=["POST","GET"])
def addpet():
    if session.get("user_loggedin") == None:
        flash("Access Denied")
        return redirect("/login")
    
    if request.method=="GET":
        cat = db.session.query(Category).all()
        return render_template("pet_owner/addpet.html", cat=cat)
    else:
        # Retrieve all the form data
        petcat = request.form.get("petcat")
        title = request.form.get("title")
        gender = request.form.get("gender")
        color = request.form.get("color")
        weight = request.form.get("weight")
        dob = request.form.get("dob")
        cover = request.files.get("cover")
        descript = request.form.get("descript")
        breed = request.form.get("breed")
        likes = request.form.get("likes")
        dislikes = request.form.get("dislikes")
        comments = request.form.get("comments")

        # validate name and file
        if title != "" and cover:
            filename = cover.filename
            allowed = [".jpg", ".png", ".jpeg"]
            name,ext = os.path.splitext(filename)
            newname = str(random.random()* 1000000) + ext
            
            if ext.lower() in allowed:
                cover.save("newP/static/collections/" +newname)
                P = Pet(pet_name=title,pet_descript=descript,pet_pic=newname,pet_gender=gender,pet_color=color,pet_cat_id=petcat,pet_dob=dob,pet_weight_at_reg=weight,user_id=session['userid'],pet_breed=breed,pet_likes=likes,pet_dislikes=dislikes,pet_comments=comments)

                db.session.add(P)
                db.session.commit()

                flash("Pet has been added", category='success')
                return redirect("/mypets")
            else:
                flash("Please upload only type jpg, png or jpeg", category="danger")
                return redirect("/pet_owner/addpet")
            
        else:
            flash("Please ensure you complete the required fields", category="danger")
            return redirect("/addpet")


@app.route("/pet_details/<int:pet_id>")
def pet_details(pet_id):
    if session.get("user_loggedin") != None:
        pet = db.session.query(Pet).get(pet_id)
        return render_template("pet_owner/pet_details.html", pets=[pet]) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/login")  
    

@app.route("/edit_pet/<int:pet_id>", methods = ["POST","GET"])
@login_required
def edit_pet_profile(pet_id):
    pet_form = EditPetProfileForm()
    petdetails = db.session.query(Pet).get(pet_id)

    if request.method == "POST": 
        try:
            petdetails.pet_name = request.form["pet_name"]
            petdetails.pet_breed = request.form["breed"]
            petdetails.pet_descript = request.form["descript"]
            petdetails.pet_likes = request.form["likes"]
            petdetails.pet_dislikes = request.form["dislikes"]
            
            db.session.commit()
            flash("Pet Profile Updated!")
            #return redirect("/pet_details/" +pet_id)
            return redirect("/mypets")

        except:
            flash("Opps, something went wrong! Please try again..")
            #return redirect("/pet_details/" +pet_id)
            return redirect("/mypets")
        
    else:
        return render_template("pet_owner/petedit.html", pet_form=pet_form, petdetails=petdetails)


@app.route("/disable_pet/<int:pet_id>", methods = ["POST","GET"])
@login_required
def disable_pet(pet_id):
    petdetails = db.session.query(Pet).get(pet_id)

    if request.method == "POST": 

        petdetails.pet_comments = request.form["comment"]
        petdetails.pet_status = "Inactive"      
        
        try:
            db.session.commit()
            flash("Pet Profile Updated!")
            return redirect("/mypets")

        except:
            flash("Opps, something went wrong! Please try again..")
            return redirect("/mypets")
        
    else:
        return render_template("None") 
    


@app.route("/book_appointment/<int:pet_id>", methods = ["POST","GET"])
def book_appointment(pet_id):
    if session.get("user_loggedin") == None:
        flash("Access Denied")
        return redirect("/login")

    if request.method == "GET":

        vets = db.session.query(Vet).all()
        pets = db.session.query(Pet).get(pet_id)

        appointment_form = AppointmentForm()
        
        return render_template("pet_owner/book_appointment.html",appointment_form=appointment_form,pets=pets,vets=vets)
    
    else:
        user_id = session.get("userid")

        comments = request.form.get("comments")
        date = request.form.get("date")
        vet = request.form.get("vets")
        current_weight = request.form.get("current_weight")

        # validatioins / insert
        if Appointment:
            A = Appointment(appointment_comments=comments,appointment_date=date,vet_id=vet,user_id=user_id,pet_id=pet_id,pet_current_weight=current_weight)

            db.session.add(A)         
            db.session.commit()

            flash("Appointment has been booked. Please check your email for follow-up!")

            return redirect("/pet_appointments")

        else:
            flash("Opps, something went wrong! Please try again..")
            return redirect("/mypets")
            

@app.route("/pet_appointments")
def view_pet_appointments():
    if session.get("user_loggedin") != None:
        user_id = session.get("userid")

        appointment = db.session.query(Appointment).filter_by(user_id=user_id).all()

        return render_template("pet_owner/appointments.html", appointments=appointment) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/mypets")  


@app.route("/edit_appointment/<int:appointment_id>", methods = ["POST","GET"])
@login_required
def edit_appointment(appointment_id):
    appointment_form = AppointmentForm()
    appointment_details = db.session.query(Appointment).get(appointment_id)

    if request.method == "POST": 
        try:
            appointment_details.appointment_comments = request.form["comments"]
            appointment_details.appointment_date = request.form["date"]
                       
            db.session.commit()
            flash("Appointment has been Updated!")
            return redirect("/pet_appointments")

        except:
            flash("Opps, something went wrong! Please try again..")
            return redirect("/pet_appointments")
        
    else:
        return render_template("pet_owner/edit_appointment.html", appointment_form=appointment_form, appointment_details=appointment_details)
    

@app.route("/delete_appointment/<id>")
def delete_appointment(id):
        check = db.session.query(Appointment).get_or_404(id)
        db.session.delete(check)
        db.session.commit()
        # flash(f"Appointment for {pet.pet_name} has been deleted!", category="success")
        flash("You just deleted a scheduled Appointment for a pet!", category="success")
        return redirect("/mypets")


@app.route("/bills/<int:bills_id>", methods=["POST","GET"])
@login_required
def billing(bills_id):

    if session.get("user_loggedin") != None:
        if request.method == "GET":
            bill_form = BillForm()
            bill = db.session.query(Bills).get(bills_id)

            return render_template("pet_owner/pay_bills.html", bill=bill,bill_form=bill_form)
        else:
            flash("Access Denied", category='danger')
            return redirect("/login")
    else:
        flash("Access Denied", category='danger')
        return redirect("/pet_appointments")
    


@app.route("/bills_history", methods = ["POST", "GET"])
@login_required
def view_bills_history():
    
    if session.get("user_loggedin") != None:
    
        bill = db.session.query(Bills).all()
        return render_template("pet_owner/bills_history.html", bills=bill) 
    else:
        flash("Access Denied", category='danger')
        return redirect("/dashboard/")  



@app.route("/paystack/<string:bills_reference_number>",methods=["POST"])
@login_required
def paystack(bills_reference_number):

    bill = db.session.query(Bills).filter(Bills.bills_reference_number == bills_reference_number).first()

    if bill:

        amount = bill.bills_amount
        email = bill.appointment_bills_relate.pet_owner_appointment_relate.user_email
        
        # connect to paystack api
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_f98bb4d17a3dda76e2367174394dd525ff3bb221"}

        data = {
            'amount':amount * 100, 
            "email":email, 
            'ref':bills_reference_number,
            "callback_url":"http://127.0.0.1:1957/landing"
            }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        json_response = response.json()

        if json_response['status'] == True:
            paygateway = json_response['data']['authorization_url']

            session["bills_id"] = bill.bills_id

            return redirect(paygateway)

        else:
            return json_response
    else:
        flash("Bill not found", category='danger')
        return redirect("/pet_appointments")
  
    

@app.route("/landing") 
def paystack_landing():

    bills_id = session.get("bills_id")

    reference = request.args.get("reference")

    # Join the appropriate tables to UPDATE APPOINTMENT STATUS AND BILLING STATUS

    appointment = (
        db.session.query(Appointment)
        .join(Bills, Appointment.appointment_id == Bills.appointment_id)
        .filter(Bills.bills_id == bills_id)
        .first()
    )

    bill = db.session.query(Bills).get(bills_id)

    # connect to paystack
    headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_f98bb4d17a3dda76e2367174394dd525ff3bb221"}

    verifyurl = "https://api.paystack.co/transaction/verify/"+str(reference)

    response = requests.get(verifyurl, headers=headers)
    json_response = json.loads(response.text)

    if json_response['status'] == True: # payment successful

        P = Payment(bills_id=bills_id, paystack_ref_no=reference)

        appointment.appointment_status = 'Paid'

        bill.bills_status = "Paid"

        db.session.add(P)
        db.session.commit()

        flash("Payment was succesful")
        return redirect("/bills_history")
        
    else:
        flash("Payment Failed")
        return redirect("/bills_history")




@app.route("/view_payment_details/<int:bills_id>") 
def view_payment_details(bills_id):

    payment = db.session.query(Payment).filter(Payment.bills_id == bills_id).first()

    # connect to paystack
    headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_f98bb4d17a3dda76e2367174394dd525ff3bb221"}

    verifyurl = "https://api.paystack.co/transaction/verify/"+str(payment.paystack_ref_no)

    response = requests.get(verifyurl, headers=headers)

    json_response = json.loads(response.text)

    return render_template("pet_owner/payment_details.html",json_response=json_response)
    
