import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

CITIES = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
PROVIDER_TYPES = ["Restaurant", "Grocery Store", "Supermarket", "Hotel", "Catering Service", "Bakery"]
RECEIVER_TYPES = ["NGO", "Community Center", "Individual", "Orphanage", "Old Age Home", "Food Bank"]
FOOD_NAMES = ["Rice", "Dal", "Chapati", "Biryani", "Bread", "Vegetables", "Fruits", "Idli",
              "Sambar", "Upma", "Poha", "Pulao", "Curry", "Sandwich", "Salad", "Soup",
              "Pasta", "Noodles", "Paratha", "Dosa", "Vada", "Sweets", "Snacks Mix", "Milk"]
FOOD_TYPES = ["Vegetarian", "Non-Vegetarian", "Vegan"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snacks"]
CLAIM_STATUS = ["Completed", "Pending", "Cancelled"]

PROVIDER_NAMES = [
    "Annapoorna Restaurant", "Fresh Mart", "City Superstore", "Grand Hotel", "Spice Garden",
    "Morning Bakery", "Green Grocer", "Royal Catering", "Taste of India", "Quick Bites",
    "Family Kitchen", "Metro Mart", "Sunshine Bakery", "Eastern Flavors", "Western Spices",
    "Heritage Restaurant", "Food Palace", "Organic Basket", "Daily Fresh", "Star Caterers",
    "Delicious Corner", "Healthy Bites", "Southern Kitchen", "Northern Dhaba", "Coastal Foods"
]

RECEIVER_NAMES = [
    "Hope Foundation", "Care NGO", "City Food Bank", "Rainbow Orphanage", "Sunrise Old Age Home",
    "Unity Community Center", "Helping Hands", "Green Earth NGO", "People First", "Joy Foundation",
    "Asha Trust", "Seva NGO", "Light House Center", "Future Hope", "Smile Foundation",
    "Priya Individual", "Rahul Individual", "Meena Individual", "Suresh Individual", "Kavya Individual",
    "Bright Stars Orphanage", "Golden Years Home", "New Life Center", "Peace Foundation", "Share & Care"
]

def random_phone():
    return f"+91-{random.randint(70000,99999)}{random.randint(10000,99999)}"

def random_address(city):
    streets = ["MG Road", "Anna Salai", "Park Street", "Civil Lines", "Gandhi Nagar",
               "Nehru Street", "Rajaji Road", "Market Road", "Station Road", "Lake View"]
    return f"{random.randint(1,200)}, {random.choice(streets)}, {city}"

def random_date_future():
    days = random.randint(1, 30)
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

def random_timestamp_past():
    days = random.randint(0, 90)
    hours = random.randint(0, 23)
    mins = random.randint(0, 59)
    return (datetime.now() - timedelta(days=days, hours=hours, minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")

# ── 1. PROVIDERS (100 rows) ──────────────────────────────────────
providers = []
for i in range(1, 101):
    city = random.choice(CITIES)
    name = random.choice(PROVIDER_NAMES) + f" {random.randint(1,99)}"
    providers.append({
        "Provider_ID": i,
        "Name": name,
        "Type": random.choice(PROVIDER_TYPES),
        "Address": random_address(city),
        "City": city,
        "Contact": random_phone()
    })
df_providers = pd.DataFrame(providers)
df_providers.to_csv("providers_data.csv", index=False)
print(f"Providers: {len(df_providers)} rows")

# ── 2. RECEIVERS (80 rows) ───────────────────────────────────────
receivers = []
for i in range(1, 81):
    city = random.choice(CITIES)
    name = random.choice(RECEIVER_NAMES) + f" {random.randint(1,50)}"
    receivers.append({
        "Receiver_ID": i,
        "Name": name,
        "Type": random.choice(RECEIVER_TYPES),
        "City": city,
        "Contact": random_phone()
    })
df_receivers = pd.DataFrame(receivers)
df_receivers.to_csv("receivers_data.csv", index=False)
print(f"Receivers: {len(df_receivers)} rows")

# ── 3. FOOD LISTINGS (200 rows) ──────────────────────────────────
food_listings = []
for i in range(1, 201):
    provider = random.choice(providers)
    food_listings.append({
        "Food_ID": i,
        "Food_Name": random.choice(FOOD_NAMES),
        "Quantity": random.randint(5, 200),
        "Expiry_Date": random_date_future(),
        "Provider_ID": provider["Provider_ID"],
        "Provider_Type": provider["Type"],
        "Location": provider["City"],
        "Food_Type": random.choice(FOOD_TYPES),
        "Meal_Type": random.choice(MEAL_TYPES)
    })
df_food = pd.DataFrame(food_listings)
df_food.to_csv("food_listings_data.csv", index=False)
print(f"Food Listings: {len(df_food)} rows")

# ── 4. CLAIMS (300 rows) ─────────────────────────────────────────
claims = []
for i in range(1, 301):
    # Weighted status: more completed than others
    status = random.choices(CLAIM_STATUS, weights=[60, 25, 15])[0]
    claims.append({
        "Claim_ID": i,
        "Food_ID": random.randint(1, 200),
        "Receiver_ID": random.randint(1, 80),
        "Status": status,
        "Timestamp": random_timestamp_past()
    })
df_claims = pd.DataFrame(claims)
df_claims.to_csv("claims_data.csv", index=False)
print(f"Claims: {len(df_claims)} rows")

print("\nAll 4 datasets generated successfully!")



