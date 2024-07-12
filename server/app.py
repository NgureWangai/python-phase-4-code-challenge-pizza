#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Setting up Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initializing Flask-Migrate and SQLAlchemy
migrate = Migrate(app, db)
db.init_app(app)

# Initializing Flask-RESTful API
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantsResource(Resource):
    def get(self):
        restaurants = [n.to_dict() for n in Restaurant.query.all()]
        for hero in restaurants:
            hero.pop('restaurant_pizzas', None)
        return make_response(restaurants, 200)

api.add_resource(RestaurantsResource, "/restaurants")

class RestaurantDetails(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        response_dict = restaurant.to_dict()
        return response_dict, 200
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant is None:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantDetails, "/restaurants/<int:id>")

class PizzasList(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Pizza.query.all()]
        response = make_response(
            response_dict_list,
            200,
        )
        return response
    
api.add_resource(PizzasList, "/pizzas")

class RestaurantPizzasList(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return new_restaurant_pizza.to_dict(), 201
        except ValueError:
            db.session.rollback()
            return {"errors": ["validation errors"]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 400

api.add_resource(RestaurantPizzasList, '/restaurant_pizzas')


if __name__ == "__main__":
    app.run(port=5555, debug=True)
