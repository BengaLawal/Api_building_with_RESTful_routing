from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

#  Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# cafe TABLE Configuration
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

    def __repr__(self):
        return f'Cafe - {self.name}'

    def to_dict(self):
        """serialising database row Object to JSON by converting it to dictionary and using jsonify to convert dict to JSON"""
        dictionary = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return dictionary


# db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=['GET'])
def get_random_cafe():
    """get random cafe from the db"""
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    print(random_cafe)
    return jsonify(cafe=random_cafe.to_dict())

@app.route('/all')
def all_cafes():
    """get all cafe in database"""
    cafes = db.session.query(Cafe).all()
    cafe_list = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafe=cafe_list)

@app.route('/search')
def search():
    """search the cafes from a set location in the url bar"""
    # search if a parameter (passed in with ?loc="x") was passed
    query_location = request.args.get('loc')
    if query_location:  # if a query was passed
        cafe_in_same_location = db.session.query(Cafe).filter_by(location=query_location)
        # cafe_in_same_location = Cafe.query.filter_by(location=query_location)
        print(cafe_in_same_location)
        cafe_list = [cafe.to_dict() for cafe in cafe_in_same_location]
        if cafe_list:
            return jsonify(cafe=cafe_list)
        else:
            return jsonify(error={
                'Not Found': "We don't have a cafe at that location."
            })
    else:
        return jsonify(error={
            'Not Found': "sorry, you have not passed a parameter - use ?loc={your location}"
        })

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    """add cafe to the database"""
    # change ImmutableMultiDict to dict
    cafe_response = request.form.to_dict()
    print(cafe_response)
    for key, value in cafe_response.items():
        if value.lower() == 'true':
            cafe_response[key] = True  # the value is changed to a boolean which will show as 1 or 0 in the db
        elif value.lower() == 'false':
            # if left empty it will return false
            cafe_response[key] = bool('')
    data = Cafe(**cafe_response)  # ** to get rid of type error: takes 1 p-arg but 2 was given
    db.session.add(data)
    db.session.commit()
    return jsonify(response={
        'success': 'Successfully added new cafe'
    })

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    """Update the price"""
    row_to_update = Cafe.query.get(cafe_id)  # cafe to update
    new_price = request.args.get('new_price')  # get new price from 'form/query'
    if row_to_update:
        row_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success='Successfully updated the price')
    else:
        return jsonify(error={
            'Not found': 'Sorry a cafe with that id was not found in the database'
        })

@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    """delete a row of cafe based on the passed id"""
    api_key = request.args.get('api_key')
    if api_key == "secretkey":
        cafe_in_same_location = db.session.query(Cafe).get(cafe_id)
        if cafe_in_same_location:
            db.session.delete(cafe_in_same_location)
            db.session.commit()
            return jsonify(success='The cafe has been removed')
        else:
            return jsonify(error='Sorry, a cafe with that id does not exist in the database')
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the right api_key")


if __name__ == '__main__':
    app.run(debug=True)