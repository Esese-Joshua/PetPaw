from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Vet(db.Model):
    vet_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    vet_fullname = db.Column(db.String(100),nullable=False)
    vet_email = db.Column(db.String(120)) 
    vet_pwd = db.Column(db.String(120),nullable=True)

class Pet_owner(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fullname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120)) 
    user_pwd = db.Column(db.String(120),nullable=True)

    #set relationship
    bills_petowner_relate = db.relationship('My_bills',back_populates='petownerbills_relate')


class My_bills(db.Model):
    bills_id = db.Column(db.Integer, autoincrement=True,primary_key=True) 
    fullname = db.Column(db.String(50),nullable=False)
    amount = db.Column(db.Float,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('pet_owner.user_id'),nullable=False) 
    bills_date = db.Column(db.DateTime(), default=datetime.utcnow)
    bills_status =db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending"))  
   
    #set relationships
    paybills_relate = db.relationship("Payment", back_populates="billsrelate")
    petownerbills_relate = db.relationship('Pet_owner',back_populates='bills_petowner_relate')


class Pet(db.Model):
    pet_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_cat_id = db.Column(db.Integer,db.ForeignKey('category.cat_id'),nullable=False) 
    # user_id = db.Column(db.Integer,db.ForeignKey('pet_owner.user_id'),nullable=False) 
    pet_name = db.Column(db.String(50),nullable=False)
    pet_descript = db.Column(db.Text())
    pet_pic = db.Column(db.String(100))
    pet_gender = db.Column(db.Enum('male','female'),nullable=False, server_default=("female"))
    pet_color = db.Column(db.String(10),nullable=False)
    pet_weight_at_reg = db.Column(db.Float())
    pet_dob = db.Column(db.DateTime(), default=datetime.utcnow)

    #set relationships 
    catrelate = db.relationship("Category", back_populates="petrelate")


class Category(db.Model):
    cat_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    cat_name=db.Column(db.String(20),nullable=True)

    #set relationships
    petrelate = db.relationship("Pet", back_populates="catrelate")


class Payment(db.Model):
    pay_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pay_amt = db.Column(db.Float, nullable=False)  
    bills_id = db.Column(db.Integer,db.ForeignKey('my_bills.bills_id'),nullable=False) 
    pay_refno = db.Column(db.Integer,nullable=False)
    pay_date = db.Column(db.DateTime(), default=datetime.utcnow)
    pay_status =db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending"))  
    
    #set relationship    
    billsrelate = db.relationship('My_bills',back_populates='paybills_relate') 

    
class Pet_medical_record(db.Model):
    Pet_medical_record_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    pet_current_weight = db.Column(db.Integer())
    pet_vaccination_status = db.Column(db.String(10),nullable=False)
    pet_last_visit_date =db.Column(db.DateTime(), default=datetime.utcnow)
    date = db.Column(db.DateTime(), default=datetime.utcnow) 


class Diagnosis_treatment(db.Model):
    diagnosis_treatment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    pet_diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.pet_diagnosis_id'),nullable=False)  
    diagnosis_treatment = db.Column(db.String(200),nullable=False)
    vet_comment =db.Column(db.String(200),nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)


class Diagnosis(db.Model):
    pet_diagnosis_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    disease_name =db.Column(db.String(20),nullable=False)


class Pet_breed(db.Model):
    pet_breed_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    pet_breed_name = db.Column(db.String(50),nullable=False)


class Pet_feeding(db.Model):
    Pet_feeding_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    pet_food_type_id = db.Column(db.Integer, db.ForeignKey('food_type.food_type_id'),nullable=False)  
    pet_feeding_time =db.Column(db.DateTime())
    pet_feeding_quantity = db.Column(db.Float())
    pet_feeding_note = db.Column(db.String(100),nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)


class Food_type(db.Model):
    food_type_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.pet_id'),nullable=False)  
    food_discription = db.Column(db.String(100),nullable=False)
    food_nutritious_value = db.Column(db.String(100),nullable=False)

