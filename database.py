import sqlite3
import pandas as pd
import os
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "food_wastage.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT NOT NULL,
        Address       TEXT,
        City          TEXT NOT NULL,
        Contact       TEXT
    );

    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID   INTEGER PRIMARY KEY,
        Name          TEXT NOT NULL,
        Type          TEXT NOT NULL,
        City          TEXT NOT NULL,
        Contact       TEXT
    );

    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID       INTEGER PRIMARY KEY,
        Food_Name     TEXT NOT NULL,
        Quantity      INTEGER NOT NULL,
        Expiry_Date   TEXT,
        Provider_ID   INTEGER,
        Provider_Type TEXT,
        Location      TEXT,
        Food_Type     TEXT,
        Meal_Type     TEXT,
        FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
    );

    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID      INTEGER PRIMARY KEY,
        Food_ID       INTEGER,
        Receiver_ID   INTEGER,
        Status        TEXT,
        Timestamp     TEXT,
        FOREIGN KEY (Food_ID)     REFERENCES food_listings(Food_ID),
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
    );
    """)
    conn.commit()
    conn.close()
    print("Tables created.")

def load_data():
    conn = get_connection()

    pd.read_csv("providers_data.csv").to_sql("providers", conn, if_exists="replace", index=False)
    pd.read_csv("receivers_data.csv").to_sql("receivers", conn, if_exists="replace", index=False)
    pd.read_csv("food_listings_data.csv").to_sql("food_listings", conn, if_exists="replace", index=False)
    pd.read_csv("claims_data.csv").to_sql("claims", conn, if_exists="replace", index=False)

    conn.close()
    print("Data loaded into database.")

# ═══════════════════════════════════════════════════════════════
# ALL 15 SQL QUERIES
# ═══════════════════════════════════════════════════════════════

QUERIES = {
    1: {
        "title": "Providers and Receivers Count per City",
        "sql": """
            SELECT p.City,
                   COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
                   COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
            FROM providers p
            LEFT JOIN receivers r ON p.City = r.City
            GROUP BY p.City
            ORDER BY Total_Providers DESC
        """
    },
    2: {
        "title": "Provider Type Contributing the Most Food",
        "sql": """
            SELECT p.Type AS Provider_Type,
                   COUNT(f.Food_ID)    AS Total_Listings,
                   SUM(f.Quantity)     AS Total_Quantity
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Type
            ORDER BY Total_Quantity DESC
        """
    },
    3: {
        "title": "Contact Information of Food Providers by City",
        "sql": """
            SELECT City, Name, Type, Contact, Address
            FROM providers
            ORDER BY City, Name
        """
    },
    4: {
        "title": "Receivers Who Claimed the Most Food",
        "sql": """
            SELECT r.Name AS Receiver_Name,
                   r.Type AS Receiver_Type,
                   r.City,
                   COUNT(c.Claim_ID) AS Total_Claims
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID
            ORDER BY Total_Claims DESC
            LIMIT 10
        """
    },
    5: {
        "title": "Total Quantity of Food Available from All Providers",
        "sql": """
            SELECT SUM(Quantity) AS Total_Food_Available,
                   COUNT(Food_ID) AS Total_Listings,
                   ROUND(AVG(Quantity), 2) AS Avg_Quantity_Per_Listing
            FROM food_listings
        """
    },
    6: {
        "title": "City with the Highest Number of Food Listings",
        "sql": """
            SELECT Location AS City,
                   COUNT(Food_ID)   AS Total_Listings,
                   SUM(Quantity)    AS Total_Quantity
            FROM food_listings
            GROUP BY Location
            ORDER BY Total_Listings DESC
        """
    },
    7: {
        "title": "Most Commonly Available Food Types",
        "sql": """
            SELECT Food_Type,
                   COUNT(Food_ID)  AS Total_Listings,
                   SUM(Quantity)   AS Total_Quantity
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Total_Listings DESC
        """
    },
    8: {
        "title": "Number of Food Claims Made per Food Item",
        "sql": """
            SELECT f.Food_Name,
                   f.Food_Type,
                   f.Meal_Type,
                   COUNT(c.Claim_ID)  AS Total_Claims
            FROM food_listings f
            LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_ID
            ORDER BY Total_Claims DESC
            LIMIT 15
        """
    },
    9: {
        "title": "Provider with the Highest Number of Successful Claims",
        "sql": """
            SELECT p.Name AS Provider_Name,
                   p.Type AS Provider_Type,
                   p.City,
                   COUNT(c.Claim_ID) AS Successful_Claims
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID
            ORDER BY Successful_Claims DESC
            LIMIT 10
        """
    },
    10: {
        "title": "Percentage of Claims: Completed vs Pending vs Cancelled",
        "sql": """
            SELECT Status,
                   COUNT(*) AS Count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims
            GROUP BY Status
            ORDER BY Count DESC
        """
    },
    11: {
        "title": "Average Quantity of Food Claimed per Receiver",
        "sql": """
            SELECT r.Name AS Receiver_Name,
                   r.Type AS Receiver_Type,
                   COUNT(c.Claim_ID)          AS Total_Claims,
                   ROUND(AVG(f.Quantity), 2)  AS Avg_Quantity_Claimed
            FROM receivers r
            JOIN claims c     ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings f ON c.Food_ID  = f.Food_ID
            GROUP BY r.Receiver_ID
            ORDER BY Avg_Quantity_Claimed DESC
            LIMIT 10
        """
    },
    12: {
        "title": "Most Claimed Meal Type",
        "sql": """
            SELECT f.Meal_Type,
                   COUNT(c.Claim_ID)  AS Total_Claims,
                   SUM(f.Quantity)    AS Total_Quantity
            FROM food_listings f
            JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC
        """
    },
    13: {
        "title": "Total Quantity of Food Donated by Each Provider",
        "sql": """
            SELECT p.Name AS Provider_Name,
                   p.Type AS Provider_Type,
                   p.City,
                   COUNT(f.Food_ID)  AS Total_Listings,
                   SUM(f.Quantity)   AS Total_Quantity_Donated
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID
            ORDER BY Total_Quantity_Donated DESC
            LIMIT 15
        """
    },
    14: {
        "title": "Food Listings Expiring Within the Next 7 Days",
        "sql": """
            SELECT f.Food_Name,
                   f.Quantity,
                   f.Expiry_Date,
                   f.Location,
                   f.Food_Type,
                   p.Name    AS Provider_Name,
                   p.Contact AS Provider_Contact
            FROM food_listings f
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            WHERE DATE(f.Expiry_Date) <= DATE('now', '+7 days')
            ORDER BY f.Expiry_Date ASC
        """
    },
    15: {
        "title": "Monthly Trend of Food Claims",
        "sql": """
            SELECT STRFTIME('%Y-%m', Timestamp) AS Month,
                   COUNT(*)                     AS Total_Claims,
                   SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS Completed,
                   SUM(CASE WHEN Status='Pending'   THEN 1 ELSE 0 END) AS Pending,
                   SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled
            FROM claims
            GROUP BY Month
            ORDER BY Month DESC
        """
    }
}

def run_all_queries():
    conn = get_connection()
    print("\n" + "="*60)
    print("RUNNING ALL 15 SQL QUERIES")
    print("="*60)
    for num, q in QUERIES.items():
        print(f"\nQ{num}: {q['title']}")
        print("-"*50)
        df = pd.read_sql_query(q["sql"], conn)
        print(df.to_string(index=False))
    conn.close()

if __name__ == "__main__":
    create_tables()
    load_data()
    run_all_queries()
