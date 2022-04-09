from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

# TODO: PUT/PATCH request - update
# TODO: DELETE request - delete
# TODO: deal with case sensitivity for search
# TODO: improve search functionality (search by different columns, search for word within a description)
# TODO: make sure postman is up to date, create documentation
# TODO: use Flask RESTful extension
# TODO: requirements file, README

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Park(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    park_name = db.Column(db.String(250), unique=True, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    nearest_metro = db.Column(db.String(250), nullable=False)
    borough = db.Column(db.String(250), nullable=False)
    has_bathrooms = db.Column(db.Boolean, nullable=False)
    has_parking = db.Column(db.Boolean, nullable=False)
    other_features = db.Column(db.String(1000))

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


db.create_all()

# db.session.add(
#     Park(
#         park_name="La Fontaine Park",
#         address="3819 Av. Calixa-Lavallée",
#         nearest_metro="Sherbrooke",
#         borough="Le Plateau-Mont-Royal",
#         has_bathrooms=1,
#         has_parking=1,
#         other_features="large pond"
#     )
# )
# db.session.add(
#     Park(
#         park_name="Maisonneuve Park",
#         address="4601 Sherbrooke St E",
#         nearest_metro="Pie-IX",
#         borough="Rosemont",
#         has_bathrooms=1,
#         has_parking=1,
#         other_features="lots of space"
#     )
# )
# db.session.commit()


@app.route("/")
def home():
    return render_template("index.html")


# GET request - all
@app.route("/all")
def show_all_parks():
    all_parks = db.session.query(Park).all()
    parks = [park.to_dict() for park in all_parks]
    return jsonify(parks)


# GET request - search
@app.route("/search")
def search():
    parks_found = Park.query.filter_by(borough=request.args.get('area')).all()
    if parks_found:
        return jsonify(parks=[park.to_dict() for park in parks_found])
    else:
        return jsonify({
            "Message": "No parks listed in that borough"
        })


# POST request - add
# TODO: do I need to verify GET v POST request?
# TODO: improve boolean parameter inputs
@app.route("/add", methods=["POST"])
def add_park():
    db.session.add(
        Park(
            park_name=request.args.get('park_name'),
            address=request.args.get('address'),
            nearest_metro=request.args.get('nearest_metro'),
            borough=request.args.get('borough'),
            has_bathrooms=bool(int(request.args.get('has_bathrooms'))),
            has_parking=bool(int(request.args.get('has_parking'))),
            other_features=request.args.get('other_features')
        )
    )
    db.session.commit()
    return jsonify({
        "Message": "New park added to database"
    })


if __name__ == '__main__':
    app.run(debug=True)
