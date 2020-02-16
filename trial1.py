from flask import Flask,render_template as ren,request,session,redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail

with open('parameter.json', 'r') as c:
    param = json.load(c)["param"]

app=Flask(__name__)

app.secret_key = 'super secret key'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = param['user_email']
app.config['MAIL_PASSWORD'] = param['user_password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail()
mail.init_app(app)




local_server=True


if(local_server==True):
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/my_blog"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/my_blog"
db = SQLAlchemy(app)


class Contact(db.Model):
    # sno,name,email,phone_number,message,date

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=False)
    phone_number = db.Column(db.String(120), unique=False, nullable=False)
    message = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=True)


class Post(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def index():
    post = Post.query.filter_by().all()[0:param['no_of_post']]

    return ren('index.html', param=param,post=post)

# edit


@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    post = db.session.query(Post).filter_by(sno=sno).first()

    if 'user' in session and session['user'] == param['user_name']:

        if request.method == 'POST':
            title = request.form.get('title_box')
            content = request.form.get('content')
            slug = request.form.get('slug')
            date = datetime.now()
            if sno == '0':
                post = Post(title=title, slug=slug, content=content, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = db.session.query(Post).filter_by(sno=sno).first()
                post.title = title
                post.slug = slug
                post.content = content
                db.session.commit()
                return redirect("/edit/" + sno)



    return ren('edit.html', param=param,post=post, sno=sno)


@app.route("/post/<string:post_slug>", methods=["GET"])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return ren('post.html', param=param, post=post)


@app.route("/about")
def about():
    return ren('about.html', param=param)

# Dashboard


@app.route("/dashboard", methods=['GET', 'POST'])
def login():
    post = Post.query.filter_by().all()

    if 'user' in session and session['user'] == param['user_name']:
        return ren('dashboard.html', post=post, param=param)

    if request.method == 'POST':
        name = request.form.get('uname')
        pas_code = request.form.get('pass')
        if name == param['user_name'] and pas_code == param['password']:
            session['user'] = 'name'

            return ren('dashboard.html', post=post, param=param)

    return ren('login.html', param=param,post=post)

#      Contact


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method == 'POST'):


        # add entry to database#

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        # sno,name,email,phone_number,message,date

        entry = Contact(name=name, email=email, phone_number=phone, message=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + email,
                          sender=email,
                          recipients=[param['user_email']],
                          body=message + " " + phone + " " + "by" + " " + name
                          )
    post = Post.query.filter_by().first()
    return ren('contact.html', param=param,post=post)


app.run(debug=True)




