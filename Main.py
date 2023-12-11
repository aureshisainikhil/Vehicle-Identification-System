import random
import re
import datetime
from turtle import pd
import pandas as pd

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect
import pymongo
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = APP_ROOT + "/static/photo"


my_client = pymongo.MongoClient('mongodb://localhost:27017')
my_db = my_client['VehicleIdentificationSystem']

admin_col = my_db['admin']
DMV_col = my_db['DMV']
Police_officer_col = my_db['Police_officer']
Vehicle_col = my_db["Vehicles"]
driver_col = my_db["driver"]
Ticket_col = my_db['Tickets']
Payment_col = my_db['Payments']
Registration_documents_col = my_db['Registration_documents']

app = Flask(__name__)
app.secret_key = "Vehicle_identification"

count = admin_col.count_documents({})
if count == 0:
    admin_col.insert_one({"username": "admin", "password": "admin"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/Admin_login1", methods=['post'])
def Admin_login1():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_col.count_documents(query)
    if username == 'admin' and password == 'admin':
        session['role'] = 'admin'
        return render_template("admin.html")
    else:
        return render_template("msg.html", message="Invalid Login Details")


@app.route("/admin")
def admin():
    return render_template("admin.html",message="Welcome To Admin", color="text-primary")

@app.route("/DMV")
def DMV():
    return render_template("admin.html",input = "dmv", message="Welcome To Admin", color="text-primary")

@app.route("/police_officer")
def police_officer():
    return render_template("admin.html",input = "police_officer", message="Welcome To Admin", color="text-primary")

@app.route("/vehicle")
def vehicle():
    return render_template("DMV_home.html",input = "vehicle", message="Welcome To DMV", color="text-primary")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


@app.route("/DMV_login")
def DMV_login():
    return render_template("DMV_login.html")


@app.route("/DMV_login1", methods=['post'])
def DMV_login1():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = DMV_col.count_documents(query)
    if count > 0:
        DMV = DMV_col.find_one(query)
        session['DMV_id'] = str(DMV['_id'])
        session['role'] = 'DMV'
         # Check if it's the first login for the DMV user
        if DMV['password_changed'] == False:
            return render_template("change_password.html", username=username)
        else:
            return redirect("/DMV_home")
    else:
        return render_template("msg.html", message="Invalid Login", color="text-danger")
    
@app.route("/change_password", methods=['post'])
def change_password():
    # print(session['role'],session['police_officer_id'])    
    newvalues = { "$set": { "password": request.form.get('new_password'),"password_changed":True} }
    if session['role'] == "DMV":
        query = {'_id':ObjectId(session['DMV_id'])}
        DMV_col.update_one(query,newvalues)
        return redirect("/DMV_home")
    elif session['role'] == "police_officer":
        query = {'_id':ObjectId(session['police_officer_id'])}
        Police_officer_col.update_one(query,newvalues)
        return redirect("/police_officer_home")
    else:
        query = {'_id':ObjectId(session['driver_id'])}
        driver_col.update_one(query,newvalues)
        return redirect("/driver_home")
    



@app.route("/DMV_home")
def DMV_home():
    return render_template("DMV_home.html",message="Welcome to DMV", color="text-success")


@app.route("/police_officer_login")
def police_officer_login():
    return render_template("police_officer_login.html")


@app.route("/police_officer_login1", methods=['post'])
def police_officer_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = Police_officer_col.count_documents(query)
    if count > 0:
       police_officer = Police_officer_col.find_one(query)
       session['police_officer_id'] = str(police_officer['_id'])
       session['role'] = 'police_officer'
       if police_officer['password_changed'] == False:
            return render_template("change_password.html", username=police_officer['name'])
       else:
            return redirect("/police_officer_home")
    else:
        return render_template("msg.html", message="Invalid Login", color="text-danger")


@app.route("/police_officer_home")
def police_officer_home():
    return render_template("police_officer_home.html")


@app.route("/add_dmv")
def add_dmv():
    return render_template("add_dmv.html")

@app.route("/Add_dmv1", methods=["POST"])
def Add_dmv1():
    username = request.form.get("username")
    password = request.form.get("password")
    location = request.form.get("address")
    phone = request.form.get("phone")
    email = request.form.get("email")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zipcode")
    
    query = {"$or": [{"username": username}]}
    count = DMV_col.count_documents(query)
    
    if count > 0:
        return render_template("msg.html", message="Duplicate Value Entered", color="text-danger")
    else:
        query2 = {
            "username": username,
            "password": password,
            "location": location,
            "phone": phone,
            "email": email,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "password_changed": False
        }
        DMV_col.insert_one(query2)
        return render_template("msg.html", message="DMV was Added", color="text-success")



@app.route("/view_dmv")
def view_dmv():
    DMV = DMV_col.find()
    Dmvs= list(DMV)
    return render_template("view_dmv.html",Dmvs=Dmvs)

@app.route("/add_police_officer")
def add_police_officer():
    return render_template("add_police_officer.html")

@app.route("/Add_police_officer1", methods=["POST"])
def Add_police_officer1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    gender = request.form.get("gender")
    experience = int(request.form.get("experience"))
    date_of_birth = request.form.get("DOB")
    ssn = request.form.get("ssn")

    query = {"$or": [{"email": email}, {"phone": phone}]}
    count = Police_officer_col.count_documents(query)

    if count > 0:
        return render_template("msg.html", message="Duplicate Value Enter", color="text-danger")
    else:
        query2 = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "address": address,
            "gender": gender,
            "experience": experience,
            "date_of_birth": date_of_birth,
            "ssn": ssn,
            "password_changed": False
        }

        Police_officer_col.insert_one(query2)
        return render_template("msg.html", message="Police officer Added Successfully", color="text-success")


@app.route("/view_police_officer")
def view_police_officer():
    Officer= Police_officer_col.find()
    Police_officers= list(Officer)
    return render_template("view_police_officer.html", Police_officers=Police_officers)


@app.route("/Add_vehicle")
def Add_vehicle():
    return render_template("Add_vehicle.html")


@app.route("/Add_vehicle1", methods=["post"])
def Add_vehicle1():
    vehicle_name = request.form.get("vehicle_name")
    vehicle_model = request.form.get("vehicle_model")
    vehicle_type = request.form.get("vehicle_type")
    vehicle_manufacturing_year = request.form.get("vehicle_manufacturing_year")
    vehicle_capacity = request.form.get("vehicle_capacity")
    vehicle_mileage = request.form.get("vehicle_mileage")
    query = {"vehicle_name": vehicle_name, "vehicle_model": vehicle_model, "vehicle_type": vehicle_type,
             "vehicle_manufacturing_year": vehicle_manufacturing_year, "vehicle_capacity": vehicle_capacity,
             "vehicle_mileage": vehicle_mileage}
    print(query)
    result = Vehicle_col.insert_one(query)
    vehicle_id = result.inserted_id
    vehicle_register_number = request.form.get("vehicle_register_number")
    vehicle_valid_from = request.form.get("vehicle_valid_from")
    vehicle_valid_to = request.form.get("vehicle_valid_to")
    insurance_valid_from = request.form.get("insurance_valid_from")
    insurance_valid_to = request.form.get("insurance_valid_to")
    insurance_number = request.form.get("insurance_number")
    vehicle_title = request.form.get("vehicle_title")
    driver_id = request.form.get("driver_id")
    query = {"_id": ObjectId(driver_id)}
    driver = driver_col.find_one(query)
    driving_licence_number = driver['driving_licence_number']
    query1 = {"$or": [{"vehicle_register_number": vehicle_register_number}, {"vehicle_title": vehicle_title}]}
    count = Registration_documents_col.count_documents(query1)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="text-danger")
    else:
        query2 = {"vehicle_id": ObjectId(vehicle_id), "driver_id": ObjectId(driver_id), "vehicle_register_number": vehicle_register_number,
                  "vehicle_valid_from": vehicle_valid_from, "vehicle_valid_to": vehicle_valid_to, "driving_licence_number": driving_licence_number,
                  "insurance_valid_from": insurance_valid_from, "insurance_valid_to": insurance_valid_to, "status": "valid", "insurance_number": insurance_number, "vehicle_title": vehicle_title}
        print(query2)
        Registration_documents_col.insert_one(query2)
        return render_template("msg.html", message="Vehicles Added Successfully", color="text-success")


@app.route("/view_vehicle")
def view_vehicle():
    keyword = request.args.get("keyword")
    if keyword == None:
        keyword = ""
    keyword2 = re.compile(".*" + keyword + ".*", re.IGNORECASE)
    query = {"$or":[{"vehicle_register_number": keyword2}, {"driving_licence_number": keyword2}]}
    Registration_documents = Registration_documents_col.find(query)
    vehicle_ids = []
    for Registration_document in Registration_documents:
        vehicle_ids.append(Registration_document['vehicle_id'])
    if len(vehicle_ids) == 0:
        query = {"BB":"JJ"}
    else:
        query = {"_id": {"$in": vehicle_ids}}
    print(query)
    vehicles = Vehicle_col.find(query)
    vehicles = list(vehicles)
    print(vehicles)
    return render_template("view_vehicle.html", vehicles=vehicles, keyword=keyword, get_driver_by_vehicle_id=get_driver_by_vehicle_id)


def get_driver_by_vehicle_id(vehicle_id):
    query = {"vehicle_id": vehicle_id}
    # print(query)
    Registration_documents = Registration_documents_col.find_one(query)
    print(Registration_documents)
    query = {"_id": Registration_documents['driver_id']}
    drivers = driver_col.find_one(query)
    print(drivers)
    return drivers, Registration_documents


@app.route("/driver_home")
def driver_home():
    return render_template("driver_home.html")


@app.route("/driver_registration")
def driver_registration():
    return render_template("driver_registration1.html")


@app.route("/driver_registration1", methods=["post"])
def driver_registration1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    gender = request.form.get("gender")
    address = request.form.get("address")
    picture = request.files.get('file')
    path = PROFILE_PATH + "/" + picture.filename
    picture.save(path)
    driving_licence_number = request.form.get("driving_licence_number")

    query = {"$or": [{"driving_licence_number":driving_licence_number},{"email": email}, {"phone": phone}]}
    count = driver_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Value Enter", color="text-danger")
    else:
        query2 = {"name": name, "email": email, "phone": phone, "password": password,
                  "gender": gender, "address": address,"picture": picture.filename, "driving_licence_number": driving_licence_number, "password_changed": True}
        driver_col.insert_one(query2)
        return render_template("msg.html", message="Driver Registered Successfully", color="text-success")

@app.route("/driver_registration2", methods=["post"])
def driver_registration2():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    address = request.form.get("address")
    picture = request.files.get('file')
    path = PROFILE_PATH + "/" + picture.filename
    picture.save(path)
    driving_licence_number = request.form.get("driving_licence_number")
    query = {"$or": [{"driving_licence_number":driving_licence_number},{"email": email}, {"phone": phone}]}
    count = driver_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Value Enter", color="text-danger")
    else:
        query2 = {"name": name, "email": email, "phone": phone, "password": phone,
                  "gender": gender, "address": address,"picture": picture.filename, "driving_licence_number": driving_licence_number, "password_changed": False}
        driver_col.insert_one(query2)
        return render_template("msg.html", message="Driver Registered Successfully",message2 = "Use Phone Number for the First Time Login !!", color="text-success")



@app.route("/view_driver")
def view_driver():
    vehicle_owner = driver_col.find()
    vehicleOwners = list(vehicle_owner)
    return render_template("view_driver.html", vehicleOwners=vehicleOwners)


@app.route("/driver_login")
def driver_login():
    return render_template("driver_login.html")


@app.route("/driver_login1", methods=['post'])
def driver_login1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = driver_col.count_documents(query)
    if count > 0:
       driver = driver_col.find_one(query)
       session['driver_id'] = str(driver['_id'])
       session['role'] = 'driver'
       if driver['password_changed'] == False:
            return render_template("change_password.html", username=driver['name'])
       else:
            return redirect("/driver_home")
       
    else:
        return render_template("msg.html", message="Invalid Login", color="text-danger")


@app.route("/view_driver_vehicle")
def view_driver_vehicle():
    driver_id = session['driver_id']
    query = {"driver_id": ObjectId(driver_id)}
    registration_documents = Registration_documents_col.find_one(query)
    # print(registration_documents)
    registration_documents_ids = []
    if registration_documents is not None:
        registration_documents = Registration_documents_col.find(query)
        for registration_document in registration_documents:
            # print(registration_document)
            registration_documents_ids.append({"_id": registration_document['_id']})
        query = {"$or": registration_documents_ids}
        registration_documents = Registration_documents_col.find(query)
        registration_documents = list(registration_documents)
        print(registration_documents)
        return render_template("view_driver_vehicle.html", registration_documents=registration_documents, get_vehicle_by_vehicle_id=get_vehicle_by_vehicle_id)
    else:
        return render_template("msg.html", message="No Vehicles Found", color="text-danger")

def get_vehicle_by_vehicle_id(vehicle_id):
    query = {"_id": vehicle_id}
    vehicle = Vehicle_col.find_one(query)
    return vehicle


@app.route("/get_customer")
def get_customer():
    keyword = request.args.get("keyword")
    keyword = re.compile(".*" + keyword + ".*", re.IGNORECASE)
    query = {"$or": [{"name": keyword}, {"email": keyword}, {"phone": keyword}]}
    drivers = driver_col.find(query)
    drivers = list(drivers)
    return render_template("get_customer.html", drivers=drivers)


@app.route("/rise_ticket")
def rise_ticket():
    keyword = request.args.get("keyword")
    if keyword == None:
        keyword = ""
    keyword2 = re.compile(".*" + keyword + ".*", re.IGNORECASE)

    query = {"vehicle_register_number": keyword2}
    Registration_documents = Registration_documents_col.find(query)
    vehicle_ids = []
    for Registration_document in Registration_documents:
        vehicle_ids.append(Registration_document['vehicle_id'])
    if len(vehicle_ids) == 0:
        query = {"BB":"JJ"}
    else:
        query = {"_id": {"$in": vehicle_ids}}
    print(query)
    vehicles = Vehicle_col.find(query)
    vehicles = list(vehicles)
    print(vehicles)
    return render_template("rise_ticket.html", vehicles=vehicles, keyword=keyword, get_driver_by_vehicle_id=get_driver_by_vehicle_id)


@app.route("/add_ticket", methods=['post'])
def add_ticket():
    vehicle_id = request.form.get('vehicle_id')
    police_officer_id = session["police_officer_id"]
    query = {"police_officer_id": ObjectId(police_officer_id)}
    police_officer = Police_officer_col.find_one(query)
    return render_template("add_ticket.html", vehicle_id=vehicle_id, police_officer=police_officer)


@app.route("/add_ticket1", methods=['post'])
def add_ticket1():
    vehicle_id = request.form.get('vehicle_id')
    police_officer_id = session["police_officer_id"]
    licence_number = request.form.get('driving_licence_number')
    query = {"driving_licence_number": licence_number}
    driver_document = driver_col.find_one(query)
    if driver_document is not None:
        driver_id = driver_document['_id']
        reason = request.form.get("reason")
        amount = request.form.get("amount")
        date = datetime.datetime.now()
        query = {"vehicle_id": ObjectId(vehicle_id), "driver_id": ObjectId(driver_id), "driving_licence_number": licence_number, "police_officer_id": ObjectId(police_officer_id), "reason": reason, "amount": amount, "status": "Ticket Raised", "date": date}
        print(query)
        Ticket_col.insert_one(query)
        return render_template("msg.html", message="Ticket added Successfully")
    else:
        return render_template("msg.html", message="Driving Licence Number not Found")

@app.route("/view_ticket_risen", methods=['POST'])
def view_ticket_risen():
    vehicle_id = request.form.get('vehicle_id')
    if session['role'] == 'police_officer':
        police_officer_id = session["police_officer_id"]
        # vehicle_id = request.form.get('vehicle_id')

    query = {"_id": ObjectId(police_officer_id)}
    police_officer = Police_officer_col.find_one(query)
    query = {"vehicle_id": ObjectId(vehicle_id)}
    print(query)
    registration_documents = Registration_documents_col.find_one(query)
    query = {"vehicle_id": ObjectId(vehicle_id), "police_officer_id": ObjectId(police_officer_id)}
    print(registration_documents)
    tickets = Ticket_col.find(query)
    print(tickets)
    return render_template("view_ticket_risen1.html", tickets=tickets, police_officer=police_officer, registration_documents=registration_documents)



@app.route("/ticket_payment", methods=['post'])
def ticket_payment():
    ticket_id = request.form.get("ticket_id")
    query = {"_id": ObjectId(ticket_id)}
    ticket = Ticket_col.find_one(query)
    return render_template("ticket_payment.html", ticket=ticket)


@app.route("/ticket_payment_action", methods=['post'])
def ticket_payment_action():
    ticket_id = request.form.get("ticket_id")
    card_number = request.form.get("card_number")
    card_holder_name = request.form.get("card_holder_name")
    cvv = request.form.get("cvv")
    query = {"_id": ObjectId(ticket_id)}
    ticket = Ticket_col.find_one(query)
    reason = ticket['reason']
    payment_for = 'Fine for'+ ' ' + reason
    amount = ticket['amount']
    status = 'Payment Success'
    date = datetime.datetime.now()
    driver_id = ticket['driver_id']
    query = {"driver_id": ObjectId(driver_id)}
    registration_document = Registration_documents_col.find_one(query)
    registration_document_id = registration_document['_id']
    query = {"card_number": card_number, "card_holder": card_holder_name, "cvv": cvv, "payment_for": payment_for, "ticket_id": ticket_id, "driver_id": driver_id, "registration_document_id": registration_document_id, "amount": amount, "status": status, "date": date}
    Payment_col.insert_one(query)
    query = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"status": "PAID"}}
    Ticket_col.update_one(query, query2)
    query = {"_id": ObjectId(ticket_id)}
    query2 = {"$set": {"Paid on": date}}
    Ticket_col.update_one(query, query2)
    return render_template("msg.html", message="Ticket was paid")


@app.route("/view_driver_tickets")
def view_driver_tickets():
    driver_id = session['driver_id']
    query = {"_id": ObjectId(driver_id)}
    driver = driver_col.find_one(query)
    driving_licence_number = driver['driving_licence_number']
    query = {'driving_licence_number': driving_licence_number}
    tickets = Ticket_col.find(query)
    print(tickets)
    tickets = list(tickets)
    return render_template("view_driver_tickets.html", driving_licence_number=driving_licence_number, tickets=tickets, get_driver_by_vehicle_id=get_driver_by_vehicle_id, get_police_officer_by_police_officer_id=get_police_officer_by_police_officer_id)


def get_police_officer_by_police_officer_id(police_officer_id):
    query = {"_id": police_officer_id}
    police_officer = Police_officer_col.find_one(query)
    return police_officer

app.run(debug=True)





