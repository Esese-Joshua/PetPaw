from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Vet(db.Model):
    vet_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    vet_fullname = db.Column(db.String(100),nullable=False)
    vet_email = db.Column(db.String(120)) 
    vet_gender = db.Column(db.Enum('Male','female'),nullable=False, server_default=("Female"))
    vet_pwd = db.Column(db.String(120),nullable=True)
    vet_address = db.Column(db.String(120),nullable=True)
    vet_bio = db.Column(db.String(120),nullable=True)

    #set relationship
    appointment_vet_relate = db.relationship('Appointment', back_populates='vet_appointment_relate')


class Appointment(db.Model):
    appointment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('pet_owner.user_id'),nullable=False)
    pet_id = db.Column(db.Integer,db.ForeignKey('pet.pet_id'),nullable=False)
    vet_id = db.Column(db.Integer,db.ForeignKey('vet.vet_id'),nullable=False)
    appointment_date = db.Column(db.Date())
    pet_current_weight = db.Column(db.Float())
    appointment_comments = db.Column(db.String(200), nullable=True)
    appointment_status = db.Column(db.Enum('Accepted','Rejected','Treated', 'Pending','In-progress','Completed','Billed'),nullable=False, server_default=("Pending"))

    #set relationship
    vet_appointment_relate = db.relationship('Vet', back_populates='appointment_vet_relate')

    pet_owner_appointment_relate = db.relationship('Pet_owner', back_populates='appointment_pet_owner_relate')

    pet_appointment_relate = db.relationship('Pet', back_populates='appointment_pet_relate')

    treatment_appointment_relate = db.relationship('Treatment', back_populates='appointment_treatment_relate')

    bills_appointment_relate = db.relationship('Bills',back_populates='appointment_bills_relate')


class Treatment(db.Model):
    treatment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    appointment_id = db.Column(db.Integer,db.ForeignKey('appointment.appointment_id'),nullable=False)
    symptoms = db.Column(db.String(200),nullable=False)   
    prescription = db.Column(db.String(200),nullable=False)
    vet_remark =db.Column(db.String(200),nullable=False)
    pet_current_weight = db.Column(db.Float())

   # set relationship    
    appointment_treatment_relate = db.relationship('Appointment', back_populates='treatment_appointment_relate')

    # pet_treatment_relate = db.relationship('Pet', back_populates='treatment_pet_relate')


class Pet_owner(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fullname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120)) 
    user_pwd = db.Column(db.String(120),nullable=True)
    user_address = db.Column(db.String(120),nullable=True)
    user_bio = db.Column(db.String(120),nullable=True)
    date_time_created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)

    #set relationship
    appointment_pet_owner_relate = db.relationship('Appointment', back_populates='pet_owner_appointment_relate')


class Bills(db.Model):
    bills_id = db.Column(db.Integer, autoincrement=True,primary_key=True) 
    bills_amount = db.Column(db.Float,nullable=False)
    appointment_id = db.Column(db.Integer,db.ForeignKey('appointment.appointment_id'),nullable=False) 
    bills_deadline = db.Column(db.Date())
    bills_status = db.Column(db.Enum('Pending','Paid'),nullable=False, server_default=("Pending"))  
    bills_reference_number = db.Column(db.String(100), nullable=False)

    #set relationships
    paybills_relate = db.relationship("Payment", back_populates="billsrelate")

    appointment_bills_relate = db.relationship('Appointment',back_populates='bills_appointment_relate')


class Payment(db.Model):
    pay_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    bills_id = db.Column(db.Integer,db.ForeignKey('bills.bills_id'),nullable=False) 
    paystack_ref_no = db.Column(db.String(50),nullable=False)
    pay_date = db.Column(db.DateTime(), default=datetime.utcnow)
    
    #set relationship    
    billsrelate = db.relationship('Bills',back_populates='paybills_relate') 


class Pet(db.Model):
    pet_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_cat_id = db.Column(db.Integer,db.ForeignKey('category.cat_id'),nullable=False) 
    user_id = db.Column(db.Integer,db.ForeignKey('pet_owner.user_id'),nullable=True) 
    pet_name = db.Column(db.String(50),nullable=False)
    pet_breed = db.Column(db.String(50),nullable=True)
    pet_descript = db.Column(db.Text())
    pet_pic = db.Column(db.String(100))
    pet_gender = db.Column(db.Enum('Male','female'),nullable=False, server_default=("Female"))
    pet_color = db.Column(db.String(10),nullable=False)
    pet_status = db.Column(db.Enum('Active','Inactive'),nullable=False, server_default=("Active"))
    date_time_created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow)
    pet_weight_at_reg = db.Column(db.Float())
    pet_dob = db.Column(db.Date())
    pet_likes = db.Column(db.String(200),nullable=True)
    pet_dislikes = db.Column(db.String(200),nullable=True)
    pet_comments =  db.Column(db.String(200),nullable=True)


    #set relationships 
    catrelate = db.relationship("Category", back_populates="petrelate")

    appointment_pet_relate = db.relationship('Appointment', back_populates='pet_appointment_relate')


class Category(db.Model):
    cat_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    cat_name=db.Column(db.String(20),nullable=True)

    #set relationships
    petrelate = db.relationship("Pet", back_populates="catrelate")
