import json

def filter_star_restaurants(input_file, output_file):
    """
    This file works for restaurants data needed in app.py.get_nearby_restaurant_list() : (POST "/api/restaurant/nearby")
    - input file: places_restaurants.json (cached data in places.db)
    - output file: diff_star_restaurants.json
    """
    with open(input_file, 'r', encoding="utf-8") as f:
        data = json.load(f)

    # 3 strars / rating < 4
    # diff_star_restaurants = [restaurant
    #                          for restaurant in data
    #                          if restaurant.get("rating") is not None and float(restaurant.get("rating", 0)) < 4.0]

    # 4 strars / 5 > rating >=4
    # diff_star_restaurants = [restaurant
    #                          for restaurant in data
    #                          if restaurant.get("rating") is not None
    #                          and float(restaurant.get("rating", 0)) < 5.0 and float(restaurant.get("rating", 0)) >= 4.0]

    # 4 strars / 5 > rating >=4
    diff_star_restaurants = [restaurant
                             for restaurant in data
                             if restaurant.get("rating") is not None and float(restaurant.get("rating", 0)) >= 5.0]
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(diff_star_restaurants, f, ensure_ascii=False, indent=4)

input_file = "data/cached_datasets/places_restaurants.json"
output_file = "data/cached_datasets/5star_restaurants.json"

filter_star_restaurants(input_file, output_file)
