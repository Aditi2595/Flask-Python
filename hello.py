from flask import Flask, render_template

# Create an instance of Flask
app = Flask(__name__)

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