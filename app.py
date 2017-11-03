from flask import Flask, request, redirect, render_template, session, flash
#flask_sqlalchemy pulls in the SQLAlchemy
#Sqlalchemy is a sql toolkit and object relational mapper
#turns python objects into relational objects in a database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogz:blogz@localhost:8889/blogz'
#configure object relational mapping and debugging
app.config['SQLALCHEMY_ECHO']=True
#ties SQLconstuctor whith flask application passed to it, which now create database object to use in main.py
db = SQLAlchemy(app)
app.secret_key= "super secret key"