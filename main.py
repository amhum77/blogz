from flask import Flask, request, redirect, render_template
#flask_sqlalchemy pulls in the SQLAlchemy
#Sqlalchemy is a sql toolkit and object relational mapper
#turns python objects into relational objects in a database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
#configure object relational mapping and debugging
app.config['SQLALCHEMY_ECHO']=True
#ties SQLconstuctor whith flask application passed to it, which now create database object to use in main.py
db = SQLAlchemy(app)


#persistent class to handle data, rather than using a list, ie Blog[] 
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100))
    blog_entry = db.Column(db.String(500))

#provide a constructor(a class that can be stored in the database), takes the user created database item (my case blog_entry)
    def __init__(self, blog_title, blog_entry):
        self.blog_title = blog_title
        self.blog_entry = blog_entry


@app.route('/blog', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_entry = request.form['blog_entry']

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        blog_title = blog.blog_title
        blog_entry = blog.blog_entry
        return render_template('show_individual_blog.html', blog_title = blog_title, blog_entry=blog_entry)

    blogs = Blog.query.all()
 #   blog_id = blog.blog.id
    return render_template('blog.html', blogs=blogs)#thought I have is to add blog_id= blog_id


#go to separate page that showcases an individual posting, one the user has selected from 
#the main page by clicking the blog title link
#I have blog_id = {blog_id} in hopes that it's converting between the varying id number's in blog db
@app.route('/show_individual_blog', methods = ['get'])
def display_blog():
    blog_title = ''
    blog_entry = ''
    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        blog_title = blog.blog_title
        blog_entry = blog.blog_entry
        return render_template('show_individual_blog.html', blog_title = blog_title, blog_entry=blog_entry)
    else:
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        blog_title = blog.blog_title
        blogentry = blog.blog_entry
        return render_template('show_individual_blog.html, blog_title=blog_title, blog_entry=blog_entry')
    #blog_url= request.args.get('blog_url')
    #blog = Blog.query.get(blog_id)
    #blogged_id = blog.id
    #blog_title = blog.blog_title
    #blog_entry = blog.blog_entry

    return render_template('show_individual_blog.html', blog_title=blog_title, blog_entry=blog_entry, blogged_id=blogged_id)

    
# I had int( request...) on line below at first, but then I think db stores id as a string value, so I took that part out
 # I don't think I want to request blog-id from the show_individual_blog.html
 #   blog_id = int(request.form['blog-id'])
 #   blog_id = Blog.query.get('blog.id')
 #   if blog_id:
 #       return redirect('/show_individual_blog?blog_id={0}'.format(blog.id))



@app.route('/newpost', methods = ['POST', 'GET'])
def make_entry():
    blog_title_error=''
    blog_entry_error=''


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
            blog = Blog(blog_title, blog_entry)
            db.session.add(blog)
            db.session.commit()
#here, I am grabbing the id number from the /newpost form with name = blog-id.  Is this a good idea? It's similar to get it done
#otherwise, it is possible to get it from the db. Well, I did change it to grab from the db(I think)
            blog_id = Blog.query.filter_by(blog_title=blog_title).first()
        
 #           blog_id = int(request.form['blog-id'])
        
            return redirect('/show_individual_blog?id={0}'.format(blog.id))
        else:
            return render_template('newpost.html', blog_title_error = blog_title_error, blog_entry_error=blog_entry_error, blog_title=blog_title, blog_entry=blog_entry)
                
if __name__=='__main__':
    app.run()

