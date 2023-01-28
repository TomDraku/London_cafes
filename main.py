from flask import Flask, render_template, url_for, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import random



app = Flask(__name__)

#Connect to Database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)


#Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    map_url = db.Column(db.String(255), unique=True)
    img_url = db.Column(db.String(255), unique=True)
    location = db.Column(db.String(255), unique=False)
    has_sockets = db.Column(db.Integer)
    has_toilet = db.Column(db.Integer)
    has_wifi = db.Column(db.Integer)
    can_take_calls = db.Column(db.Integer)
    seats = db.Column(db.String(255), unique=False)
    coffee_price = db.Column(db.String(255), unique=False)
    
    def to_dict(self):
        #Method 1. 
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

    
    
#cafe website
@app.route("/")
def home():
    cafes = Cafe.query.all()
    return render_template("index.html",cafes=cafes)

@app.route("/api")
def api():
    my_documentation = "https://documenter.getpostman.com/view/19153758/UVXjLGrb"
    return render_template("api_index.html",link=my_documentation)

# HTTP GET - Read Record

@app.route("/random")
def get():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={'can_take_calls':random_cafe.can_take_calls, 
                   'coffee_price':random_cafe.coffee_price,
                   'has_sockets':random_cafe.has_sockets, 
                   'has_toilet':random_cafe.has_toilet,
                   'has_wifi':random_cafe.has_wifi, 
                   'id':random_cafe.id, 
                   'img_url':random_cafe.img_url, 
                   'location':random_cafe.location,
                   'map_url':random_cafe.map_url,
                   'name':random_cafe.name, 
                   'seats':random_cafe.seats}
                  )
    
@app.route("/all")
def get_all():
    all_cafes = db.session.query(Cafe).all()
    print(all_cafes)
    my_all_cafes = []
    for cafe in all_cafes:
        my_all_cafes.append(cafe.to_dict())
    return jsonify(cafe=my_all_cafes)

# HTTP POST - Create Record

@app.route("/search")
def search():
    query_location = request.args.get("loc")
    my_cafe = Cafe.query.filter_by(location=query_location).all()
    if len(my_cafe) > 0:
        all_nearest_cafes = []
        for cafe in my_cafe:
            all_nearest_cafes.append(cafe.to_dict())
        return jsonify(cafe=all_nearest_cafes)
    else:
        message = {"Not found":"Sorry we don't have a cafe at this lokation"}
        return jsonify(error=message)

@app.route("/add", methods=['GET', 'POST'] )
def add():
    
    cafe = Cafe(
        name=request.form.get("name"), 
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(int(request.form.get("has_toilet"))),
        has_wifi=bool(int(request.form.get("has_wifi"))),
        can_take_calls=bool(int(request.form.get("can_take_calls"))),
        coffee_price=request.form.get("coffee_price"),
        has_sockets=bool(int(request.form.get("has_sockets")))
    )
    db.session.add(cafe)
    db.session.commit()
    message = {"success":"Successfully added the new cafe"}
    return jsonify(response = message)

# HTTP PUT/PATCH - Update Record

@app.route("/update-price/<cafe_id>", methods=['GET','PATCH'])
def update_price(cafe_id):
    new_price=request.args.get("new_price")
    print(new_price)
    try:
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.coffee_price = new_price
    except AttributeError:
        message = {"error":"Sorry the cafe with that id was not found in the database"}
        return jsonify(response = message)
    else:
        db.session.commit()  
        message = {"success":"Successfully updated the price of coffee"}
        return jsonify(response = message)
    
# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['GET', 'DELETE'])
def delate(cafe_id):
    user_api_key=request.args.get("api-key")
    print(user_api_key)
    
    api_key = "TopSecretAPIKey"
    if user_api_key == api_key:
        cafe_to_delete = Cafe.query.get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            message = {"success":"Successfully delated the cafe"}
            return jsonify(response = message)
        else:
            message = {"error":"Sorry the cafe with that id was not found in the database"}
            return jsonify(response = message)
    else:
        message = {"error":"Sorry that is not allowed. Make sure that you have the right api key"}
        return jsonify(response = message)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    


