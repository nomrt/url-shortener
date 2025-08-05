import string, random
from flask import Flask, render_template, request, redirect
from models import db, URL
from flask import jsonify

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


@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.get_json()
    if not data or 'url' not in data:
        print("📩 API endpoint hit")

        return jsonify({'error': 'Missing URL in request'}), 400

    original_url = data['url']
    short_code = generate_short_code()

    while URL.query.filter_by(short_code=short_code).first():
        short_code = generate_short_code()

    new_url = URL(original_url=original_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    return jsonify({
        'original_url': original_url,
        'short_url': request.host_url + short_code
    }), 201

@app.route('/api/<short_code>', methods=['GET'])
def api_redirect(short_code):
    url = URL.query.filter_by(short_code=short_code).first()
    if url:
        return jsonify({'original_url': url.original_url}), 200
    else:
        return jsonify({'error': 'Short code not found'}), 404


