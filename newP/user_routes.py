import re,random,os, json, requests

from flask import render_template, request, redirect, flash, make_response, session, url_for
from sqlalchemy.sql import text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


from newP import app, csrf
from newP.models import db, Pet_owner, Vet, Pet, Pet_medical_record, My_bills, Payment, Category
from newP.forms import SignupForm, UserProfileForm, LoginForm, PetProfileForm


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



@app.route("/profile", methods = ["POST","GET"])
@login_required
def user_profile():
    pform = UserProfileForm()
    useronline = session.get("userid")
    userdeets = db.session.query(Pet_owner).get(useronline)
    
    if request.method == "GET": 
        return render_template("pet_owner/profile.html", pform=pform, userdeets=userdeets)
    else:
        
        if pform.validate_on_submit():
            fullname = request.pform.get("fullname")
            gender = request.form.get("gender")
            # user_dob = request.form.get("dob")
            picture = request.files.get("pix")

            filename = pform.pix.data.filename
            
            picture.save("newP/static/images/profile/"+filename)
            userdeets.user_fullname = fullname
            userdeets.user_gender = gender
            userdeets.user_pix = filename
            db.session.commit()

            flash("Profile Updated!")
            return redirect("/dashboard")
        else:
            return render_template("pet_owner/profile.html", pform=pform, userdeets=userdeets)


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
    return redirect("/signup")


@app.route("/medics", methods = ["POST","GET"])
@login_required
def medical_records():
    useronline = session.get("Pet_medical_record_id")
    userdeets = db.session.query(Pet_medical_record).get(useronline)
    return render_template("/pet_owner/medics.html", userdeets=userdeets)



@app.route("/mybills", methods=["POST","GET"])
def billing():
    if session.get("user_loggedin") != None:
        pay = db.session.query(My_bills).all()
        return render_template("pet_owner/mybills.html", pay=pay)
    else:
        flash("Access Denied", category='danger')
        return redirect("/pet_owner/login")


@app.route("/payment")
def make_payment():
    userdeets = db.session.query(Pet_owner).get(session.get("userid")) 
    if session.get("ref") != None:
        ref = session["ref"]
        # get the details of the transaction and display to the user
        tranxdetails = db.session.query(Payment).filter(Payment.pay_refno==ref).first()
        return render_template("pet_owner/payments.html",userdeets=userdeets,tranxdetails=tranxdetails)
    else:
        return redirect("/mybills")


@app.route("/paystack",methods=["POST"])
def paystack():
    if session.get("ref") != None:
        ref = session["ref"]

        tranxdetails = db.session.query(Payment).filter(Payment.pay_refno==ref).first()

        amount = Payment.pay_amt

        # connect to paystack api
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_f98bb4d17a3dda76e2367174394dd525ff3bb221"}
        data = {'amount': amount * 100, "reference":ref}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        rspjson = response.json()

        if rspjson['status'] == True:
            paygateway = rspjson['data']['authorization_url']
            return redirect(paygateway)
        else:
            return rspjson
    else:
        return redirect("/payment")
    
@app.route("/landing")
def paystack_landing():
    ref= session.get("ref")
    if ref == None:
        return redirect("/payment")
    else: # connect to paystack
        headers = {"Content-Type":"application/json","Authorization":"Bearer sk_test_f98bb4d17a3dda76e2367174394dd525ff3bb221"}

        verifyurl = "https://api.paystack.co/transaction/verify/"+str(ref)
        response = requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status'] == True: # payment successful
            return rspjson
        else: 
            return "Payment was not successful. Please try again!"
         

@app.route("/allpets")
def all_pets():
    if session.get("user_loggedin") != None:
        pets = db.session.query(Pet).all()
        return render_template("pet_owner/mypets.html", pets=pets)
    else:
        flash("Access Denied", category='danger')
        return redirect("/pet_owner/login")
    

@app.route("/deletepet/<id>")
def delete__pet(id):
    if session.get("user_loggedin") == None:
        flash("Access Denied", category="danger")
        return redirect("/pet_owner/login")
    else:
        check = db.session.query(Pet).get_or_404(id)
        os.remove("newP/static/collections/" + check.pet_pic)
        db.session.delete(check)
        db.session.commit()
        flash(f"Pet {check.pet_name} has been deleted!", category="success")
        return redirect("/allpets")
    

@app.route("/addpet", methods=["POST","GET"])
def addpet():
    if session.get("user_loggedin") == None:
        flash("Access Denied")
        return redirect("/pet_owner/login")
    
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

        # validate name and file
        if title != "" and cover:
            filename = cover.filename
            allowed = [".jpg", ".png", ".jpeg"]
            name,ext = os.path.splitext(filename)
            newname = str(random.random()* 1000000) + ext
            
            if ext.lower() in allowed:
                cover.save("newP/static/collections/" +newname)
                P = Pet(pet_name=title,pet_descript=descript,pet_pic=newname,pet_gender=gender,pet_color=color,pet_cat_id=petcat,pet_dob=dob,pet_weight_at_reg=weight)

                db.session.add(P)
                db.session.commit()

                flash("Pet has been added", category='success')
                return redirect("/allpets")
            else:
                flash("Please upload only type jpg, png or jpeg", category="danger")
                return redirect("/pet_owner/addpet")
            
        else:
            flash("Please ensure you complete the required fields", category="danger")
            return redirect("/addpet")

