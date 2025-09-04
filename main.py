import os
import openpyxl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SelectField, SubmitField, PasswordField, EmailField, TextAreaField, DateTimeField, \
    FileField
from wtforms.validators import DataRequired, URL
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import pandas as pd
from datetime import datetime
import smtplib
import time

UPLOAD_FOLDER = 'uploads'  # Create this directory in your project
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf', 'doc', 'docx'}  # Add other allowed extensions if needed


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


global posts, To_do_l
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# engine = create_engine("sqlite:///mydb.db", echo=True)
# Base.metadata.create_all(bind=engine)
#
# Session = sessionmaker(bind=engine)
# session = Session()

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class RegisterForm2(FlaskForm):
    # todo = StringField("TODO", validators=[DataRequired()])
    todo = TextAreaField('Text', render_kw={"rows": 5, "cols": 11})
    date = DateTimeField('Date for the task in mm/dd/yy', format='%m/%d/%y', validators=[DataRequired()])
    submit = SubmitField("submit")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class mailinfoForm(FlaskForm):
    email = StringField("Email*", validators=[DataRequired()])
    password = PasswordField("Password*", validators=[DataRequired()])
    file = FileField("Upload excel file*", validators=[DataRequired()])
    file2 = FileField("Upload resume*")
    file3=FileField("Upload content of mail in txt format*")
    text=StringField("Subject for Resume, Enter in Caps*",validators=[DataRequired()])
    submit = SubmitField("Click to send mails")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    todo = relationship("Todolist", back_populates="user")
    name = db.Column(db.String(100))


class Todolist(db.Model):
    __tablename__ = "hobby"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.String(250), nullable=False)
    Date = db.Column(db.String(50), nullable=False)
    user = relationship("User", back_populates="todo")


with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/', methods=['GET', 'POST'])
def home():
    global To_do_l
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        print(email)
        print(password)
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('home'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('home'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template('home.html', form=form)


@app.route('/logout')
def logout():
    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash messsage
            # Redirect to /login route.
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('home'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('create_todo'))
    return render_template('signup.html', form=form)


@app.route('/create_todo', methods=["POST", "GET"])
def create_todo():
    form = RegisterForm2()
    if form.validate_on_submit():
        new_to_do = Todolist(user=current_user, text=form.todo.data, Date=form.date.data)
        print(form.todo.data)
        print(form.date.data)
        db.session.add(new_to_do)
        db.session.commit()
        print(current_user.todo)
        return redirect(url_for('get_all_posts'))
    return render_template('to_do_list.html', form=form)


@app.route('/getall', methods=['GET', 'POST'])
def get_all_posts():
    global To_do_l, posts
    posts = current_user.todo
    tree = []
    with open('data.csv', mode='r') as file:

        # reading the CSV file
        csvFile = csv.reader(file)
        for lines in csvFile:
            tree.append(lines)
        # print(csvFile)
    # p=(current_user.todo.text,current_user.email)
    print(tree)
    for post in posts:
        t = [post.text, current_user.email, post.Date]
        tree.append(t)
    print(tree)
    with open(file="data.csv", mode='w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Text", "Mail", "time"])
        csvwriter.writerows(tree)
    # with open(filename,'w') as csvfile:
    #     csvwriter=csv.writer(csvfile)
    with open('data.csv', 'r') as in_file, open('data2.csv', 'w') as out_file:
        seen = set()  # set for fast O(1) amortized lookup
        for line in in_file:
            if line in seen: continue  # skip duplicate
            seen.add(line)
            out_file.write(line)
    f = open("data.csv", "w")
    f.truncate()
    f.close()
    with open('data2.csv', 'r') as in_file, open('data.csv', 'w') as out_file:
        seen = set()  # set for fast O(1) amortized lookup
        for line in in_file:
            seen.add(line)
            out_file.write(line)
    form = RegisterForm2()
    if form.validate_on_submit():
        new_to_do = Todolist(user=current_user, text=form.todo.data, Date=form.date.data)
        print(form.todo.data)
        db.session.add(new_to_do)
        db.session.commit()
        print(current_user.todo)
        # print(posts.Date)
        return redirect(url_for('get_all_posts'))
    return render_template("getalltodos.html", all_posts=posts, logged_in=current_user.is_authenticated, form=form,
                           current_user=current_user)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = Todolist.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/mail_sender", methods=['GET', 'POST'])
def mail_sender():
    form = mailinfoForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        text=form.text.data
        print(email)
        print(password)
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)  # Secure the filename
            file_path1=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_path1)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file2 = request.files['file2']
        if file2:
            filename = secure_filename(file2.filename)
            file_path2 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_path2)
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file3 = request.files['file3']
        if file3:
            filename = secure_filename(file3.filename)
            file_path3 = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(file_path3)
            file3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        workbook = openpyxl.load_workbook(file_path1)

        # Select a sheet
        sheet = workbook.active  # Or workbook['SheetName']
        e_list = []

        # Read data from a specific cell
        cell_value = sheet['A1'].value
        print(f"Value of A1: {cell_value}")

        # Iterate through rows and print values
        for row in sheet.iter_rows():
            for cell in row:
                e_list.append(cell.value)
        e_list.pop(0)
        print(e_list)
        e_list = [item for item in e_list if item is not None]
        print(e_list)
        names_list = [email.split('@')[0].split('.')[0] for email in e_list]
        print(names_list)
        names_list_title_case = [name.title() for name in names_list]
        print(names_list_title_case)
        # Create new lists to store the filtered values
        filtered_e_list = []
        filtered_names_list = []

        # Iterate through the lists using indices
        for i in range(len(e_list)):
            if "@" in e_list[i]:
                filtered_e_list.append(e_list[i])
                filtered_names_list.append(names_list_title_case[i])

        # Update the original lists with the filtered values
        e_list = filtered_e_list
        names_list = filtered_names_list

        print("Filtered e_list:", e_list)
        print("Filtered names_list:", names_list)
        e_list_lower = [email.lower() for email in filtered_e_list]
        print(e_list_lower)
        import re

        cleaned_names_list = []
        for name in names_list:
            # Remove numbers and symbols using regex
            cleaned_name = re.sub(r'[^a-zA-Z\s]', '', name)
            cleaned_names_list.append(cleaned_name)

        filtered_names_list = cleaned_names_list
        print(filtered_names_list)

        # Define your email address and password
        sender_email = email  # Replace with your email
        sender_password = password  # Replace with your password

        # Define SMTP server details (example for Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587  # For TLS

        print("Email environment configured.")
        # Define the resume path and prepare the attachment
        resume_path = file_path2

        # Open the file in read-binary mode
        with open(resume_path, 'rb') as attachment:
            # Create a MIMEBase object
            part = MIMEBase("application", "octet-stream")

            # Set the payload to the content of the attachment
            part.set_payload(attachment.read())

        # Encode the payload using Base64
        encoders.encode_base64(part)

        # Set the Content-Disposition header
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {resume_path}",
        )
        e_mails_sent=[]

        # Read the email body from the text file
        try:
            with open(file_path3,
                      "r") as email_file:  # Assuming the email body is in a file named email_body.txt
                email_body_template = email_file.read()
        except FileNotFoundError:
            print("Error: 'email_body.txt' not found. Please upload the email body file.")
            email_body_template = "Hello {name},\n\nPlease find my resume attached.\n\nSincerely,\nYour Name"  # Default body if file not found

        # Iterate through the lists and send emails
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)

            for recipient_email, name in zip(e_list_lower, filtered_names_list):
                # Create the email message
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = text # Replace with your subject

                # Personalize the email body
                email_body = email_body_template.format(name=name)

                # Attach the body with the plain text format
                msg.attach(MIMEText(email_body, 'plain'))

                # Attach the resume
                msg.attach(part)

                # Send the email
                server.sendmail(sender_email, recipient_email, msg.as_string())
                e_mails_sent.append(recipient_email)
            folder_path="uploads"
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(filename, "is removed")
            return render_template("sent_mails.html",e_mails_sent=e_mails_sent)

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('home'))
        else:
            login_user(user)

            return redirect(url_for('get_all_posts'))
    return render_template("mail.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)

from datetime import datetime
