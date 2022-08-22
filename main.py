from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def into_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET Requests - Read Records
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.into_dict()), 200


@app.route("/all")
def get_all():
    cafes = db.session.query(Cafe).all()
    all_dict = {}
    for cafe in cafes:
        all_dict.update({cafe.name: cafe.into_dict()})
    return jsonify(cafe=all_dict), 200


@app.route("/search")
def search():
    location = request.args.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=location).all()
    if cafes:
        return jsonify(cafe=[cafe.into_dict() for cafe in cafes]), 200
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"}), 404


# HTTP POST Requests - Create Records
@app.route("/add", methods=['POST'])
def add():
    new_cafe = Cafe(
        name=request.form.get('name'),
        map_url=request.form.get('map_url'),
        img_url=request.form.get('img_url'),
        location=request.form.get('location'),
        has_toilet=bool(request.form.get('has_toilet')),
        has_wifi=bool(request.form.get('has_wifi')),
        has_sockets=bool(request.form.get('has_sockets')),
        can_take_calls=bool(request.form.get('can_take_calls')),
        seats=request.form.get('seats'),
        coffee_price=request.form.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'Success': 'Successfully added the new cafe! Thank you for your submission!'}), 200


# HTTP PATCH Requests - Update Records
@app.route("/change-price/<int:cafe_id>", methods=['PATCH'])
def edit_price(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        new_price = request.args.get('new_price')
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={'Success': 'Successfully changed the coffee price! Thank you for your submission!'}), 200
    else:
        return jsonify(error={'Error': 'There is no cafe with that ID. Check the ID and try again!'}), 404


# HTTP DELETE Requests - Delete Records
@app.route('/closed_cafe/<cafe_id>', methods=['DELETE'])
def close_cafe(cafe_id):
    key = request.args.get("api_key")
    if key == "TopSecretAPIKey":
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={'Success': 'Successfully closed the cafe! Thank you for your submission!'}), 200
        else:
            return jsonify(error={'Error': 'There is no cafe with that ID. Check the ID and try again!'}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
