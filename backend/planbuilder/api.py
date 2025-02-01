import sqlite3
from datetime import datetime, timedelta
import googlemaps
import json
from .config import GOOGLE_API_KEY
from .database import initialize_database, is_location_fetched, load_places_from_db, save_fetched_region, save_places_to_db
from .utils import build_itinerary_json, build_itinerary_timeline, haversine_distance
from .planning import categorize_place, count_mealtimes_in_window, filter_and_prepare_places, filter_places_by_travel_time, greedy_itinerary_planner

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

def fetch_places_nearby(location, query, radius):
    try:
        categories = ["tourist_attractions", "restaurant", "museum", "movie_theaters"]
        # Load places from the database
        places = load_places_from_db()

        # Filter places by query (category) and radius
        filtered_places = []
        for place in places:
            # Check if the category matches the query
            if query.lower() not in place["category"].lower() and query.lower() != "all categories":
                continue

            # Calculate the distance to check if the place is within the radius
            distance = haversine_distance(location[0], location[1], place["lat"],
                                          place["lng"]) * 1000  # Convert to meters
            if distance is not None and distance <= radius:
                filtered_places.append(place)

        # If no places found in the database, return an empty list
        if not filtered_places:
            print(f"No places found for query '{query}' within {radius} meters.")
            return []

        print(f"Found {len(filtered_places)} places matching '{query}' within {radius} meters.")
        return filtered_places
        # Fetching new data from Google Places API
        # print("Fetching new data from Google Places API.")
        # result = gmaps.places_nearby(
        #     location=location,
        #     radius=radius,
        #     keyword=query,
        #     open_now=False
        # )
        #
        #
        # formatted_places = []
        # for place in result.get("results", []):
        #     #
        #     lat = place["geometry"]["location"].get("lat")
        #     lng = place["geometry"]["location"].get("lng")
        #
        #     formatted_places.append({
        #         "place_id": place.get("place_id"),
        #         "name": place.get("name"),
        #         "lat": lat,
        #         "lng": lng,
        #         "rating": place.get("rating", None),
        #         "price_level": place.get("price_level", None),
        #     })
        # return formatted_places
    except Exception as e:
        print(f"Error fetching places: {e}")
        return []

def fetch_activities(location, radius=3000):
    """
    Fetch multiple categories: tourist attractions, restaurants, movie theaters.
    Merge them into a unique list (deduplicating by place_id).
    Utilizes the database to avoid redundant API calls.
    """
    categories = ["tourist_attractions", "restaurant", "museum", "other"]
    all_places = []
    
    # Check if the current location has already been fetched
    if is_location_fetched(location[0], location[1], radius):
        print("Using cached data from the database.")
        # Load existing places from DB that are within the radius
        combined_places = load_places_from_db()
        # Filter places within the radius
        # Filter places within the radius
        filtered_places = []
        for p in combined_places:
            distance_m = haversine_distance(location[0], location[1], p["lat"], p["lng"]) * 1000  # Convert km to meters
            # Skip places with invalid or None distances
            if distance_m is None:
                print(f"Skipping place due to invalid distance: {p}")  # Optional: Debugging output
                continue

            # Add place if within the radius
            if distance_m <= radius:
                filtered_places.append(p)

        return filtered_places
    else:
        print("fetch_activities: Fetching new data from Google Places API.")
        
        for cat in categories:
            fetched_places = fetch_places_nearby(location, cat, radius=radius)
            all_places.extend(fetched_places)
        
        if not all_places:
            print("No places found for the given categories and location.")
            return []
        
        # Deduplicate by place_id
        unique_places = {p["place_id"]: p for p in all_places}.values()
        unique_places = list(unique_places)
        
        # Categorize new places
        categorized_places = []
        for p in unique_places:
            p["category"] = categorize_place(p)
            categorized_places.append({
                "place_id": p["place_id"],
                "name": p["name"],
                "lat": p["geometry"]["location"]["lat"],
                "lng": p["geometry"]["location"]["lng"],
                "rating": p.get("rating"),
                "price_level": p.get("price_level"),
                "category": p["category"]
            })
        
        # Save new places to DB
        if categorized_places:
            save_places_to_db(categorized_places)
            # Save fetched region
            save_fetched_region(location[0], location[1], radius)
        
        return categorized_places

def generate_plan(day):
    itinerary_DB_file = "itineraries.db"
    conn = sqlite3.connect(itinerary_DB_file)
    cursor = conn.cursor()

    query = """
    SELECT 
            activities.latitude, 
            activities.longitude,
            itinerary_activities.location, 
            itinerary_activities.activity, 
            itinerary_activities.activity_desc, 
            itinerary_activities.time, 
            activities.duration
    FROM 
            itinerary_activities
    INNER JOIN
            activities
    ON
            itinerary_activities.id = activities.id
    WHERE
            itinerary_activities.day = ?
    """
    cursor.execute(query, (day, ))
    rows = cursor.fetchall()

    result = []
    for row in rows:
        latitude, longitude, location, activity, activity_desc, time, duration = row
        time = datetime.strptime(time, "%I:%M %p") # Convert time to datetime
        end_time = (time + timedelta(minutes=duration)).strftime("%I:%M %p")
        result.append({
            "lat": latitude,
            "lng": longitude,
            "name": location,
            "activity": activity,
            "activity_desc": activity_desc,
            "time": time.strftime("%H:%M"),
            "end_time": end_time
        })
    return result

    # # Extract input parameters
    # location = tuple(request_data.get("location", [45.4, -73.5]))  # Montreal
    # hotel_location = tuple(request_data.get("hotel_location", [45.5110, -73.5598]))
    # budget = request_data.get("budget", 500)
    # start_time_str = request_data.get("start_time", "2025-01-26 11:00")
    # end_time_str = request_data.get("end_time", "2025-01-26 19:00")
    # visited_locations = set(request_data.get("visited_locations", []))
    # planned_locations = set(request_data.get("planned_locations", []))
    # radius = request_data.get("radius", 3000)
    # max_travel_time = request_data.get("max_travel_time", 60)
    # # Convert datetime strings
    # start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
    # end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
    # # Fetch and filter places
    # combined_places = fetch_activities(location, radius)
    # # print(f"Combined places: {json.dumps(combined_places, indent=4)}")
    # candidate_places = filter_and_prepare_places(
    #     combined_places, visited_locations, planned_locations, budget, location, radius
    # )
    # if not candidate_places:
    #     print("No activities found for the given location and criteria. ")
    #     return {"message": "No candidate places found within filters."}
    #
    # candidate_places = filter_places_by_travel_time(candidate_places, location, max_travel_time)
    # if not candidate_places:
    #     print("No activities found for the given location and criteria.")
    #     return {"message": "No candidate places between travel time found within filters."}
    #
    # mealtime_slots = count_mealtimes_in_window(start_time, end_time, {
    #     "lunch": (datetime.strptime("12:00", "%H:%M"), datetime.strptime("14:00", "%H:%M")),
    #     "dinner": (datetime.strptime("18:00", "%H:%M"), datetime.strptime("21:00", "%H:%M"))
    # })
    # # Generate itinerary
    # itinerary = greedy_itinerary_planner(
    #     candidate_places, hotel_location, start_time, end_time, budget, mealtime_slots
    # )
    # build_itinerary_timeline(itinerary)
    # # Convert to JSON
    # itinerary_json = build_itinerary_json(itinerary)
    # return itinerary_json

if __name__ == "__main__":
    initialize_database()
    generate_plan({})
