import sqlite3

def create_itineraries_db(db_name="itineraries.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS itineraries (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         location TEXT NOT NULL,
    #         duration_days INTEGER NOT NULL,
    #         duration_nights INTEGER NOT NULL
    #     )
    # ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS itinerary_activities (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         itinerary_id INTEGER NOT NULL,
    #         day INTEGER NOT NULL,
    #         time TEXT,
    #         location TEXT NOT NULL,
    #         activity TEXT NOT NULL,
    #         activity_desc TEXT,
    #         cuisine TEXT,
    #         avg_cost_per_person TEXT,
    #         FOREIGN KEY (itinerary_id) REFERENCES itineraries(id)
    #     )
    # ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            latitude TEXT,
            longitude TEXT,
            avg_cost_per_person INTEGER,
            duration INTEGER,
            service_type TEXT NOT NULL,
            info TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created with 'activities' tables.")

create_itineraries_db()