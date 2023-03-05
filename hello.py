from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Create an instance of Flask
app = Flask(__name__)

# Add database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# working with mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Password%401995@localhost/our_users'

#Create a secret key
app.config['SECRET_KEY'] = "my super secrte key that is not supposed to be seen by anyone"

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#app.app_context().push()
# Create a Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # hashing the password
    password_hash = db.Column(db.String(120))

    @property
    def password(self):
        raise AttributeError('password is not readable!!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Include app_context() to crate database 
with app.app_context():
    db.create_all()

# Create a String
def __repr__(self):
    return '<Name %r>' % self.name

# Create a flask form
class NamerForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a password checking form
class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
# Tags used in jinja template can be changed accordingly
# safe - to render on page without html tag
# capitalize
# lower
# upper
# title
# trim
# striptags

# Create a route decorator
@app.route('/')
def index():
    first_name = "Aditi"
    stuff = "This is a <strong>Bold</strong> text"
    title_ex = "Hi its me, i'm the problem its me."
    favorite_pizza = ['Peporronica', 'Farmhouse', 'Cheese', 'Onion']
    return render_template('index.html', first_name=first_name, stuff=stuff, title_ex=title_ex, favorite_pizza=favorite_pizza)

# localhost:5000/user/john
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    render_template("500.html"), 500


# Create a form
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()

    # Validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!!")
    return render_template('name.html', name=name, form=form)

# Create an add user route
@app.route('/add_user', methods=['GET','POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash the password incoming from form
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            print(user)
        
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash("User Added Successfully!!")
    our_users = Users.query.order_by(Users.date_added)
    print(our_users)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

# Updating user details
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully")
            return render_template('update.html', form = form, name_to_update = name_to_update)
        except:
            flash("Oops! Something went wrong!, Please try again!")
            return render_template('update.html', form = form, name_to_update = name_to_update)
        
    else:
       return render_template('update.html', form = form, name_to_update = name_to_update, id=id)

 # Deleteing user from db   
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")
        our_users = Users.query.order_by(Users.date_added)
        print(our_users)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("Oops! Something went wrong.")
        our_users = Users.query.order_by(Users.date_added)
        print(our_users)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    
    # testing if password matches on login
@app.route('/test_pw', methods=['GET', 'POST'])
def test_password():
    email = None
    password = None
    passed = None
    pw_to_check = None
    form = PasswordForm()

    # Validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check hashed password if matching
        passed = check_password_hash(pw_to_check.password_hash, password)
        print(passed)
        #flash("Form Submitted Successfully!!")
    return render_template('test_pwd.html', email=email, password_hash=password, pw_to_check=pw_to_check, passed=passed, form=form)



    ## WTF Fields
    # BooleanField
    # DateField
    # DateTimeField
    # DecimalField
    # FileField
    # HiddenField
    # MultipleField
    # FieldList
    # FloatField
    # FormField
    # IntegerField
    # PasswordField
    # RadioField
    # SelectField
    # SelectMultipleField
    # SubmitField
    # StringField
    # TextAreaField


    ## Validators
    # DataRequired
    # Email
    # EqualTo
    # InputRequired
    # IPAddress
    # Length
    # MacAddress
    # NumberRange
    # Optional
    # Regexp
    # URL
    # UUID
    # AnyOf
    # NoneOf

if __name__ == '__main__':
    app.run(debug=True)
