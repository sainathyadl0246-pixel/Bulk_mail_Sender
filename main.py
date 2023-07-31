from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from wtforms import StringField, SelectField, SubmitField, PasswordField, EmailField, TextAreaField
from wtforms.validators import DataRequired, URL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class RegisterForm2(FlaskForm):
    # todo = StringField("TODO", validators=[DataRequired()])
    todo = TextAreaField('Text', render_kw={"rows": 5, "cols": 11})
    submit = SubmitField("submit")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


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
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
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
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login'))

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
        new_to_do = Todolist(user=current_user, text=form.todo.data)
        print(form.todo.data)
        db.session.add(new_to_do)
        db.session.commit()
        print(current_user.todo)
        return redirect(url_for('get_all_posts'))
    return render_template('to_do_list.html', form=form)


@app.route('/getall', methods=['GET', 'POST'])
def get_all_posts():
    posts = current_user.todo
    form = RegisterForm2()
    if form.validate_on_submit():
        new_to_do = Todolist(user=current_user, text=form.todo.data)
        print(form.todo.data)
        db.session.add(new_to_do)
        db.session.commit()
        print(current_user.todo)
        return redirect(url_for('get_all_posts'))
    return render_template("getalltodos.html", all_posts=posts, logged_in=current_user.is_authenticated, form=form,current_user=current_user)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = Todolist.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)
