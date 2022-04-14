from flask import Flask, render_template, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
from dotenv import load_dotenv
import os

# TODO: improve case sensitivity for search
# TODO: re-address boolean fields in add
# TODO: improve parameter validation
# TODO: utilise marshmallow

load_dotenv()

app = Flask(__name__)
api = Api(app)


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


# db.create_all()

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
class AllParks(Resource):
    def get(self):
        all_parks = db.session.query(Park).all()
        parks = [park.to_dict() for park in all_parks]
        return make_response(jsonify(parks), 200)


api.add_resource(AllParks, '/all')


# GET request - search
class SearchByBorough(Resource):
    def get(self):
        parks_found_by_borough = Park.query.filter(Park.borough.contains(request.args.get('area'))).all()
        if parks_found_by_borough:
            return make_response(jsonify(parks=[park.to_dict() for park in parks_found_by_borough]), 200)
        else:
            return make_response(jsonify({
                "Message": "No parks listed in that borough"
            }), 404)


api.add_resource(SearchByBorough, '/search-by-borough')


# GET request - search
class SearchByName(Resource):
    def get(self):
        parks_found_by_name = Park.query.filter(Park.park_name.contains(request.args.get('name'))).all()
        if parks_found_by_name:
            return make_response(jsonify(parks=[park.to_dict() for park in parks_found_by_name]), 200)
        else:
            return make_response(jsonify({
                "Message": "No park name matches found"
            }), 404)


api.add_resource(SearchByName, '/search-by-name')


# POST request - add
class AddPark(Resource):
    def post(self):
        db.session.add(
            Park(
                park_name=request.args.get('park_name'),
                address=request.args.get('address'),
                nearest_metro=request.args.get('nearest_metro'),
                borough=request.args.get('borough'),
                has_bathrooms=bool(int(request.args.get('has_bathrooms'))),
                has_parking=bool(int(request.args.get('has_parking'))),
                other_features=request.args.get('other_features'),
            )
        )
        db.session.commit()
        return make_response(jsonify({
            "Message": "New park added to database"
        }), 200)


api.add_resource(AddPark, '/add')


# PATCH request - update
class EditFeatures(Resource):
    def patch(self, park_id):
        features_to_add = request.args.get('features')
        park_to_edit = Park.query.get(park_id)
        if park_to_edit:
            park_to_edit.other_features = features_to_add
            db.session.commit()
            return make_response(jsonify({
                "Message": "Features updated"
            }), 200)
        else:
            return make_response(jsonify({
                "Message": "Park not found"
            }), 404)


api.add_resource(EditFeatures, '/edit-features/<int:park_id>')


# DELETE request - delete
class DeletePark(Resource):
    def delete(self, park_id):
        api_key = request.args.get('api-key')
        if api_key == "SecretPassword":
            park_to_delete = Park.query.get(park_id)
            if park_to_delete:
                db.session.delete(park_to_delete)
                db.session.commit()
                return make_response(jsonify({
                    "Message": "Park deleted"
                }), 200)
            else:
                return make_response(jsonify({
                    "Message": "Park not found"
                }), 404)
        else:
            return make_response(jsonify({
                "Message": "API key not accepted"
            }), 403)


api.add_resource(DeletePark, '/delete-park/<int:park_id>')

if __name__ == '__main__':
    app.run(debug=True)
