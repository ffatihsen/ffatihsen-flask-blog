from flask import Flask,render_template,request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Message,Mail
from werkzeug import secure_filename
import os
import math




app=Flask(__name__)

app.secret_key="super-secret-key"

app.config["UPLOAD_FOLDER"]="C:\\Users\\90542\\Desktop\\yukle"


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sennfatih1999@gmail.com'
app.config['MAIL_PASSWORD'] = 'şifre'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

app.config['DATABASE_URI'] = 'sqlite:////Udemy3/flask_udemy/blog.db'



db = SQLAlchemy(app)

class Contacts(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num=db.Column(db.String(12), nullable=False)
    msg=db.Column(db.String(120), nullable=False)
    email=db.Column(db.String(20), nullable=False)
    date=db.Column(db.String(12), nullable=True)


class Posts(db.Model):
    num = db.Column(db.Integer, primary_key=True)
    baslik=db.Column(db.String(30), nullable=False)
    alt_bas = db.Column(db.String(30), nullable=False)
    url_yap=db.Column(db.String(30), nullable=False)
    içerik=db.Column(db.String(120), nullable=False)



@app.route("/post/<string:url_yap>",methods=["GET","POST"])
def post(url_yap):
    if(request.method=="GET"):
        posto=Posts.query.filter_by(url_yap=url_yap).first()
        return render_template("post.html",posto=posto)
    return render_template("post.html")



@app.route("/contact",methods=["GET","POST"])
def contact():
    if(request.method=="POST"):
        name=request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        entry=Contacts(name=name,phone_num=phone,msg=message,date=datetime.now(),email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("Blogtan yeni mesaj var "+name,
                          sender=email,
                          recipients=["sennfatih1999@gmail.com"],
                          body=message+"\n"+phone)
        return redirect(url_for("index"))

    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dashboard",methods=["GET","POST"])
def dashboard():
    kullanıcı_adı="fatih1234"
    kullanıcı_pass="1478523"

    if("user" in session and session["user"]==kullanıcı_adı):
        posts=Posts.query.all()
        return render_template("dashboard.html",posts=posts)

    if(request.method=="POST"):
        username=request.form.get("uname")
        userpass=request.form.get("pass")
        if(username==kullanıcı_adı and userpass==kullanıcı_pass):
            session["user"]=username
            posts = Posts.query.all()
            return render_template("dashboard.html",posts=posts)
    else:
        return render_template("login.html")



@app.route("/")
def index():
    sayi=3
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/(sayi))
    page=request.args.get("page")
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*(sayi) : (page-1)*(sayi)+(sayi)]
    if(page==1):
        geri="#"
        next="/?page="+str(page+1)
    elif(page==last):
        geri="/?page="+str(page-1)
        next="#"

    else:
        next = "/?page=" + str(page + 1)
        geri = "/?page=" + str(page - 1)
    return render_template("index.html",posts=posts,geri=geri,next=next)


@app.route("/edit/<string:num>",methods=["GET","POST"])
def edit(num):
    kullanıcı_adı="fatih1234"
    kullanıcı_pass="1478523"
    if ("user" in session and session["user"] == kullanıcı_adı):
        if(request.method=="POST"):
            box_title=request.form.get("baslik")
            box_altbas = request.form.get("altbaslik")
            box_içerik = request.form.get("içerik")
            box_url_yap = request.form.get("url_yap")
            if(num=="0"):
                entry = Posts(baslik=box_title, alt_bas=box_altbas, url_yap=box_url_yap, içerik=box_içerik)
                db.session.add(entry)
                db.session.commit()

            else:
                post=Posts.query.filter_by(num=num).first()
                post.baslik=box_title
                post.alt_bas=box_altbas
                post.içerik=box_içerik
                post.url_yap= box_url_yap

                db.session.commit()
                return redirect("/edit/"+num)
        post=Posts.query.filter_by(num=num).first()
        return render_template("edit.html",post=post,num=num)


@app.route("/uploader",methods=["GET","POST"])
def uploader():
    kullanıcı_adı="fatih1234"
    kullanıcı_pass="1478523"
    if ("user" in session and session["user"] == kullanıcı_adı):
        if(request.method=="POST"):
            f=request.files["file1"]
            f.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(f.filename)))
            return "Başarıyla yüklendi"


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/dashboard")

@app.route("/delete/<string:num>")
def delete(num):
    kullanıcı_adı="fatih1234"
    kullanıcı_pass="1478523"
    if ("user" in session and session["user"] == kullanıcı_adı):
        post=Posts.query.filter_by(num=num).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


# Create DB if not exist
db.create_all()

if __name__ == '__main__':
    app.run(debug=True)