
import pandas as pd
#from flask import Flask, render_template, request, url_for,redirect,session
import pickle
import numpy as np
from flask import *
import flask_login
import os
from num2words import num2words
import mysql.connector

model=pickle.load(open("LinearRegressionModel.pkl",'rb'))
car=pd.read_csv("cleaned car.csv")
app=Flask(__name__)

app.secret_key=os.urandom(24)

conn=mysql.connector.connect(
    host='localhost',
    user='root',
    password='Password123@',
    port='3306',
    database='database'
)

mycursor=conn.cursor()


@app.route('/')
def login():
    if 'user_id' in session:
        return redirect('/home')

    else:
        return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/about')
def about():
    return render_template('about.html')


# @app.route('/prediction')
# def prediction():
#     return render_template('prediction.html')

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


@app.route('/login_validation',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    mycursor.execute('''SELECT * FROM `database`.`uinfo` WHERE `email` LIKE '{}' AND `pwd` LIKE '{}' '''
                     .format(email,password))
    uinfo=mycursor.fetchall()


    if len(uinfo)>0:
        session['user_id']=uinfo[0][0]
        return redirect('/home')
    else:
        flash('Incorrect username/ password')
        return redirect('/')


@app.route('/add_user',methods=['POST'])
def add_user():
    name=request.form.get('uname')
    email=request.form.get('uemail')
    password=request.form.get('upassword')

    mycursor.execute('''INSERT INTO `database`.`uinfo` (`uid`,`name`, `email`, `pwd`) 
    VALUES (NULL , '{}','{}','{}' )'''.format(name, email, password))

    conn.commit()

    return render_template('login.html')




@app.route('/home')
def home():
    companies=sorted(car['company'].unique())
    car_models = sorted(car['name'].unique())
    year = sorted(car['year'].unique(),reverse=True)
    fuel_type = (car['fuel_type'].unique())
    companies.insert(0, "Select Company")
    year.insert(0,"Select Year of Purchase")



    if 'user_id' in session:
        return render_template('home.html',companies=companies,car_models=car_models,years=year,fuel_types=fuel_type)
    else:
        return redirect('/')

@app.route('/predict',methods=['POST'])
def predict():
    company= request.form.get('company')
    car_model=request.form.get('car_model')
    year=request.form.get('year')
    fuel_type=request.form.get('fuel_type')
    kms_driven=request.form.get('kms_driven')

    prediction=model.predict(pd.DataFrame([[car_model, company, year, kms_driven, fuel_type]], columns=['name', 'company', 'year', 'kms_driven', 'fuel_type']))



    return str(np.round(prediction[0], 0))


if __name__=="__main__":
    app.run(debug=True)



