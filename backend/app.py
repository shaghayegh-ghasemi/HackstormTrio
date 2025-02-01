from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from planbuilder.api import fetch_activities, generate_plan, fetch_places_nearby
from planbuilder.database import initialize_database
import sqlite3
import json
import os


app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/api/tiers", methods=["GET"])
def get_tiers():
    return ["basic", "signature", "luxury"]

@app.route("/api/itinerary/extract", methods=["POST"])
def extract():
    data = request.form
    
    prompt = "\"" + data["query"] + "\"" + """\n\nFor the above string, extract the location and the 
    duration in the XDYN format, where X is the number of days and Y is the number of nights. Return the response in JSON format"""
    res = call_chatgpt_api(prompt)
    if res == {}:
        return {"error": "insufficient query data"}
    
    # TODO: Review and improve prompt
    if 'D' not in res["duration"]:
        print(res["duration"])
        d = res["duration"].split("/")[0]
        n = res["duration"].split("/")[1]
        res["duration"] = d + "D" + n + "N"
    
    return res

@app.route("/api/itinerary/generate", methods=["POST"])
def generate_itinerary():
    data = request.form
    
    location = data["location"]
    duration = data["duration"]
    plan = data["plan"]
    
    if plan not in ["basic", "signature", "luxury"]:
        return {"itinerary": []}
    itinerary_name = location + '_' + duration + '_' + plan
    conn = sqlite3.connect('itineraries.db')
    c = conn.cursor()
    c.execute('SELECT day, time, location, activity, activity_desc, cuisine, avg_cost_per_person FROM itinerary_activities where itinerary_id = (SELECT id from itineraries where name = ?)', (itinerary_name,))
    fields = [field_md[0] for field_md in c.description]
    result = [dict(zip(fields,row)) for row in c.fetchall()]
    conn.close()
    return {"itinerary": result}


@app.route("/api/restaurant/nearby", methods=["GET"])
def get_nearby_restaurant_list():
    data = request.form
    plan = data["plan"]
    location = data["location"]
    prompt = ""
    if plan == "basic":
        data = open("db/data/cached_datasets/3star_restaurants.json", "r").read()
        data_json = json.loads(data)
        # Filter for matching location
        response = [restaurant for restaurant in data_json if restaurant.get("name") == location]
        if not response:
            return {"err": "invalid location"}, 400
        # response = data_json[location]
    elif plan == "signature":
        data = open("db/data/cached_datasets/4star_restaurants.json", "r").read()
        data_json = json.loads(data)
        response = [restaurant for restaurant in data_json if restaurant.get("name") == location]
        if not response:
            return {"err": "invalid location"}, 400
    elif plan == "luxury":
        data = open("db/data/cached_datasets/5star_restaurants.json", "r").read()
        data_json = json.loads(data)
        response = [restaurant for restaurant in data_json if restaurant.get("name") == location]
        if not response:
            return {"err": "invalid location"}, 400
    else:
        return {"err": "invalid plan"}, 400

    return {"alternatives": response}


@app.route("/api/itinerary/edit", methods=["PUT"])
def edit_itinerary():
    data = request.form
    prompt = edit_itinerary_prompt(
        data["day"], data["activity"], data["old_activity"], data["new_activity"]
    )
    chatgpt_response = call_chatgpt_api(prompt)
    return {
        "prompt": prompt,
        "itinerary": chatgpt_response,
    }
    
@app.route("/api/itinerary/next", methods=["POST"])
def next_activity():
    data = request.form
    lat = data["lat"]
    lon = data["lon"]
    visited_activities= data["visited"]
    planned_activities= data["planned"]
    return data
    
    
def call_chatgpt_api(prompt):
    api_key = os.getenv("OPENAI_API_KEY")

    app_env = os.getenv("APP_ENV")
    if app_env == "dev":
        return {"location": "Montreal", "duration": "5D4N"}

    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )
    gpt_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )
    res = gpt_response.choices[0].message.content
    res_json = json.loads(res)
    return res_json

@app.route('/api/fetch_places', methods=['POST'])
def api_fetch_places():
    data = request.json
    location = data.get('location')
    query = data.get('query')
    radius = data.get('radius', 3000)

    if not location or not query:
        return jsonify({"error": "Missing required fields: 'location' and 'query'"}), 400

    try:
        places = fetch_places_nearby(location, query, radius)
        return jsonify(places), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetch_activities', methods=['POST'])
def api_fetch_activities():
    data = request.json
    location = tuple(data.get('location', [45.5128, -73.5460]))  # Default: Montreal
    radius = data.get('radius', 3000)

    try:
        activities = fetch_activities(location, radius)
        return jsonify(activities), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_plan', methods=['POST'])
def api_generate_plan():
    """
    input: Day x (number x: 2 to 5)
    :return: activities table's location and name, itinerary_activities' time,  end-time(activities table's duration + itinerary_activities'time)
    - itinerary.db including itinerary_activities table and activities table
    - front-end gives the page showing which day it is, and backend receives its day number.
    Then backend can call itineraries.db to return the data with day = x.
    """

    """
    Update the activities table: find the right lat & lng 
    and change the id in activities table to the correct one in itenaries table
    """
    data = request.json
    day = data.get("day")
    # test: 1<= day <= 5
    if not day or day > 5:
        return jsonify({"error": "Invalid Input. Day must be less than 6"}), 400

    try:
        plan = generate_plan(day)
        return jsonify(plan), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -- DEPRECATED -- 
# util funtions
def generate_3star_itinerary_prompt() -> str:
    """
    Returns a prompt that can be used to generate an itinerary
    """
    prompt = f"""Hotel List:
1. Hotel Chrome Montreal
2. Le Square Phillips Hotel And Suites
3. Hotel Zero 1

Pick one hotel in the above list, generate a travel itinerary for a 5 Days and 4 Nights getaway in Montreal, Canada. Include affordable activities for sightseeing, attractions and restaurant meals, making sure that the travel route minimises travel time and distance. Generate the result in the JSON format, with the following properties:
1. Day#
2. Time
3. Location
4. Activity
5. Activity Description
6. Average activity cost/person
"""

    return prompt


def generate_4star_itinerary_prompt() -> str:
    """
    Returns a prompt that can be used to generate an itinerary
    """
    prompt = f"""Hotel List:
1. Honeyrose Hotel
2. Hotel Bonaventure Montreal
3. Le St-Martin Hotel Montreal

Pick one hotel in the above list, generate a travel itinerary for a 5 Days and 4 Nights getaway in Montreal, Canada. Include mid-priced activities for sightseeing, attractions and restaurant meals, making sure that the travel route minimises travel time and distance. Generate the result in the JSON format, with the following properties:
1. Day #
2. Time
3. Location
4. Activity
5. Activity Description
6. Average activity cost/person
"""

    return prompt


def generate_5star_itinerary_prompt() -> str:
    """
    Returns a prompt that can be used to generate an itinerary
    """
    prompt = f"""Hotel List:
1. The Ritz-Carlton, Montreal
2. Four Seasons Montreal
3. Le Mount Stephen

Pick one hotel in the above list, generate a travel itinerary for a 5 Days and 4 Nights getaway in Montreal, Canada. Include affordable and luxury activities like sightseeing, attractions and restaurant meals, making sure that the travel route minimises travel time and distance. Generate the result in the JSON format, with the following properties:
1. Day #
2. Time
3. Location
4. Activity
5. Activity Description
6. Average activity cost/person
"""

    return prompt


def edit_itinerary_prompt(day, activity, old_activity, new_activity) -> str:
    prompt = f"""For the itinerary update the {activity} on day {day} from {old_activity} to {new_activity}. Generate the updated day itinerary result in the JSON format, with the following properties:
1. Day #
2. Time
3. Location
4. Activity
5. Activity Description
"""

    return prompt

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)