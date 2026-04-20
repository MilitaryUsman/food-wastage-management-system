import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os, sys

# ── path setup ──────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(BASE, "food_wastage.db")

st.set_page_config(
    page_title="Food Wastage Management System",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #1a2e1a; }
  [data-testid="stSidebar"] * { color: #d4edda !important; }
  .metric-card {
    background: #f0faf0; border-left: 4px solid #2d6a2d;
    border-radius: 8px; padding: 16px 20px; margin: 6px 0;
  }
  .section-header {
    background: linear-gradient(135deg, #2d6a2d, #4caf50);
    color: white; padding: 12px 20px; border-radius: 8px;
    font-size: 18px; font-weight: 600; margin-bottom: 16px;
  }
  .stTabs [data-baseweb="tab-list"] { gap: 8px; }
  .stTabs [data-baseweb="tab"] {
    background: #e8f5e9; border-radius: 6px 6px 0 0;
    font-weight: 500; color: #2d6a2d;
  }
  .stTabs [aria-selected="true"] {
    background: #2d6a2d !important; color: white !important;
  }
  div[data-testid="stDataFrame"] { border: 1px solid #c8e6c9; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── DB helpers ───────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def query(sql, params=()):
    return pd.read_sql_query(sql, get_conn(), params=params)

def execute(sql, params=()):
    c = get_conn()
    c.execute(sql, params)
    c.commit()

# ── SIDEBAR ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🥗 Food Wastage\n### Management System")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏠 Dashboard",
        "📋 SQL Queries",
        "🍱 Food Listings",
        "🤝 Providers",
        "👥 Receivers",
        "📦 Claims",
        "➕ CRUD Operations",
        "📊 Analytics & EDA"
    ])
    st.markdown("---")
    cities   = ["All"] + query("SELECT DISTINCT City FROM providers ORDER BY City")["City"].tolist()
    sel_city = st.selectbox("Filter by City", cities)
    st.markdown("---")
    total_p = query("SELECT COUNT(*) as c FROM providers")["c"][0]
    total_r = query("SELECT COUNT(*) as c FROM receivers")["c"][0]
    total_f = query("SELECT COUNT(*) as c FROM food_listings")["c"][0]
    total_c = query("SELECT COUNT(*) as c FROM claims")["c"][0]
    st.metric("Providers", total_p)
    st.metric("Receivers", total_r)
    st.metric("Food Listings", total_f)
    st.metric("Total Claims", total_c)

# ════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown('<div class="section-header">🏠 Local Food Wastage Management System — Dashboard</div>', unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4, k5 = st.columns(5)
    total_qty = query("SELECT SUM(Quantity) as q FROM food_listings")["q"][0]
    comp_pct  = query("SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),1) as p FROM claims WHERE Status='Completed'")["p"][0]
    k1.metric("🏪 Providers",      total_p)
    k2.metric("🤝 Receivers",      total_r)
    k3.metric("🍱 Food Listings",  total_f)
    k4.metric("📦 Total Claims",   total_c)
    k5.metric("✅ Completion Rate", f"{comp_pct}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 Listings by City")
        df = query("SELECT Location as City, COUNT(*) as Listings, SUM(Quantity) as Quantity FROM food_listings GROUP BY Location ORDER BY Listings DESC")
        fig = px.bar(df, x="City", y="Listings", color="Quantity",
                     color_continuous_scale="Greens",
                     template="plotly_white")
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("🍽️ Claim Status Distribution")
        df2 = query("SELECT Status, COUNT(*) as Count FROM claims GROUP BY Status")
        fig2 = px.pie(df2, names="Status", values="Count",
                      color_discrete_sequence=["#4caf50","#ff9800","#f44336"],
                      hole=0.4)
        fig2.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🥦 Food Type Breakdown")
        df3 = query("SELECT Food_Type, COUNT(*) as Count FROM food_listings GROUP BY Food_Type")
        fig3 = px.pie(df3, names="Food_Type", values="Count",
                      color_discrete_sequence=["#388e3c","#66bb6a","#a5d6a7"])
        fig3.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("🍳 Meal Type Demand")
        df4 = query("""
            SELECT f.Meal_Type, COUNT(c.Claim_ID) as Claims
            FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
            GROUP BY f.Meal_Type ORDER BY Claims DESC
        """)
        fig4 = px.bar(df4, x="Meal_Type", y="Claims",
                      color="Meal_Type",
                      color_discrete_sequence=["#1b5e20","#2e7d32","#388e3c","#43a047"],
                      template="plotly_white")
        fig4.update_layout(margin=dict(t=10, b=10), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 2 — SQL QUERIES
# ════════════════════════════════════════════════════════════════
elif page == "📋 SQL Queries":
    st.markdown('<div class="section-header">📋 All 15 SQL Queries & Results</div>', unsafe_allow_html=True)

    QUERIES = {
        1:  ("Providers and Receivers Count per City",
             "SELECT p.City, COUNT(DISTINCT p.Provider_ID) AS Total_Providers, COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers FROM providers p LEFT JOIN receivers r ON p.City=r.City GROUP BY p.City ORDER BY Total_Providers DESC"),
        2:  ("Provider Type Contributing the Most Food",
             "SELECT p.Type AS Provider_Type, COUNT(f.Food_ID) AS Total_Listings, SUM(f.Quantity) AS Total_Quantity FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Type ORDER BY Total_Quantity DESC"),
        3:  ("Contact Information of Providers by City",
             "SELECT City, Name, Type, Contact, Address FROM providers ORDER BY City, Name"),
        4:  ("Receivers Who Claimed the Most Food",
             "SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS Total_Claims FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID ORDER BY Total_Claims DESC LIMIT 10"),
        5:  ("Total Quantity of Food Available",
             "SELECT SUM(Quantity) AS Total_Food_Available, COUNT(Food_ID) AS Total_Listings, ROUND(AVG(Quantity),2) AS Avg_Quantity FROM food_listings"),
        6:  ("City with Highest Number of Food Listings",
             "SELECT Location AS City, COUNT(Food_ID) AS Total_Listings, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC"),
        7:  ("Most Commonly Available Food Types",
             "SELECT Food_Type, COUNT(Food_ID) AS Total_Listings, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Food_Type ORDER BY Total_Listings DESC"),
        8:  ("Number of Claims per Food Item",
             "SELECT f.Food_Name, f.Food_Type, f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_ID ORDER BY Total_Claims DESC LIMIT 15"),
        9:  ("Provider with Highest Successful Claims",
             "SELECT p.Name, p.Type, p.City, COUNT(c.Claim_ID) AS Successful_Claims FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID JOIN claims c ON f.Food_ID=c.Food_ID WHERE c.Status='Completed' GROUP BY p.Provider_ID ORDER BY Successful_Claims DESC LIMIT 10"),
        10: ("Claim Status: Completed vs Pending vs Cancelled",
             "SELECT Status, COUNT(*) AS Count, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),2) AS Percentage FROM claims GROUP BY Status ORDER BY Count DESC"),
        11: ("Average Quantity Claimed per Receiver",
             "SELECT r.Name, r.Type, COUNT(c.Claim_ID) AS Total_Claims, ROUND(AVG(f.Quantity),2) AS Avg_Quantity FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID JOIN food_listings f ON c.Food_ID=f.Food_ID GROUP BY r.Receiver_ID ORDER BY Avg_Quantity DESC LIMIT 10"),
        12: ("Most Claimed Meal Type",
             "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims, SUM(f.Quantity) AS Total_Quantity FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY Total_Claims DESC"),
        13: ("Total Quantity Donated by Each Provider",
             "SELECT p.Name, p.Type, p.City, COUNT(f.Food_ID) AS Listings, SUM(f.Quantity) AS Total_Donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY Total_Donated DESC LIMIT 15"),
        14: ("Food Listings Expiring Within 7 Days",
             "SELECT f.Food_Name, f.Quantity, f.Expiry_Date, f.Location, p.Name AS Provider, p.Contact FROM food_listings f JOIN providers p ON f.Provider_ID=p.Provider_ID WHERE DATE(f.Expiry_Date)<=DATE('now','+7 days') ORDER BY f.Expiry_Date"),
        15: ("Monthly Trend of Food Claims",
             "SELECT STRFTIME('%Y-%m', Timestamp) AS Month, COUNT(*) AS Total_Claims, SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS Completed, SUM(CASE WHEN Status='Pending' THEN 1 ELSE 0 END) AS Pending, SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled FROM claims GROUP BY Month ORDER BY Month DESC"),
    }

    selected = st.selectbox("Select Query", [f"Q{n}: {t}" for n,(t,_) in QUERIES.items()])
    qnum = int(selected.split(":")[0][1:])
    title, sql = QUERIES[qnum]

    st.markdown(f"**{title}**")
    with st.expander("View SQL"):
        st.code(sql, language="sql")

    df = query(sql)
    st.dataframe(df, use_container_width=True)
    st.caption(f"{len(df)} rows returned")

    st.markdown("---")
    st.subheader("Run All 15 Queries")
    if st.button("▶ Run All & Show Summary"):
        for n, (t, s) in QUERIES.items():
            with st.expander(f"Q{n}: {t}"):
                st.dataframe(query(s), use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 3 — FOOD LISTINGS
# ════════════════════════════════════════════════════════════════
elif page == "🍱 Food Listings":
    st.markdown('<div class="section-header">🍱 Food Listings</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    cities_list   = ["All"] + query("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"].tolist()
    ft_list       = ["All"] + query("SELECT DISTINCT Food_Type FROM food_listings ORDER BY Food_Type")["Food_Type"].tolist()
    mt_list       = ["All"] + query("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type")["Meal_Type"].tolist()
    pt_list       = ["All"] + query("SELECT DISTINCT Provider_Type FROM food_listings ORDER BY Provider_Type")["Provider_Type"].tolist()

    f_city = c1.selectbox("City",          cities_list)
    f_ft   = c2.selectbox("Food Type",     ft_list)
    f_mt   = c3.selectbox("Meal Type",     mt_list)
    f_pt   = c4.selectbox("Provider Type", pt_list)

    sql = "SELECT * FROM food_listings WHERE 1=1"
    params = []
    if f_city != "All": sql += " AND Location=?";       params.append(f_city)
    if f_ft   != "All": sql += " AND Food_Type=?";      params.append(f_ft)
    if f_mt   != "All": sql += " AND Meal_Type=?";      params.append(f_mt)
    if f_pt   != "All": sql += " AND Provider_Type=?";  params.append(f_pt)

    df = query(sql, params)
    st.info(f"Showing {len(df)} listings")
    st.dataframe(df, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 4 — PROVIDERS
# ════════════════════════════════════════════════════════════════
elif page == "🤝 Providers":
    st.markdown('<div class="section-header">🤝 Food Providers</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cities_p = ["All"] + query("SELECT DISTINCT City FROM providers ORDER BY City")["City"].tolist()
    types_p  = ["All"] + query("SELECT DISTINCT Type FROM providers ORDER BY Type")["Type"].tolist()
    f_city = c1.selectbox("City",          cities_p)
    f_type = c2.selectbox("Provider Type", types_p)

    sql = "SELECT * FROM providers WHERE 1=1"
    params = []
    if f_city != "All": sql += " AND City=?"; params.append(f_city)
    if f_type != "All": sql += " AND Type=?"; params.append(f_type)

    df = query(sql, params)
    st.info(f"Showing {len(df)} providers")
    st.dataframe(df, use_container_width=True)

    st.subheader("Provider Contributions")
    df2 = query("SELECT p.Name, p.City, SUM(f.Quantity) as Total FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY Total DESC LIMIT 15")
    fig = px.bar(df2, x="Name", y="Total", color="City", template="plotly_white",
                 color_discrete_sequence=px.colors.sequential.Greens_r)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 5 — RECEIVERS
# ════════════════════════════════════════════════════════════════
elif page == "👥 Receivers":
    st.markdown('<div class="section-header">👥 Food Receivers</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    cities_r = ["All"] + query("SELECT DISTINCT City FROM receivers ORDER BY City")["City"].tolist()
    types_r  = ["All"] + query("SELECT DISTINCT Type FROM receivers ORDER BY Type")["Type"].tolist()
    f_city = c1.selectbox("City",          cities_r)
    f_type = c2.selectbox("Receiver Type", types_r)

    sql = "SELECT * FROM receivers WHERE 1=1"
    params = []
    if f_city != "All": sql += " AND City=?"; params.append(f_city)
    if f_type != "All": sql += " AND Type=?"; params.append(f_type)

    df = query(sql, params)
    st.info(f"Showing {len(df)} receivers")
    st.dataframe(df, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 6 — CLAIMS
# ════════════════════════════════════════════════════════════════
elif page == "📦 Claims":
    st.markdown('<div class="section-header">📦 Food Claims</div>', unsafe_allow_html=True)

    status_list = ["All", "Completed", "Pending", "Cancelled"]
    f_status = st.selectbox("Filter by Status", status_list)

    sql = """
        SELECT c.Claim_ID, f.Food_Name, r.Name AS Receiver, r.City,
               c.Status, c.Timestamp
        FROM claims c
        JOIN food_listings f ON c.Food_ID=f.Food_ID
        JOIN receivers r ON c.Receiver_ID=r.Receiver_ID
        WHERE 1=1
    """
    params = []
    if f_status != "All":
        sql += " AND c.Status=?"
        params.append(f_status)
    sql += " ORDER BY c.Timestamp DESC"

    df = query(sql, params)
    st.info(f"Showing {len(df)} claims")
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        df2 = query("SELECT Status, COUNT(*) as Count FROM claims GROUP BY Status")
        fig = px.pie(df2, names="Status", values="Count",
                     color_discrete_sequence=["#4caf50","#ff9800","#f44336"], hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        df3 = query("SELECT STRFTIME('%Y-%m', Timestamp) AS Month, COUNT(*) AS Claims FROM claims GROUP BY Month ORDER BY Month")
        fig2 = px.line(df3, x="Month", y="Claims", markers=True,
                       color_discrete_sequence=["#2d6a2d"], template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# PAGE 7 — CRUD OPERATIONS
# ════════════════════════════════════════════════════════════════
elif page == "➕ CRUD Operations":
    st.markdown('<div class="section-header">➕ CRUD Operations</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Food Listing", "✏️ Update Listing", "🗑️ Delete Listing", "📝 Manage Claims"])

    # ADD
    with tab1:
        st.subheader("Add New Food Listing")
        c1, c2 = st.columns(2)
        food_name   = c1.text_input("Food Name")
        quantity    = c2.number_input("Quantity", min_value=1, value=10)
        expiry      = c1.date_input("Expiry Date")
        food_type   = c2.selectbox("Food Type",   ["Vegetarian","Non-Vegetarian","Vegan"])
        meal_type   = c1.selectbox("Meal Type",   ["Breakfast","Lunch","Dinner","Snacks"])
        location    = c2.selectbox("Location",    query("SELECT DISTINCT City FROM providers ORDER BY City")["City"].tolist())
        provider_df = query("SELECT Provider_ID, Name FROM providers ORDER BY Name")
        provider    = c1.selectbox("Provider", provider_df["Name"].tolist())
        prov_id     = int(provider_df[provider_df["Name"]==provider]["Provider_ID"].values[0])
        prov_type   = query("SELECT Type FROM providers WHERE Provider_ID=?", (prov_id,))["Type"].values[0]

        if st.button("✅ Add Food Listing"):
            if food_name:
                max_id = query("SELECT COALESCE(MAX(Food_ID),0)+1 as nid FROM food_listings")["nid"][0]
                execute("""INSERT INTO food_listings VALUES (?,?,?,?,?,?,?,?,?)""",
                        (int(max_id), food_name, int(quantity), str(expiry),
                         prov_id, prov_type, location, food_type, meal_type))
                st.success(f"✅ '{food_name}' added successfully!")
                st.cache_resource.clear()
            else:
                st.warning("Please enter food name.")

    # UPDATE
    with tab2:
        st.subheader("Update Food Listing Quantity")
        food_ids = query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
        opts     = food_ids.apply(lambda r: f"ID {r['Food_ID']} — {r['Food_Name']}", axis=1).tolist()
        sel      = st.selectbox("Select Food Item", opts)
        fid      = int(sel.split("—")[0].replace("ID","").strip())
        new_qty  = st.number_input("New Quantity", min_value=1, value=10)
        if st.button("✅ Update Quantity"):
            execute("UPDATE food_listings SET Quantity=? WHERE Food_ID=?", (int(new_qty), fid))
            st.success("Quantity updated!")
            st.cache_resource.clear()

    # DELETE
    with tab3:
        st.subheader("Delete Food Listing")
        food_ids2 = query("SELECT Food_ID, Food_Name, Location FROM food_listings ORDER BY Food_ID")
        opts2     = food_ids2.apply(lambda r: f"ID {r['Food_ID']} — {r['Food_Name']} ({r['Location']})", axis=1).tolist()
        sel2      = st.selectbox("Select Food Item to Delete", opts2)
        fid2      = int(sel2.split("—")[0].replace("ID","").strip())
        st.warning("⚠️ This will also delete all related claims.")
        if st.button("🗑️ Delete Listing"):
            execute("DELETE FROM claims WHERE Food_ID=?",       (fid2,))
            execute("DELETE FROM food_listings WHERE Food_ID=?", (fid2,))
            st.success("Listing deleted.")
            st.cache_resource.clear()

    # CLAIMS MANAGEMENT
    with tab4:
        st.subheader("Add New Claim")
        c1, c2 = st.columns(2)
        food_opts = query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_Name")
        recv_opts = query("SELECT Receiver_ID, Name FROM receivers ORDER BY Name")
        sel_food  = c1.selectbox("Food Item", food_opts.apply(lambda r: f"{r['Food_ID']} — {r['Food_Name']}", axis=1).tolist())
        sel_recv  = c2.selectbox("Receiver",  recv_opts.apply(lambda r: f"{r['Receiver_ID']} — {r['Name']}", axis=1).tolist())
        status    = c1.selectbox("Status", ["Pending","Completed","Cancelled"])
        fid3  = int(sel_food.split("—")[0].strip())
        rid3  = int(sel_recv.split("—")[0].strip())
        if st.button("✅ Add Claim"):
            max_cid = query("SELECT COALESCE(MAX(Claim_ID),0)+1 as nid FROM claims")["nid"][0]
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            execute("INSERT INTO claims VALUES (?,?,?,?,?)", (int(max_cid), fid3, rid3, status, ts))
            st.success("Claim added!")
            st.cache_resource.clear()

        st.markdown("---")
        st.subheader("Update Claim Status")
        claims_df = query("SELECT c.Claim_ID, f.Food_Name, r.Name, c.Status FROM claims c JOIN food_listings f ON c.Food_ID=f.Food_ID JOIN receivers r ON c.Receiver_ID=r.Receiver_ID ORDER BY c.Claim_ID DESC LIMIT 50")
        st.dataframe(claims_df, use_container_width=True)
        cid_sel    = st.number_input("Claim ID to Update", min_value=1, value=1)
        new_status = st.selectbox("New Status", ["Completed","Pending","Cancelled"])
        if st.button("✅ Update Claim Status"):
            execute("UPDATE claims SET Status=? WHERE Claim_ID=?", (new_status, int(cid_sel)))
            st.success("Status updated!")
            st.cache_resource.clear()

# ════════════════════════════════════════════════════════════════
# PAGE 8 — EDA & ANALYTICS
# ════════════════════════════════════════════════════════════════
elif page == "📊 Analytics & EDA":
    st.markdown('<div class="section-header">📊 Exploratory Data Analysis & Insights</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🗺️ Location Analysis", "🍽️ Food Analysis", "📈 Claims Trends"])

    with tab1:
        st.subheader("Providers and Receivers per City")
        df = query("""
            SELECT p.City,
                   COUNT(DISTINCT p.Provider_ID) AS Providers,
                   COUNT(DISTINCT r.Receiver_ID) AS Receivers
            FROM providers p
            LEFT JOIN receivers r ON p.City=r.City
            GROUP BY p.City ORDER BY Providers DESC
        """)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Providers", x=df["City"], y=df["Providers"], marker_color="#2d6a2d"))
        fig.add_trace(go.Bar(name="Receivers", x=df["City"], y=df["Receivers"], marker_color="#81c784"))
        fig.update_layout(barmode="group", template="plotly_white", title="Providers vs Receivers by City")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Total Food Quantity Available by City")
        df2 = query("SELECT Location as City, SUM(Quantity) as Total_Qty FROM food_listings GROUP BY Location ORDER BY Total_Qty DESC")
        fig2 = px.bar(df2, x="City", y="Total_Qty", color="Total_Qty",
                      color_continuous_scale="Greens", template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Food Type Distribution")
            df3 = query("SELECT Food_Type, COUNT(*) as Count, SUM(Quantity) as Total FROM food_listings GROUP BY Food_Type")
            fig3 = px.pie(df3, names="Food_Type", values="Count",
                          color_discrete_sequence=["#1b5e20","#4caf50","#a5d6a7"])
            st.plotly_chart(fig3, use_container_width=True)

        with c2:
            st.subheader("Meal Type Distribution")
            df4 = query("SELECT Meal_Type, COUNT(*) as Count FROM food_listings GROUP BY Meal_Type")
            fig4 = px.bar(df4, x="Meal_Type", y="Count",
                          color="Meal_Type",
                          color_discrete_sequence=["#1b5e20","#2e7d32","#388e3c","#43a047"],
                          template="plotly_white")
            st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Top 10 Most Listed Food Items")
        df5 = query("SELECT Food_Name, COUNT(*) as Listings, SUM(Quantity) as Total_Qty FROM food_listings GROUP BY Food_Name ORDER BY Listings DESC LIMIT 10")
        fig5 = px.bar(df5, x="Food_Name", y="Total_Qty", color="Listings",
                      color_continuous_scale="Greens", template="plotly_white")
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("Provider Type vs Food Quantity")
        df6 = query("SELECT p.Type, SUM(f.Quantity) as Total FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Type ORDER BY Total DESC")
        fig6 = px.bar(df6, x="Type", y="Total", color="Total",
                      color_continuous_scale="Greens", template="plotly_white")
        st.plotly_chart(fig6, use_container_width=True)

    with tab3:
        st.subheader("Monthly Claims Trend")
        df7 = query("SELECT STRFTIME('%Y-%m', Timestamp) AS Month, COUNT(*) AS Total, SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS Completed, SUM(CASE WHEN Status='Pending' THEN 1 ELSE 0 END) AS Pending, SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled FROM claims GROUP BY Month ORDER BY Month")
        fig7 = go.Figure()
        fig7.add_trace(go.Scatter(x=df7["Month"], y=df7["Completed"], name="Completed", line=dict(color="#4caf50"), mode="lines+markers"))
        fig7.add_trace(go.Scatter(x=df7["Month"], y=df7["Pending"],   name="Pending",   line=dict(color="#ff9800"), mode="lines+markers"))
        fig7.add_trace(go.Scatter(x=df7["Month"], y=df7["Cancelled"], name="Cancelled", line=dict(color="#f44336"), mode="lines+markers"))
        fig7.update_layout(template="plotly_white", title="Claims by Status Over Time")
        st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Top 10 Receivers by Claims")
        df8 = query("SELECT r.Name, r.Type, COUNT(c.Claim_ID) as Claims FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID ORDER BY Claims DESC LIMIT 10")
        fig8 = px.bar(df8, x="Name", y="Claims", color="Type", template="plotly_white",
                      color_discrete_sequence=["#1b5e20","#2e7d32","#388e3c","#43a047","#4caf50","#66bb6a"])
        fig8.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig8, use_container_width=True)

        st.subheader("Claim Completion Rate by Receiver Type")
        df9 = query("""
            SELECT r.Type,
                   ROUND(SUM(CASE WHEN c.Status='Completed' THEN 1.0 ELSE 0 END)*100/COUNT(*),1) AS Completion_Rate
            FROM receivers r
            JOIN claims c ON r.Receiver_ID=c.Receiver_ID
            GROUP BY r.Type ORDER BY Completion_Rate DESC
        """)
        fig9 = px.bar(df9, x="Type", y="Completion_Rate",
                      color="Completion_Rate", color_continuous_scale="Greens",
                      template="plotly_white", text="Completion_Rate")
        fig9.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig9, use_container_width=True)
