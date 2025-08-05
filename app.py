import string, random
from flask import Flask, render_template, request, redirect
from models import db, URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_code = generate_short_code()

        # Ensure uniqueness
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate_short_code()

        new_url = URL(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()

        return render_template('index.html', short_url=request.host_url + short_code)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_short_url(short_code):
    url = URL.query.filter_by(short_code=short_code).first_or_404()
    return redirect(url.original_url)
