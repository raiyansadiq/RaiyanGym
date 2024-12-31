from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym.db'  # SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    plan = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Member {self.name}>'


with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/membership')
def membership():
    return render_template('membership.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        plan = request.form['plan']

        # Check if the email already exists
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            return render_template('membership.html', error="This email is already registered!")

        # Add the new member
        new_member = Member(name=name, email=email, plan=plan)
        new_member.set_password(password)
        db.session.add(new_member)
        db.session.commit()

        return redirect(url_for('thank_you', name=name))
    except Exception as e:
        return "An error occurred during registration. Please try again."

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Process contact form submission
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # Here, you can add logic to send an email or save to the database
        return render_template('contact.html', success=True)
    return render_template('contact.html')

@app.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        member = Member.query.filter_by(email=email).first()
        if member and member.check_password(password):
            return redirect(url_for('members'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
