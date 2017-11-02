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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

#persistent class to handle data, rather than using a list, ie Blog[] 
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100))
    blog_entry = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#provide a constructor(a class that can be stored in the database), takes the user created database item (my case blog_entry)
    def __init__(self, blog_title, blog_entry, owner):
        self.blog_title = blog_title
        self.blog_entry = blog_entry
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index','list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


#if we don't add in the methods decorator here, our server will only handle get requests
@app.route('/login', methods = ['POST', 'GET'])
def login():
#on a post request, we want to get data out of the login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('That username is not in our system. Please sign up')
            return redirect('/signup') 
        if user and user.password == password:
            session['username']= username
            flash("Logged in")
            return redirect('/newpost') 
        else:
            flash('Password is incorrect')
                  
    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup():
    username = ''
    password = ''
    verify = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
#    username = request.args.get('username')
#    password = request.args.get('password')
#    verify = request.args.get('verify')

            def left_blank(user_entry):
                if user_entry == '':
                    return True 

            if left_blank(username):
                flash('Must enter username')
            #    return redirect('/signup')

            if left_blank(password):
                flash('Must enter a password')
             #   return redirect('/signup')
                
            if left_blank(verify):
                flash('Must verify passoword')
             #   return redirect('/signup')

            if len(password) < 3:
                flash('Password is too short, must have more than 3 characters')
            #    return redirect('/signup')

            if len(username) < 3:
                flash('Username must have 4 or more characters')
            #    return redirect('/signup')

            if not password == verify:
                flash('Passwords do not match')
                return redirect('/signup')

            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username']= username
                return redirect('/newpost')
        else:
            flash('This username already exists')
            return redirect('/signup')
    return render_template('signup.html', username=username, password=password, verify=verify)


#log user out of session
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

#List all blog users on the "Home" button
@app.route('/')
def index():
    users = User.query.all()
 #   print (users) gives [<User 1> <User 2>] etc
    return render_template('index.html', users=users)    
#with /blog page user sees a list of blogs by all users
# somewhere in /blog, want to show the posts of a single blogger by sending to singleUser.html
#A get request with a user query parameter will be on this page
@app.route('/blog', methods = ['POST', 'GET'])
def list_blogs():
    blog_title = ''
    blog_entry = ''
    
    username = request.args.get('user')# this returns amhum (for an example)
    owner = User.query.filter_by(username = username).first()
    blogs = Blog.query.filter_by(owner=owner).all()
#    author_blog = User.query.filter_by(username=author)
 #   if request.method == 'POST':
 #       blog_title = request.form['blog_title']
 #       blog_entry = request.form['blog_entry']
 #   owner = User.query.filter_by(username = username)
    if username:
        return render_template('singleUser.html', blogs=blogs, username=username, owner=owner)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)
 #       blog_title = blog.blog_title
  #      blog_entry= blog.blog_entry
   #     owner = blog.owner_id
    #    ublogs = Blog.query.filter_by(owner=owner).all()
    #    return render_template('singleUser.html', blog_title=blog_title, blog_entry=blog_entry, owner=owner)
 #   else:
  #      blogs = Blog.query.all()
   #     return render_template('blog.html', blogs=blogs)


#go to separate page that showcases an individual posting, one the user has selected from 
#the main page by clicking the blog title link
@app.route('/show_individual_blog', methods = ['get','post'])
def display_blog():
    blog_title = ''
    blog_entry = ''
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        blog_title = blog.blog_title
        blog_entry = blog.blog_entry
        owner = blog.owner_id
        return render_template('show_individual_blog.html', blog_title = blog_title, blog_entry=blog_entry,blog = blog, owner=owner)
  
@app.route('/newpost', methods = ['POST', 'GET'])
def make_entry():
    blog_title_error=''
    blog_entry_error=''
    owner = User.query.filter_by(username=session['username']).first()

    def left_blank(user_entry):
        if user_entry == '':
            return True 

#the following get request gets the newpost form
    if request.method == 'GET':
#        blog_title = request.args.get('blog_title')
#        blog_entry = request.args.get('blog_entry')
        return render_template('newpost.html')
# the rest of this grabs the submitted information and processes it.    
    if request.method == 'POST': 
        blog_title = request.form['blog_title']
        blog_entry = request.form['blog_entry']

        if left_blank(blog_title):
            blog_title_error = 'Please add a title'
            blog_entry = blog_entry

        if left_blank(blog_entry):
            blog_entry_error = 'Please enter your blog post' 
            blog_title = blog_title
            
        if not blog_title_error and not blog_entry_error:
            blog = Blog(blog_title, blog_entry, owner)
            db.session.add(blog)
            db.session.commit()
            blog_title = blog.blog_title
            blog_entry = blog.blog_entry
#here, I am grabbing the id number from the /newpost form with name = blog-id.  Is this a good idea? It's similar to get it done
#otherwise, it is possible to get it from the db. Well, I did change it to grab from the db(I think)
 #           blog_id = Blog.query.filter_by(blog_title=blog_title).first()     
            return render_template('show_individual_blog.html', blog=blog, blog_title = blog_title, blog_entry=blog_entry)#.format(blog.id))
        else:
            return render_template('newpost.html', blog_title_error = blog_title_error, blog_entry_error=blog_entry_error, blog_title=blog_title, blog_entry=blog_entry)



               
if __name__=='__main__':
    app.run()

