#!/usr/bin/env python
# coding: utf-8

import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
	page_title="Netflix Insights",
	page_icon="N",
	layout="wide",
	initial_sidebar_state="expanded",
)

ACCENT = "#7a0d0d"
PLAN_ORDER = ["Basic", "Standard", "Premium"]


def image_data_uri(filename: str) -> str:
	image_path = Path(__file__).resolve().parent / filename
	if not image_path.is_file():
		return ""
	encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
	return f"data:image/jpeg;base64,{encoded_image}"


@st.cache_data
def load_data(data_path: str) -> pd.DataFrame:
	data = pd.read_csv(data_path)
	data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
	return data.dropna(subset=["Watch_Date"]).drop_duplicates()


data_path = Path(__file__).resolve().parent / "netflix.csv"
try:
	netflix = load_data(str(data_path))
except (FileNotFoundError, pd.errors.ParserError) as error:
	st.error(f"Could not load the Netflix dataset: {error}")
	st.stop()

if netflix.empty:
	st.error("The dataset has no rows with valid watch dates.")
	st.stop()

st.markdown(
	"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
	.stApp, [data-testid="stAppViewContainer"] { background: linear-gradient(180deg, #fff7f7 0%, #f3e6e6 18%, #1b0909 100%); color: #1a0d0d; }
	[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(43,8,8,0.98), rgba(18,5,5,0.98)); border-right: 1px solid rgba(130,18,18,0.85); }
	[data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
	[data-testid="stSidebar"] [data-baseweb="select"] > div,
	[data-testid="stSidebar"] [data-baseweb="input"] > div { background: #000000 !important; border-color: #000000 !important; color: #ffffff !important; }
	[data-testid="stSidebar"] [data-baseweb="select"] > div:hover,
	[data-testid="stSidebar"] [data-baseweb="input"] > div:hover { border-color: #000000 !important; }
	[data-testid="stSidebar"] [data-baseweb="tag"] { background: #000000 !important; border: 1px solid #000000 !important; color: #ffffff !important; }
	[data-testid="stSidebar"] [data-baseweb="tag"] span,
	[data-testid="stSidebar"] [data-baseweb="select"] [role="combobox"],
	[data-testid="stSidebar"] input { color: #ffffff !important; }
	[data-testid="stSidebar"] h2,
	[data-testid="stSidebar"] label,
	[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { color: #ffffff !important; }
	[data-testid="stSidebar"] svg { color: #ffffff !important; }
	.block-container { max-width: 1440px; padding-top: 2.4rem; padding-bottom: 3rem; }
	h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
	.eyebrow { color: #8c1010; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
	.dashboard-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.3rem; font-weight: 700; margin: 0.25rem 0 0; }
	.dashboard-subtitle { color: #5d2a2a; margin: 0.3rem 0 1.5rem; }
	[data-testid="stMetric"] { background: rgba(255,255,255,0.82); border: 1px solid rgba(111,17,17,0.16); border-radius: 8px; padding: 1rem 1.1rem; box-shadow: 0 1px 0 rgba(0,0,0,0.04); }
	[data-testid="stMetricLabel"] { color: #4c3b3b; }
	[data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif; color: #1a0e0e; }
	[data-testid="stPlotlyChart"] { background: rgba(255,255,255,0.75); border: 1px solid rgba(111,17,17,0.12); border-radius: 8px; padding: 0.4rem; }
	.hero-banner { min-height: 250px; display: flex; align-items: flex-end; padding: 1.8rem 2rem; margin-bottom: 1.25rem; border: 1px solid rgba(125,15,15,0.14); border-radius: 8px; background-color: #1b0909; background-size: cover; background-position: center 43%; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06); }
	.hero-brand { display: flex; align-items: center; gap: 1.1rem; }
	.hero-logo { width: 78px; height: 78px; flex: none; object-fit: contain; border-radius: 4px; }
	.hero-logo-fallback { width: 78px; height: 78px; display: grid; place-items: center; color: #b01010; font: 700 3rem 'Space Grotesk', sans-serif; }
	.hero-banner .eyebrow,
	.hero-banner .hero-title [data-heading-text],
	.hero-banner .hero-subtitle,
	.hero-banner .hero-subtitle > span {
		color: #ffffff !important;
		-webkit-text-fill-color: #ffffff !important;
		text-shadow: 0 1px 8px rgba(0,0,0,0.95);
	}
	.hero-title { margin: 0; font: 700 2.3rem 'Space Grotesk', sans-serif; color: #d92525; }
	.hero-subtitle { margin: 0.35rem 0 0; color: #f5d9d9; }
	@media (max-width: 640px) { .hero-banner { min-height: 210px; padding: 1.2rem; background-position: 58% center; } .hero-logo, .hero-logo-fallback { width: 58px; height: 58px; } .hero-title { font-size: 1.8rem; } }
	hr { border-color: rgba(15,15,15,0.12); }
	</style>
	""",
	unsafe_allow_html=True,
)

st.sidebar.markdown(
	f"<div class='eyebrow' style='color:{ACCENT}'>N / INSIGHTS</div>",
	unsafe_allow_html=True,
)
st.sidebar.header("Filters")


def multiselect_filter(label: str, column: str) -> list[str]:
	options = sorted(netflix[column].dropna().astype(str).unique().tolist())
	return st.sidebar.multiselect(label, options, default=options)


regions = multiselect_filter("Region", "Region")
plans = multiselect_filter("Subscription plan", "Subscription_Plan")
categories = multiselect_filter("Category", "Category")
min_date = netflix["Watch_Date"].min().date()
max_date = netflix["Watch_Date"].max().date()
date_range = st.sidebar.date_input(
	"Watch dates",
	value=(min_date, max_date),
	min_value=min_date,
	max_value=max_date,
)

if len(date_range) == 2:
	start_date, end_date = date_range
elif len(date_range) == 1:
	start_date = end_date = date_range[0]
else:
	start_date, end_date = min_date, max_date

filtered = netflix[
	netflix["Region"].astype(str).isin(regions)
	& netflix["Subscription_Plan"].astype(str).isin(plans)
	& netflix["Category"].astype(str).isin(categories)
	& netflix["Watch_Date"].dt.date.between(start_date, end_date)
].copy()

background_image = image_data_uri("netflix bg images.jpg")
logo_image = image_data_uri("netflixlogo.images.jpg")
hero_background = (
	f"background-image: linear-gradient(90deg, rgba(10,10,10,.96) 0%, rgba(10,10,10,.78) 42%, rgba(10,10,10,.2) 100%), "
	f"linear-gradient(0deg, rgba(10,10,10,.48), transparent 72%), url('{background_image}');"
	if background_image
	else "background-image: linear-gradient(120deg, #171717, #2a1618);"
)
logo_markup = (
	f"<img class='hero-logo' src='{logo_image}' alt='Netflix logo'>"
	if logo_image
	else "<div class='hero-logo-fallback' aria-hidden='true'>N</div>"
)
st.markdown(
	f"""
	<div class="hero-banner" style="{hero_background}">
		<div class="hero-brand">
			{logo_markup}
			<div>
				<div class="eyebrow">Streaming performance</div>
				<h1 class="hero-title">Netflix Insights</h1>
				<p class="hero-subtitle">A clear view of audience, viewing habits, and revenue.</p>
			</div>
		</div>
	</div>
	""",
	unsafe_allow_html=True,
)

metric_columns = st.columns(4)
metric_columns[0].metric("Customers", f"{filtered['Customer_ID'].nunique():,}")
metric_columns[1].metric("Revenue", f"{filtered['Monthly_Revenue'].sum():,.0f}")
average_rating = filtered["Rating"].mean()
metric_columns[2].metric("Average rating", f"{average_rating:.1f} / 5" if pd.notna(average_rating) else "—")
watch_hours = filtered["Watch_Time_Minutes"].sum() / 60
metric_columns[3].metric("Watch time", f"{watch_hours:,.1f} hrs")

st.divider()


def style_chart(chart: object, height: int = 340) -> object:
	chart.update_layout(
		height=height,
		paper_bgcolor="rgba(0,0,0,0)",
		plot_bgcolor="rgba(0,0,0,0)",
		font={"family": "DM Sans, sans-serif", "color": "#e8e5e3", "size": 12},
		margin={"l": 18, "r": 18, "t": 54, "b": 20},
		title={"font": {"family": "Space Grotesk, sans-serif", "size": 17}},
		legend={"orientation": "h", "y": -0.2},
	)
	chart.update_xaxes(gridcolor="#303030", zerolinecolor="#303030", title=None)
	chart.update_yaxes(gridcolor="#303030", zerolinecolor="#303030", title=None)
	return chart


def show_chart(chart: object) -> None:
	st.plotly_chart(style_chart(chart), width="stretch", config={"displaylogo": False})


def chart_heading(title: str, description: str) -> None:
	st.subheader(title)
	st.caption(description)


if filtered.empty:
	st.info("No records match these filters. Adjust the selections in the sidebar.")
else:
	region_col, category_col = st.columns(2, gap="large")
	with region_col:
		chart_heading("Revenue by region", "Total revenue across the selected audience.")
		region_revenue = (
			filtered.groupby("Region", as_index=False, observed=True)["Monthly_Revenue"]
			.sum()
			.sort_values("Monthly_Revenue", ascending=True)
		)
		show_chart(
			px.bar(
				region_revenue,
				x="Monthly_Revenue",
				y="Region",
				orientation="h",
				color_discrete_sequence=[ACCENT],
				labels={"Monthly_Revenue": "Revenue", "Region": ""},
			)
		)

	with category_col:
		chart_heading("Revenue by category", "Which genres contribute most to revenue?")
		category_revenue = (
			filtered.groupby("Category", as_index=False, observed=True)["Monthly_Revenue"]
			.sum()
			.sort_values("Monthly_Revenue", ascending=True)
		)
		show_chart(
			px.bar(
				category_revenue,
				x="Monthly_Revenue",
				y="Category",
				orientation="h",
					color_discrete_sequence=["#f0444b"],
				labels={"Monthly_Revenue": "Revenue", "Category": ""},
			)
		)

	month_col, plan_col = st.columns(2, gap="large")
	with month_col:
		chart_heading("Monthly revenue", "Revenue by watch month, in calendar order.")
		monthly_revenue = (
			filtered.assign(Month=filtered["Watch_Date"].dt.to_period("M").dt.to_timestamp())
			.groupby("Month", as_index=False, observed=True)["Monthly_Revenue"]
			.sum()
			.sort_values("Month")
		)
		monthly_revenue["Month"] = monthly_revenue["Month"].dt.strftime("%b %Y")
		show_chart(
			px.bar(
				monthly_revenue,
				x="Month",
				y="Monthly_Revenue",
				color_discrete_sequence=[ACCENT],
				labels={"Monthly_Revenue": "Revenue", "Month": ""},
			)
		)

	with plan_col:
		chart_heading("Rating points by plan", "Sum of customer ratings for each subscription tier.")
		plan_ratings = (
			filtered.groupby("Subscription_Plan", as_index=False, observed=True)["Rating"]
			.sum()
			.rename(columns={"Rating": "Rating points"})
		)
		plan_ratings["Subscription_Plan"] = pd.Categorical(
			plan_ratings["Subscription_Plan"], categories=PLAN_ORDER, ordered=True
		)
		plan_ratings = plan_ratings.sort_values("Subscription_Plan")
		show_chart(
			px.line(
				plan_ratings,
				x="Subscription_Plan",
				y="Rating points",
				markers=True,
				color_discrete_sequence=["#f0444b"],
				labels={"Subscription_Plan": "Plan"},
			)
		)

	rating_col, detail_col = st.columns(2, gap="large")
	with rating_col:
		chart_heading("Rating share by plan", "How each plan contributes to all rating points.")
		show_chart(
			px.pie(
				plan_ratings,
				names="Subscription_Plan",
				values="Rating points",
				hole=0.66,
				color_discrete_sequence=[ACCENT, "#f06b45", "#f5a65b"],
			)
		)

	with detail_col:
		chart_heading("Top titles", "Most-watched titles in the selected audience.")
		top_titles = (
			filtered.groupby("Title", as_index=False, observed=True)["Watch_Count"]
			.sum()
			.sort_values("Watch_Count", ascending=False)
			.head(8)
		)
		show_chart(
			px.bar(
				top_titles.sort_values("Watch_Count"),
				x="Watch_Count",
				y="Title",
				orientation="h",
				color_discrete_sequence=["#f5a65b"],
				labels={"Watch_Count": "Watches", "Title": ""},
			)
		)

st.caption(f"Showing {len(filtered):,} of {len(netflix):,} records · Dates: {start_date:%b %d, %Y} – {end_date:%b %d, %Y}")




