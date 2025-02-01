import sqlite3
import json

def load_activities_into_db(db_name="itineraries.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    activity_data = open("db/data/activities.json", "r").read()
    activity_data = json.loads(activity_data)
    for activity in activity_data:
        cursor.execute('''
            INSERT INTO activities (id, name, city, address, latitude, longitude, avg_cost_per_person, duration, service_type, info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (activity['id'], activity['name'], activity['city'], activity['address'], activity['latitude'], activity['longitude'], activity['avg_cost_per_person'],
                activity['duration'], activity['service_type'], activity['info']))
    conn.commit()
    conn.close()
    print("Data loaded successfully into 'activities' tables.")
    
load_activities_into_db()

# -- deprecated 
def load_data_into_db(itinerary_data, db_name="itineraries.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    for itinerary in itinerary_data:
        cursor.execute('''
            INSERT INTO itineraries (name, location, duration_days, duration_nights)
            VALUES (?, ?, ?, ?)
        ''', (itinerary['name'], itinerary['location'], itinerary['duration_days'], itinerary['duration_nights']))
        
        # Montreal_5D4N_basic
        itinerary_id = cursor.lastrowid
        activity_data = open("db/data/Montreal_5D4N_basic.json", "r").read()
        activity_data = json.loads(activity_data)
        for activity in activity_data:
            if activity['itinerary_name'] == itinerary['name']:
                cursor.execute('''
                    INSERT INTO itinerary_activities (itinerary_id, day, time, location, activity, activity_desc, cuisine, avg_cost_per_person)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (itinerary_id, activity['day'], activity['time'], activity['location'], activity['activity'],
                      activity['activity_desc'], activity['cuisine'], activity['avg_cost_per_person']))
            
        # Montreal_5D4N_signature
        itinerary_id = 2
        activity_data = open("db/data/Montreal_5D4N_signature.json", "r").read()
        activity_data = json.loads(activity_data)
        for activity in activity_data:
            if activity['itinerary_name'] == itinerary['name']:
                cursor.execute('''
                    INSERT INTO itinerary_activities (itinerary_id, day, time, location, activity, activity_desc, cuisine, avg_cost_per_person)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (itinerary_id, activity['day'], activity['time'], activity['location'], activity['activity'],
                      activity['activity_desc'], activity['cuisine'], activity['avg_cost_per_person']))
                
        # Montreal_5D4N_luxury
        itinerary_id = 3
        activity_data = open("db/data/Montreal_5D4N_luxury.json", "r").read()
        activity_data = json.loads(activity_data)
        for activity in activity_data:
            if activity['itinerary_name'] == itinerary['name']:
                cursor.execute('''
                    INSERT INTO itinerary_activities (itinerary_id, day, time, location, activity, activity_desc, cuisine, avg_cost_per_person)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (itinerary_id, activity['day'], activity['time'], activity['location'], activity['activity'],
                      activity['activity_desc'], activity['cuisine'], activity['avg_cost_per_person']))
    conn.commit()
    conn.close()
    print("Data loaded successfully into 'itineraries' and 'itinerary_activities' tables.")

itinerary_data = [
    {"name": "Montreal_5D4N_basic", "location": "Montreal", "duration_days": 5, "duration_nights": 4},
    {"name": "Montreal_5D4N_signature", "location": "Montreal", "duration_days": 5, "duration_nights": 4},
    {"name": "Montreal_5D4N_luxury", "location": "Montreal", "duration_days": 5, "duration_nights": 4},
]

# load_data_into_db(itinerary_data)
