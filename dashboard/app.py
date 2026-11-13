from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Delivery Performance Audit", layout="wide")

DATA_DIR = Path(__file__).parent
STATUS_ORDER = ["On Time", "Late", "Super Late"]
STATUS_COLORS = ["#2e7d32", "#f9a825", "#c62828"]


@st.cache_data
def load_data():
    orders = pd.read_csv(DATA_DIR / "orders.csv.gz")
    categories = pd.read_csv(DATA_DIR / "categories.csv")
    orders["Delay_Days"] = -orders["Days_Difference"]
    orders["bad_review"] = orders["review_score"] <= 2
    return orders, categories


orders, categories = load_data()

# ---------------- Title ----------------
st.title("Delivery Performance Audit")
st.write(
    "Veridi Logistics delivery data (Olist, Brazil, 2016-2018). "
    "Use the filters on the left to look at one region or state."
)

# ---------------- Filters ----------------
st.sidebar.header("Filters")
all_regions = sorted(orders["region"].unique())
regions = st.sidebar.multiselect("Region", all_regions, default=all_regions)

states_in_regions = sorted(orders.loc[orders["region"].isin(regions), "customer_state"].unique())
states = st.sidebar.multiselect("State", states_in_regions, default=states_in_regions)

data = orders[orders["region"].isin(regions) & orders["customer_state"].isin(states)]

if data.empty:
    st.warning("No orders match these filters. Pick at least one region and state.")
    st.stop()

national_late_pct = orders["is_late"].mean() * 100

# ---------------- KPIs ----------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Delivered orders", f"{len(data):,}")
col2.metric("% late", f"{data['is_late'].mean() * 100:.1f}%")
col3.metric("% super late (>5 days)", f"{(data['Delivery_Status'] == 'Super Late').mean() * 100:.1f}%")
col4.metric("Average review", f"{data['review_score'].mean():.2f} / 5")
col5.metric("Median days early", f"{data['Days_Difference'].median():.0f}")

st.divider()

# ---------------- Story 3: states ----------------
st.header("Which states have the most late deliveries?")
st.write("Bars are coloured by region. The dashed line is the national average.")

by_state = data.groupby(["customer_state", "region"]).agg(
    orders=("is_late", "size"),
    late_pct=("is_late", "mean"),
    avg_review=("review_score", "mean"),
).reset_index()
by_state["late_pct"] = by_state["late_pct"] * 100

state_bars = alt.Chart(by_state).mark_bar().encode(
    x=alt.X("customer_state:N", sort="-y", title="State"),
    y=alt.Y("late_pct:Q", title="% late"),
    color=alt.Color("region:N", title="Region"),
    tooltip=[
        alt.Tooltip("customer_state", title="State"),
        alt.Tooltip("region", title="Region"),
        alt.Tooltip("orders", title="Orders", format=","),
        alt.Tooltip("late_pct", title="% late", format=".1f"),
        alt.Tooltip("avg_review", title="Avg review", format=".2f"),
    ],
)
national_line = alt.Chart(pd.DataFrame({"y": [national_late_pct]})).mark_rule(
    strokeDash=[6, 4], color="black"
).encode(y="y:Q")
st.altair_chart(state_bars + national_line, width="stretch")

by_region = data.groupby("region").agg(
    orders=("is_late", "size"),
    late_pct=("is_late", "mean"),
    avg_review=("review_score", "mean"),
).reset_index()
by_region["late_pct"] = (by_region["late_pct"] * 100).round(1)
by_region["avg_review"] = by_region["avg_review"].round(2)
by_region = by_region.sort_values("late_pct", ascending=False)
by_region.columns = ["Region", "Orders", "% late", "Avg review"]
st.dataframe(by_region, hide_index=True, width="stretch")

st.divider()

# ---------------- Story 4: reviews ----------------
st.header("Do late deliveries cause bad reviews?")

by_status = data.groupby("Delivery_Status").agg(
    avg_review=("review_score", "mean"),
    bad_pct=("bad_review", "mean"),
    orders=("is_late", "size"),
).reindex(STATUS_ORDER).dropna().reset_index()
by_status["bad_pct"] = by_status["bad_pct"] * 100

status_color = alt.Color(
    "Delivery_Status:N",
    scale=alt.Scale(domain=STATUS_ORDER, range=STATUS_COLORS),
    legend=None,
)

left, right = st.columns(2)

with left:
    st.subheader("Average review score")
    base = alt.Chart(by_status).encode(
        x=alt.X("Delivery_Status:N", sort=STATUS_ORDER, title=None),
        y=alt.Y("avg_review:Q", title="Average review (1-5)", scale=alt.Scale(domain=[0, 5])),
    )
    bars = base.mark_bar().encode(color=status_color)
    labels = base.mark_text(dy=-8).encode(text=alt.Text("avg_review:Q", format=".2f"))
    st.altair_chart(bars + labels, width="stretch")

with right:
    st.subheader("% of 1-2 star reviews")
    base = alt.Chart(by_status).encode(
        x=alt.X("Delivery_Status:N", sort=STATUS_ORDER, title=None),
        y=alt.Y("bad_pct:Q", title="% bad reviews"),
    )
    bars = base.mark_bar().encode(color=status_color)
    labels = base.mark_text(dy=-8).encode(text=alt.Text("bad_pct:Q", format=".1f"))
    st.altair_chart(bars + labels, width="stretch")

st.subheader("Delivery delay vs average review score")
st.write("Negative days mean the order came early. Only days with at least 30 orders are shown.")

by_delay = data.groupby("Delay_Days").agg(
    avg_review=("review_score", "mean"),
    orders=("is_late", "size"),
).reset_index()
by_delay = by_delay[(by_delay["orders"] >= 30) & by_delay["Delay_Days"].between(-30, 30)]

delay_line = alt.Chart(by_delay).mark_line(point=True).encode(
    x=alt.X("Delay_Days:Q", title="Delivery delay in days (negative = early)"),
    y=alt.Y("avg_review:Q", title="Average review (1-5)", scale=alt.Scale(domain=[1, 5])),
    tooltip=[
        alt.Tooltip("Delay_Days", title="Days late"),
        alt.Tooltip("avg_review", title="Avg review", format=".2f"),
        alt.Tooltip("orders", title="Orders", format=","),
    ],
)
promised_line = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(strokeDash=[6, 4], color="red").encode(x="x:Q")
st.altair_chart(delay_line + promised_line, width="stretch")

st.divider()

# ---------------- Candidate's choice: monthly trend ----------------
st.header("Monthly trend: late orders vs review score")
st.write("Bars show the % of late orders and the line shows the average review. Months with fewer than 100 orders are hidden.")

monthly = data.groupby("month").agg(
    orders=("is_late", "size"),
    late_pct=("is_late", "mean"),
    avg_review=("review_score", "mean"),
).reset_index()
monthly["late_pct"] = monthly["late_pct"] * 100
monthly = monthly[monthly["orders"] >= 100]

if monthly.empty:
    st.info("Not enough orders per month for this selection.")
else:
    base = alt.Chart(monthly).encode(x=alt.X("month:N", title="Month"))
    late_bars = base.mark_bar(color="#f9a825").encode(y=alt.Y("late_pct:Q", title="% late"))
    review_line = base.mark_line(point=True, color="#1565c0").encode(
        y=alt.Y("avg_review:Q", title="Average review", scale=alt.Scale(zero=False))
    )
    st.altair_chart(
        alt.layer(late_bars, review_line).resolve_scale(y="independent"),
        width="stretch",
    )

st.divider()

# ---------------- Bonus: categories ----------------
st.header("Which product categories are late most often?")
st.write("Whole country, categories with at least 300 orders. Category names are translated to English.")

top_n = st.slider("Number of categories to show", 5, 30, 15)
top_categories = categories.sort_values("late_pct", ascending=False).head(top_n)

category_bars = alt.Chart(top_categories).mark_bar(color="#1565c0").encode(
    x=alt.X("late_pct:Q", title="% late"),
    y=alt.Y("category:N", sort="-x", title=None),
    tooltip=[
        alt.Tooltip("category", title="Category"),
        alt.Tooltip("orders", title="Orders", format=","),
        alt.Tooltip("late_pct", title="% late", format=".1f"),
        alt.Tooltip("avg_review", title="Avg review", format=".2f"),
    ],
)
category_avg_line = alt.Chart(pd.DataFrame({"x": [national_late_pct]})).mark_rule(
    strokeDash=[6, 4], color="black"
).encode(x="x:Q")
st.altair_chart(category_bars + category_avg_line, width="stretch")

st.divider()

# ---------------- Findings ----------------
st.header("Key findings")
st.markdown(
    """
- **Late orders get much worse reviews.** On time orders average about 4.3 stars, late orders about 3.0, and super late orders about 1.7.
- **It is a regional problem, not a nationwide one.** The Northeast has about double the late rate of the South, and Alagoas, Maranhão and Sergipe are the worst states.
- **Remote states are hit harder, but distance is not the whole story.** Every Northeast state and the North as a whole are above average, yet far-off Amazonas and Rondônia are among the best states.
- **Most estimates are too long, not too short.** We promise about 23 days and deliver in about 12, but late orders spiked in early 2018 and reviews dropped at the same time.
"""
)
