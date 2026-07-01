"""
India Agriculture Interactive Dashboard — ICRISAT District Level Data
Single-file Streamlit + Plotly app (crop config + data utils + UI merged).

Run:
    pip install -r requirements.txt
    streamlit run agriculture_dashboard.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

DATA_PATH = "ICRISAT-District Level Data - ICRISAT-District Level Data.csv"

# ============================================================================
# SECTION 1: CROP -> CATEGORY CONFIGURATION
# ============================================================================

CROP_CATEGORIES = {
    "Food Grains": {
        "Rice":          {"area": "RICE AREA (1000 ha)", "production": "RICE PRODUCTION (1000 tons)", "yield": "RICE YIELD (Kg per ha)"},
        "Wheat":         {"area": "WHEAT AREA (1000 ha)", "production": "WHEAT PRODUCTION (1000 tons)", "yield": "WHEAT YIELD (Kg per ha)"},
        "Sorghum (Total)": {"area": "SORGHUM AREA (1000 ha)", "production": "SORGHUM PRODUCTION (1000 tons)", "yield": "SORGHUM YIELD (Kg per ha)"},
        "Kharif Sorghum": {"area": "KHARIF SORGHUM AREA (1000 ha)", "production": "KHARIF SORGHUM PRODUCTION (1000 tons)", "yield": "KHARIF SORGHUM YIELD (Kg per ha)"},
        "Rabi Sorghum":  {"area": "RABI SORGHUM AREA (1000 ha)", "production": "RABI SORGHUM PRODUCTION (1000 tons)", "yield": "RABI SORGHUM YIELD (Kg per ha)"},
        "Pearl Millet":  {"area": "PEARL MILLET AREA (1000 ha)", "production": "PEARL MILLET PRODUCTION (1000 tons)", "yield": "PEARL MILLET YIELD (Kg per ha)"},
        "Maize":         {"area": "MAIZE AREA (1000 ha)", "production": "MAIZE PRODUCTION (1000 tons)", "yield": "MAIZE YIELD (Kg per ha)"},
        "Finger Millet": {"area": "FINGER MILLET AREA (1000 ha)", "production": "FINGER MILLET PRODUCTION (1000 tons)", "yield": "FINGER MILLET YIELD (Kg per ha)"},
        "Barley":        {"area": "BARLEY AREA (1000 ha)", "production": "BARLEY PRODUCTION (1000 tons)", "yield": "BARLEY YIELD (Kg per ha)"},
    },
    "Pulses": {
        "Chickpea":     {"area": "CHICKPEA AREA (1000 ha)", "production": "CHICKPEA PRODUCTION (1000 tons)", "yield": "CHICKPEA YIELD (Kg per ha)"},
        "Pigeonpea":    {"area": "PIGEONPEA AREA (1000 ha)", "production": "PIGEONPEA PRODUCTION (1000 tons)", "yield": "PIGEONPEA YIELD (Kg per ha)"},
        "Minor Pulses": {"area": "MINOR PULSES AREA (1000 ha)", "production": "MINOR PULSES PRODUCTION (1000 tons)", "yield": "MINOR PULSES YIELD (Kg per ha)"},
    },
    "Oilseeds": {
        "Groundnut":           {"area": "GROUNDNUT AREA (1000 ha)", "production": "GROUNDNUT PRODUCTION (1000 tons)", "yield": "GROUNDNUT YIELD (Kg per ha)"},
        "Sesamum":             {"area": "SESAMUM AREA (1000 ha)", "production": "SESAMUM PRODUCTION (1000 tons)", "yield": "SESAMUM YIELD (Kg per ha)"},
        "Rapeseed & Mustard":  {"area": "RAPESEED AND MUSTARD AREA (1000 ha)", "production": "RAPESEED AND MUSTARD PRODUCTION (1000 tons)", "yield": "RAPESEED AND MUSTARD YIELD (Kg per ha)"},
        "Safflower":           {"area": "SAFFLOWER AREA (1000 ha)", "production": "SAFFLOWER PRODUCTION (1000 tons)", "yield": "SAFFLOWER YIELD (Kg per ha)"},
        "Castor":              {"area": "CASTOR AREA (1000 ha)", "production": "CASTOR PRODUCTION (1000 tons)", "yield": "CASTOR YIELD (Kg per ha)"},
        "Linseed":             {"area": "LINSEED AREA (1000 ha)", "production": "LINSEED PRODUCTION (1000 tons)", "yield": "LINSEED YIELD (Kg per ha)"},
        "Sunflower":           {"area": "SUNFLOWER AREA (1000 ha)", "production": "SUNFLOWER PRODUCTION (1000 tons)", "yield": "SUNFLOWER YIELD (Kg per ha)"},
        "Soyabean":            {"area": "SOYABEAN AREA (1000 ha)", "production": "SOYABEAN PRODUCTION (1000 tons)", "yield": "SOYABEAN YIELD (Kg per ha)"},
        "Total Oilseeds":      {"area": "OILSEEDS AREA (1000 ha)", "production": "OILSEEDS PRODUCTION (1000 tons)", "yield": "OILSEEDS YIELD (Kg per ha)"},
    },
    "Commercial / Cash Crops": {
        "Sugarcane": {"area": "SUGARCANE AREA (1000 ha)", "production": "SUGARCANE PRODUCTION (1000 tons)", "yield": "SUGARCANE YIELD (Kg per ha)"},
        "Cotton":    {"area": "COTTON AREA (1000 ha)", "production": "COTTON PRODUCTION (1000 tons)", "yield": "COTTON YIELD (Kg per ha)"},
    },
    "Horticulture": {
        "Fruits":               {"area": "FRUITS AREA (1000 ha)", "production": None, "yield": None},
        "Vegetables":           {"area": "VEGETABLES AREA (1000 ha)", "production": None, "yield": None},
        "Fruits & Vegetables":  {"area": "FRUITS AND VEGETABLES AREA (1000 ha)", "production": None, "yield": None},
        "Potatoes":             {"area": "POTATOES AREA (1000 ha)", "production": None, "yield": None},
        "Onion":                {"area": "ONION AREA (1000 ha)", "production": None, "yield": None},
    },
    "Fodder": {
        "Fodder": {"area": "FODDER AREA (1000 ha)", "production": None, "yield": None},
    },
}

# Crops that only have Area (no Production/Yield) in the source data
AREA_ONLY_CATEGORIES = {"Horticulture", "Fodder"}

# Crops used for "Total <Category>" roll-ups (categories where we sum constituent crops).
# For Oilseeds we use the dataset's own OILSEEDS columns as ground truth instead of re-summing,
# to avoid double counting since "Total Oilseeds" is already provided.
CATEGORY_SUM_CROPS = {
    "Food Grains": ["Rice", "Wheat", "Sorghum (Total)", "Pearl Millet", "Maize", "Finger Millet", "Barley"],
    "Pulses": ["Chickpea", "Pigeonpea", "Minor Pulses"],
    "Oilseeds": ["Total Oilseeds"],  # already an aggregate column in source
    "Commercial / Cash Crops": ["Sugarcane", "Cotton"],
    "Horticulture": ["Fruits & Vegetables", "Potatoes", "Onion"],
    "Fodder": ["Fodder"],
}

ALL_CROPS_FLAT = {}
for _cat, _crops in CROP_CATEGORIES.items():
    for _crop, _cols in _crops.items():
        ALL_CROPS_FLAT[_crop] = {"category": _cat, **_cols}

# ============================================================================
# SECTION 2: DATA LOADING & AGGREGATION HELPERS
# ============================================================================

# Some state names in this dataset differ from common/current usage or from the
# GeoJSON used for the India map. Keep a normalizer for display + map-matching.
STATE_NAME_FIXES = {
    "Orissa": "Odisha",
}


def load_raw(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # -1 is used in this dataset as a missing-value sentinel
    df[numeric_cols] = df[numeric_cols].replace(-1, np.nan)
    df["State Name"] = df["State Name"].replace(STATE_NAME_FIXES)
    return df


def get_crop_cols(crop: str):
    """Return (area_col, production_col, yield_col) for a crop, any may be None."""
    info = ALL_CROPS_FLAT[crop]
    return info["area"], info["production"], info["yield"]


def add_category_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Adds '<Category> AREA/PRODUCTION/YIELD (computed)' columns to df by summing
    constituent crops for each category (row-wise), then computing weighted yield."""
    df = df.copy()
    for category, crop_list in CATEGORY_SUM_CROPS.items():
        area_cols, prod_cols = [], []
        for crop in crop_list:
            a, p, _ = get_crop_cols(crop)
            if a:
                area_cols.append(a)
            if p:
                prod_cols.append(p)
        area_out = f"{category} AREA (computed)"
        prod_out = f"{category} PRODUCTION (computed)"
        yield_out = f"{category} YIELD (computed)"
        df[area_out] = df[area_cols].sum(axis=1, skipna=True) if area_cols else np.nan
        if prod_cols:
            df[prod_out] = df[prod_cols].sum(axis=1, skipna=True)
            with np.errstate(divide="ignore", invalid="ignore"):
                df[yield_out] = np.where(df[area_out] > 0, (df[prod_out] / df[area_out]) * 1000, np.nan)
        else:
            df[prod_out] = np.nan
            df[yield_out] = np.nan
    return df


def category_metric_col(category: str, metric: str) -> str:
    """metric in {'AREA','PRODUCTION','YIELD'} -> computed column name for a category total."""
    return f"{category} {metric} (computed)"


def weighted_yield(production_sum: float, area_sum: float) -> float:
    if area_sum and area_sum > 0:
        return (production_sum / area_sum) * 1000
    return np.nan


def top_n_by_sum(df: pd.DataFrame, group_col: str, value_col: str, n: int = 7, ascending: bool = False) -> pd.DataFrame:
    g = df.groupby(group_col, as_index=False)[value_col].sum(numeric_only=True)
    g = g.sort_values(value_col, ascending=ascending).head(n)
    return g


def state_year_agg(df: pd.DataFrame, value_col: str, agg="sum") -> pd.DataFrame:
    return df.groupby(["State Name", "Year"], as_index=False)[value_col].agg(agg)

# ============================================================================
# SECTION 3: STREAMLIT APP (UI)
# ============================================================================
# ----------------------------------------------------------------------------
# PAGE CONFIG + STYLE
# ----------------------------------------------------------------------------
st.set_page_config(page_title="India Agriculture Dashboard | ICRISAT", layout="wide",
                    page_icon="🌾", initial_sidebar_state="expanded")

ACCENT = "#5F259F"   # phonepe-purple accent
ACCENT2 = "#00B9AE"

st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.2rem; }}
    h1, h2, h3 {{ color: #2b2b2b; }}
    .metric-card {{
        background: linear-gradient(135deg, {ACCENT}12, {ACCENT2}12);
        border: 1px solid #eee; border-radius: 12px; padding: 14px 18px; margin-bottom: 6px;
    }}
    .insight-box {{
        background: #f4f1fa; border-left: 5px solid {ACCENT};
        padding: 10px 16px; border-radius: 6px; margin: 6px 0 18px 0; font-size: 0.95rem;
        color: #1a1a1a !important;
    }}
    .insight-box, .insight-box * {{ color: #1a1a1a !important; }}
    div[data-testid="stMetricValue"] {{ color: {ACCENT}; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 1rem; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

PLOT_TEMPLATE = "plotly_white"
COLOR_SEQ = px.colors.qualitative.Bold


def insight(text: str):
    st.markdown(f'<div class="insight-box">💡 <b>Insight:</b> {text}</div>', unsafe_allow_html=True)


def data_table(df: pd.DataFrame, label: str = "📄 View underlying data"):
    with st.expander(label):
        st.dataframe(df, width="stretch")


# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading ICRISAT dataset...")
def get_data():
    df = load_raw(DATA_PATH)
    df = add_category_aggregates(df)
    return df


df_full = get_data()
YEAR_MIN, YEAR_MAX = int(df_full["Year"].min()), int(df_full["Year"].max())
ALL_STATES = sorted(df_full["State Name"].unique().tolist())

# ----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------------
st.sidebar.markdown("## 🌾 Agri Dashboard")
st.sidebar.caption("ICRISAT District Level Data · 1966-2017 · 20 States")

mode = st.sidebar.radio(
    "Choose a view",
    ["📊 Insights & Questions Dashboard", "🗺️ India Map Explorer (PhonePe-Pulse style)"],
    index=0,
)

st.sidebar.markdown("---")

# ============================================================================
# MODE 1 : INSIGHTS & QUESTIONS DASHBOARD
# ============================================================================
if mode.startswith("📊"):
    st.sidebar.subheader("Global Filters")
    year_range = st.sidebar.slider("Year range", YEAR_MIN, YEAR_MAX, (YEAR_MIN, YEAR_MAX))
    state_filter = st.sidebar.multiselect("State(s) — optional, applies where relevant", ALL_STATES)

    df = df_full[(df_full["Year"] >= year_range[0]) & (df_full["Year"] <= year_range[1])]
    if state_filter:
        df_state_scope = df[df["State Name"].isin(state_filter)]
    else:
        df_state_scope = df

    st.title("🌾 India Agriculture — Exploratory Analysis & Insights")
    st.caption("Data source: ICRISAT District Level Data (1966–2017)")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Districts", df["Dist Name"].nunique())
    c2.metric("States", df["State Name"].nunique())
    c3.metric("Years covered", f"{year_range[0]}–{year_range[1]}")
    c4.metric("Total Rice Prod. (kt)", f"{df['RICE PRODUCTION (1000 tons)'].sum():,.0f}")
    c5.metric("Total Wheat Prod. (kt)", f"{df['WHEAT PRODUCTION (1000 tons)'].sum():,.0f}")

    tabs = st.tabs(["🔍 Exploratory Data Analysis (15)", "❓ Key Questions (10)"])
    tab_eda, tab_q = tabs[0], tabs[1]

    # ------------------------------------------------------------------ EDA
    with tab_eda:

        # 1. Top 7 Rice production states
        st.subheader("1. Top 7 Rice-Producing States")
        g = df.groupby("State Name", as_index=False)["RICE PRODUCTION (1000 tons)"].sum().sort_values(
            "RICE PRODUCTION (1000 tons)", ascending=False).head(7)
        fig = px.bar(g, x="State Name", y="RICE PRODUCTION (1000 tons)", color="State Name",
                     color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE, text_auto=".2s")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Rice Production (1000 tons)")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{g.iloc[0]['State Name']}</b> leads all-India rice production with "
                f"{g.iloc[0]['RICE PRODUCTION (1000 tons)']:,.0f} thousand tons over the selected period — "
                f"about {g.iloc[0]['RICE PRODUCTION (1000 tons)']/g['RICE PRODUCTION (1000 tons)'].sum()*100:.1f}% of the combined top-7 total.")
        data_table(g)

        # 2. Top 5 Wheat states — bar + pie
        st.subheader("2. Top 5 Wheat-Producing States (Bar) & Share (Pie)")
        gw = df.groupby("State Name", as_index=False)["WHEAT PRODUCTION (1000 tons)"].sum().sort_values(
            "WHEAT PRODUCTION (1000 tons)", ascending=False).head(5)
        colA, colB = st.columns(2)
        with colA:
            fig = px.bar(gw, x="State Name", y="WHEAT PRODUCTION (1000 tons)", color="State Name",
                         color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE, text_auto=".2s")
            fig.update_layout(showlegend=False, xaxis_title="")
            st.plotly_chart(fig, width="stretch")
        with colB:
            fig = px.pie(gw, names="State Name", values="WHEAT PRODUCTION (1000 tons)", hole=0.45,
                         color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE)
            st.plotly_chart(fig, width="stretch")
        insight(f"<b>{gw.iloc[0]['State Name']}</b> alone contributes "
                f"{gw.iloc[0]['WHEAT PRODUCTION (1000 tons)']/gw['WHEAT PRODUCTION (1000 tons)'].sum()*100:.1f}% "
                f"of the top-5 states' wheat output — India's wheat belt is heavily concentrated in the north/northwest.")
        data_table(gw)

        # 3. Oilseed production by top 5 states
        st.subheader("3. Oilseed Production — Top 5 States")
        go_ = df.groupby("State Name", as_index=False)["OILSEEDS PRODUCTION (1000 tons)"].sum().sort_values(
            "OILSEEDS PRODUCTION (1000 tons)", ascending=False).head(5)
        fig = px.bar(go_, x="OILSEEDS PRODUCTION (1000 tons)", y="State Name", orientation="h",
                     color="OILSEEDS PRODUCTION (1000 tons)", color_continuous_scale="Purples", template=PLOT_TEMPLATE, text_auto=".2s")
        fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{go_.iloc[0]['State Name']}</b> is India's top oilseed producer in this dataset, "
                f"producing {go_.iloc[0]['OILSEEDS PRODUCTION (1000 tons)']:,.0f} thousand tons cumulatively.")
        data_table(go_)

        # 4. Top 7 Sunflower states
        st.subheader("4. Top 7 Sunflower-Producing States")
        gs = df.groupby("State Name", as_index=False)["SUNFLOWER PRODUCTION (1000 tons)"].sum().sort_values(
            "SUNFLOWER PRODUCTION (1000 tons)", ascending=False).head(7)
        fig = px.bar(gs, x="State Name", y="SUNFLOWER PRODUCTION (1000 tons)", color="State Name",
                     color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE, text_auto=".2s")
        fig.update_layout(showlegend=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{gs.iloc[0]['State Name']}</b> dominates sunflower cultivation "
                f"with {gs.iloc[0]['SUNFLOWER PRODUCTION (1000 tons)']:,.0f} thousand tons.")
        data_table(gs)

        # 5. India sugarcane production - last 50 years
        st.subheader("5. India's Sugarcane Production — Last 50 Years")
        gy = df_full.groupby("Year", as_index=False)["SUGARCANE PRODUCTION (1000 tons)"].sum()
        fig = px.line(gy, x="Year", y="SUGARCANE PRODUCTION (1000 tons)", markers=False,
                      template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT])
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, width="stretch")
        peak = gy.loc[gy["SUGARCANE PRODUCTION (1000 tons)"].idxmax()]
        insight(f"National sugarcane production grew from {gy.iloc[0]['SUGARCANE PRODUCTION (1000 tons)']:,.0f} "
                f"kt in {int(gy.iloc[0]['Year'])} to a peak of {peak['SUGARCANE PRODUCTION (1000 tons)']:,.0f} kt "
                f"in {int(peak['Year'])} — a multi-decade upward trend driven by irrigation expansion and better varieties.")
        data_table(gy)

        # 6. Rice vs Wheat production - last 50 years
        st.subheader("6. Rice Production vs Wheat Production — Last 50 Years")
        gr = df_full.groupby("Year", as_index=False)[["RICE PRODUCTION (1000 tons)", "WHEAT PRODUCTION (1000 tons)"]].sum()
        gr_melt = gr.melt(id_vars="Year", var_name="Crop", value_name="Production (1000 tons)")
        fig = px.line(gr_melt, x="Year", y="Production (1000 tons)", color="Crop",
                      template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT, ACCENT2])
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, width="stretch")
        insight("Both crops show consistent growth, but rice retains a higher absolute production level "
                "throughout, reflecting its role as India's staple kharif crop versus wheat's rabi dominance.")
        data_table(gr)

        # 7. Rice production by West Bengal districts
        st.subheader("7. Rice Production by West Bengal Districts")
        wb = df_full[df_full["State Name"] == "West Bengal"]
        gwb = wb.groupby("Dist Name", as_index=False)["RICE PRODUCTION (1000 tons)"].sum().sort_values(
            "RICE PRODUCTION (1000 tons)", ascending=False)
        fig = px.bar(gwb, x="Dist Name", y="RICE PRODUCTION (1000 tons)", color="RICE PRODUCTION (1000 tons)",
                     color_continuous_scale="Greens", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"Within West Bengal, <b>{gwb.iloc[0]['Dist Name']}</b> is the largest rice-producing district "
                f"(cumulative {gwb.iloc[0]['RICE PRODUCTION (1000 tons)']:,.0f} kt, 1966–2017).")
        data_table(gwb)

        # 8. Top 10 wheat production years from UP
        st.subheader("8. Top 10 Wheat-Production Years — Uttar Pradesh")
        up = df_full[df_full["State Name"] == "Uttar Pradesh"]
        gup = up.groupby("Year", as_index=False)["WHEAT PRODUCTION (1000 tons)"].sum().sort_values(
            "WHEAT PRODUCTION (1000 tons)", ascending=False).head(10)
        fig = px.bar(gup.sort_values("Year"), x="Year", y="WHEAT PRODUCTION (1000 tons)",
                     template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT])
        fig.update_xaxes(type="category")
        st.plotly_chart(fig, width="stretch")
        insight(f"UP's best wheat year on record is <b>{int(gup.iloc[0]['Year'])}</b> with "
                f"{gup.iloc[0]['WHEAT PRODUCTION (1000 tons)']:,.0f} kt — the top-10 years are concentrated "
                f"in the later part of the series, showing the impact of Green-Revolution-era productivity gains.")
        data_table(gup.sort_values("WHEAT PRODUCTION (1000 tons)", ascending=False))

        # 9. Millet production - last 50 years
        st.subheader("9. Millet Production (Pearl + Finger Millet) — Last 50 Years")
        df_full["MILLET PRODUCTION (1000 tons)"] = (
            df_full["PEARL MILLET PRODUCTION (1000 tons)"].fillna(0) + df_full["FINGER MILLET PRODUCTION (1000 tons)"].fillna(0)
        )
        gm = df_full.groupby("Year", as_index=False)["MILLET PRODUCTION (1000 tons)"].sum()
        fig = px.area(gm, x="Year", y="MILLET PRODUCTION (1000 tons)", template=PLOT_TEMPLATE,
                      color_discrete_sequence=[ACCENT2])
        st.plotly_chart(fig, width="stretch")
        insight(f"Combined millet production peaked at {gm['MILLET PRODUCTION (1000 tons)'].max():,.0f} kt "
                f"in {int(gm.loc[gm['MILLET PRODUCTION (1000 tons)'].idxmax(),'Year'])}, "
                "reflecting millets' role as a resilient, lower-input crop across semi-arid India.")
        data_table(gm)

        # 10. Sorghum (Kharif vs Rabi) by region/state
        st.subheader("10. Sorghum Production (Kharif vs Rabi) by State")
        gsor = df.groupby("State Name", as_index=False)[["KHARIF SORGHUM PRODUCTION (1000 tons)", "RABI SORGHUM PRODUCTION (1000 tons)"]].sum()
        gsor = gsor[(gsor["KHARIF SORGHUM PRODUCTION (1000 tons)"] > 0) | (gsor["RABI SORGHUM PRODUCTION (1000 tons)"] > 0)]
        gsor_melt = gsor.melt(id_vars="State Name", var_name="Season", value_name="Production (1000 tons)")
        fig = px.bar(gsor_melt, x="State Name", y="Production (1000 tons)", color="Season", barmode="stack",
                     template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT, ACCENT2])
        st.plotly_chart(fig, width="stretch")
        insight("Rabi sorghum is concentrated in Maharashtra/Karnataka while Kharif sorghum is more broadly "
                "spread — the two seasons draw on different agro-climatic windows.")
        data_table(gsor)

        # 11. Top 7 states for groundnut
        st.subheader("11. Top 7 States for Groundnut Production")
        ggn = df.groupby("State Name", as_index=False)["GROUNDNUT PRODUCTION (1000 tons)"].sum().sort_values(
            "GROUNDNUT PRODUCTION (1000 tons)", ascending=False).head(7)
        fig = px.bar(ggn, x="State Name", y="GROUNDNUT PRODUCTION (1000 tons)", color="State Name",
                     color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE, text_auto=".2s")
        fig.update_layout(showlegend=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{ggn.iloc[0]['State Name']}</b> is India's groundnut powerhouse, historically driven by "
                "its semi-arid tropic zones ideally suited to the crop.")
        data_table(ggn)

        # 12. Soybean production by top 5 states + yield efficiency
        st.subheader("12. Soybean — Top 5 States: Production vs Yield Efficiency")
        gsb = df.groupby("State Name", as_index=False).agg(
            **{"SOYABEAN PRODUCTION (1000 tons)": ("SOYABEAN PRODUCTION (1000 tons)", "sum"),
               "SOYABEAN AREA (1000 ha)": ("SOYABEAN AREA (1000 ha)", "sum")})
        gsb["Yield (Kg/ha)"] = np.where(gsb["SOYABEAN AREA (1000 ha)"] > 0,
                                         gsb["SOYABEAN PRODUCTION (1000 tons)"] / gsb["SOYABEAN AREA (1000 ha)"] * 1000, np.nan)
        gsb = gsb.sort_values("SOYABEAN PRODUCTION (1000 tons)", ascending=False).head(5)
        fig = go.Figure()
        fig.add_bar(x=gsb["State Name"], y=gsb["SOYABEAN PRODUCTION (1000 tons)"], name="Production (1000 t)",
                    marker_color=ACCENT)
        fig.add_trace(go.Scatter(x=gsb["State Name"], y=gsb["Yield (Kg/ha)"], name="Yield (Kg/ha)",
                                  yaxis="y2", mode="lines+markers", marker_color=ACCENT2, line_width=3))
        fig.update_layout(template=PLOT_TEMPLATE, yaxis=dict(title="Production (1000 t)"),
                           yaxis2=dict(title="Yield (Kg/ha)", overlaying="y", side="right"))
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{gsb.iloc[0]['State Name']}</b> leads in volume, but yield efficiency (kg/ha) can favor a "
                "different state — high production doesn't always mean the most efficient land use.")
        data_table(gsb)

        # 13. Oilseed production in major states - crop composition
        st.subheader("13. Oilseed Crop Composition in Top 5 Oilseed States")
        oil_crops = ["Groundnut", "Sesamum", "Rapeseed & Mustard", "Safflower", "Castor", "Linseed", "Sunflower", "Soyabean"]
        top5_oil_states = go_["State Name"].tolist() if len(go_) else []
        rows = []
        for crop in oil_crops:
            a, p, y = get_crop_cols(crop)
            tmp = df[df["State Name"].isin(top5_oil_states)].groupby("State Name", as_index=False)[p].sum()
            tmp["Crop"] = crop
            tmp = tmp.rename(columns={p: "Production (1000 tons)"})
            rows.append(tmp)
        comp = pd.concat(rows, ignore_index=True)
        fig = px.bar(comp, x="State Name", y="Production (1000 tons)", color="Crop", barmode="stack",
                     template=PLOT_TEMPLATE, color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")
        insight("Groundnut and Soyabean dominate the oilseed mix in most major producing states, "
                "while Rapeseed & Mustard is important in the north.")
        data_table(comp)

        # 14. Impact of area on production (Rice, Wheat, Maize)
        st.subheader("14. Impact of Area Cultivated on Production — Rice, Wheat, Maize")
        rows = []
        for crop in ["Rice", "Wheat", "Maize"]:
            a, p, y = get_crop_cols(crop)
            tmp = df[[a, p]].dropna().rename(columns={a: "Area (1000 ha)", p: "Production (1000 tons)"})
            tmp["Crop"] = crop
            rows.append(tmp.sample(min(1500, len(tmp)), random_state=42))
        scat = pd.concat(rows, ignore_index=True)
        fig = px.scatter(scat, x="Area (1000 ha)", y="Production (1000 tons)", color="Crop", opacity=0.5,
                         trendline="ols", template=PLOT_TEMPLATE, color_discrete_sequence=COLOR_SEQ)
        st.plotly_chart(fig, width="stretch")
        corrs = {c: df[[get_crop_cols(c)[0], get_crop_cols(c)[1]]].corr().iloc[0, 1] for c in ["Rice", "Wheat", "Maize"]}
        insight("Correlation between area & production — " + ", ".join(f"<b>{k}</b>: {v:.2f}" for k, v in corrs.items()) +
                ". Values close to 1 confirm that area expansion is a strong driver of production for these staples.")
        data_table(scat)


    # -------------------------------------------------------------- QUESTIONS
    with tab_q:

        # Q1: Year-wise trend of rice production across states (top 3)
        st.subheader("Q1. Year-wise Trend of Rice Production — Top 3 States")
        top3_states = df_full.groupby("State Name")["RICE PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(3).index.tolist()
        q1 = df_full[df_full["State Name"].isin(top3_states)].groupby(["Year", "State Name"], as_index=False)["RICE PRODUCTION (1000 tons)"].sum()
        fig = px.line(q1, x="Year", y="RICE PRODUCTION (1000 tons)", color="State Name", template=PLOT_TEMPLATE,
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, width="stretch")
        insight(f"Top 3 rice states by cumulative output are <b>{', '.join(top3_states)}</b>. "
                "All three show a generally rising trend with some volatility around monsoon-deficit years.")
        data_table(q1)

        # Q2: Top 5 districts by wheat yield increase over last 5 years
        st.subheader("Q2. Top 5 Districts by Wheat Yield Increase (Last 5 Years)")
        last5 = sorted(df_full["Year"].unique())[-5:]
        y_start, y_end = last5[0], last5[-1]
        w_start = df_full[df_full["Year"] == y_start].groupby("Dist Name")["WHEAT YIELD (Kg per ha)"].mean()
        w_end = df_full[df_full["Year"] == y_end].groupby("Dist Name")["WHEAT YIELD (Kg per ha)"].mean()
        delta = (w_end - w_start).dropna().sort_values(ascending=False).head(5).reset_index()
        delta.columns = ["Dist Name", "Yield Increase (Kg/ha)"]
        fig = px.bar(delta, x="Dist Name", y="Yield Increase (Kg/ha)", color="Yield Increase (Kg/ha)",
                     color_continuous_scale="Greens", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"Between {y_start} and {y_end}, <b>{delta.iloc[0]['Dist Name']}</b> posted the sharpest wheat "
                f"yield gain (+{delta.iloc[0]['Yield Increase (Kg/ha)']:,.0f} kg/ha) — likely reflecting seed/input upgrades or better rainfall.")
        data_table(delta)

        # Q3: States with highest growth in oilseed production (5-year growth rate)
        st.subheader("Q3. States with Highest Oilseed Production Growth (5-Year Growth Rate)")
        o_start = df_full[df_full["Year"] == y_start].groupby("State Name")["OILSEEDS PRODUCTION (1000 tons)"].sum()
        o_end = df_full[df_full["Year"] == y_end].groupby("State Name")["OILSEEDS PRODUCTION (1000 tons)"].sum()
        growth = ((o_end - o_start) / o_start.replace(0, np.nan) * 100).dropna().sort_values(ascending=False).head(7).reset_index()
        growth.columns = ["State Name", "Growth Rate (%)"]
        fig = px.bar(growth, x="State Name", y="Growth Rate (%)", color="Growth Rate (%)",
                     color_continuous_scale="Purples", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{growth.iloc[0]['State Name']}</b> shows the fastest oilseed production growth "
                f"({growth.iloc[0]['Growth Rate (%)']:.1f}%) between {y_start}–{y_end}.")
        data_table(growth)

        # Q4: District-wise correlation between area and production (Rice, Wheat, Maize)
        st.subheader("Q4. District-wise Correlation Between Area & Production — Rice, Wheat, Maize")
        corr_rows = []
        for crop in ["Rice", "Wheat", "Maize"]:
            a, p, y = get_crop_cols(crop)
            dist_g = df_full.groupby("Dist Name")[[a, p]].sum()
            corr_rows.append({"Crop": crop, "Correlation (Area vs Production)": dist_g[a].corr(dist_g[p])})
        corr_df = pd.DataFrame(corr_rows)
        fig = px.bar(corr_df, x="Crop", y="Correlation (Area vs Production)", color="Crop",
                     color_discrete_sequence=COLOR_SEQ, template=PLOT_TEMPLATE, range_y=[0, 1])
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")
        insight("All three staples show strong positive correlation between cultivated area and total "
                "production at the district level — " +
                ", ".join(f"<b>{row['Crop']}</b>: {row['Correlation (Area vs Production)']:.2f}" for _, row in corr_df.iterrows()) + ".")
        data_table(corr_df)

        # Q5: Yearly production growth of cotton in top 5 cotton producing states
        st.subheader("Q5. Yearly Production Growth of Cotton — Top 5 Cotton States")
        top5_cotton = df_full.groupby("State Name")["COTTON PRODUCTION (1000 tons)"].sum().sort_values(ascending=False).head(5).index.tolist()
        q5 = df_full[df_full["State Name"].isin(top5_cotton)].groupby(["Year", "State Name"], as_index=False)["COTTON PRODUCTION (1000 tons)"].sum()
        fig = px.line(q5, x="Year", y="COTTON PRODUCTION (1000 tons)", color="State Name", template=PLOT_TEMPLATE,
                      color_discrete_sequence=COLOR_SEQ)
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, width="stretch")
        insight(f"Top-5 cotton states are <b>{', '.join(top5_cotton)}</b>. A sharp acceleration is visible "
                "in the 2000s, coinciding with the introduction of Bt cotton varieties in India.")
        data_table(q5)

        # Q6: Districts with highest groundnut production in 2017
        st.subheader("Q6. Districts with Highest Groundnut Production (2017)")
        gn17 = df_full[df_full["Year"] == df_full["Year"].max()].groupby("Dist Name", as_index=False)["GROUNDNUT PRODUCTION (1000 tons)"].sum()
        gn17 = gn17.sort_values("GROUNDNUT PRODUCTION (1000 tons)", ascending=False).head(10)
        fig = px.bar(gn17, x="Dist Name", y="GROUNDNUT PRODUCTION (1000 tons)", color="GROUNDNUT PRODUCTION (1000 tons)",
                     color_continuous_scale="Oranges", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"In the latest year available ({int(df_full['Year'].max())}), <b>{gn17.iloc[0]['Dist Name']}</b> "
                f"led groundnut production with {gn17.iloc[0]['GROUNDNUT PRODUCTION (1000 tons)']:,.1f} kt.")
        data_table(gn17)

        # Q7: Annual average maize yield across all states
        st.subheader("Q7. Annual Average Maize Yield Across All States")
        q7 = df_full.groupby("Year", as_index=False)["MAIZE YIELD (Kg per ha)"].mean()
        fig = px.line(q7, x="Year", y="MAIZE YIELD (Kg per ha)", template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT])
        fig.update_traces(line_width=3)
        st.plotly_chart(fig, width="stretch")
        insight(f"Average maize yield rose from ~{q7.iloc[0]['MAIZE YIELD (Kg per ha)']:,.0f} kg/ha "
                f"in {int(q7.iloc[0]['Year'])} to ~{q7.iloc[-1]['MAIZE YIELD (Kg per ha)']:,.0f} kg/ha "
                f"by {int(q7.iloc[-1]['Year'])}, reflecting hybrid seed adoption and better agronomy nationwide.")
        data_table(q7)

        # Q8: Total area cultivated for oilseeds in each state
        st.subheader("Q8. Total Area Cultivated for Oilseeds — By State")
        q8 = df_full.groupby("State Name", as_index=False)["OILSEEDS AREA (1000 ha)"].sum().sort_values(
            "OILSEEDS AREA (1000 ha)", ascending=False)
        fig = px.bar(q8, x="State Name", y="OILSEEDS AREA (1000 ha)", color="OILSEEDS AREA (1000 ha)",
                     color_continuous_scale="Purples", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{q8.iloc[0]['State Name']}</b> allocates the most cumulative land to oilseeds "
                f"({q8.iloc[0]['OILSEEDS AREA (1000 ha)']:,.0f} thousand ha, 1966–2017).")
        data_table(q8)

        # Q9: Districts with the highest rice yield
        st.subheader("Q9. Districts with the Highest Average Rice Yield")
        rice_area_thresh = df_full[df_full["RICE AREA (1000 ha)"] > 1]
        q9 = rice_area_thresh.groupby("Dist Name", as_index=False)["RICE YIELD (Kg per ha)"].mean().sort_values(
            "RICE YIELD (Kg per ha)", ascending=False).head(10)
        fig = px.bar(q9, x="Dist Name", y="RICE YIELD (Kg per ha)", color="RICE YIELD (Kg per ha)",
                     color_continuous_scale="Greens", template=PLOT_TEMPLATE)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig, width="stretch")
        insight(f"<b>{q9.iloc[0]['Dist Name']}</b> records the highest average rice yield "
                f"({q9.iloc[0]['RICE YIELD (Kg per ha)']:,.0f} kg/ha) among districts with meaningful rice area (>1000 ha).")
        data_table(q9)

        # Q10: Compare production of wheat and rice for top 5 states over 10 years
        st.subheader("Q10. Wheat vs Rice Production — Top 5 States, Last 10 Years")
        last10 = sorted(df_full["Year"].unique())[-10:]
        d10 = df_full[df_full["Year"].isin(last10)]
        top5_combo = d10.groupby("State Name")[["RICE PRODUCTION (1000 tons)", "WHEAT PRODUCTION (1000 tons)"]].sum().sum(axis=1).sort_values(ascending=False).head(5).index.tolist()
        q10 = d10[d10["State Name"].isin(top5_combo)].groupby(["State Name", "Year"], as_index=False)[
            ["RICE PRODUCTION (1000 tons)", "WHEAT PRODUCTION (1000 tons)"]].sum()
        q10_melt = q10.melt(id_vars=["State Name", "Year"], var_name="Crop", value_name="Production (1000 tons)")
        fig = px.bar(q10_melt, x="Year", y="Production (1000 tons)", color="Crop", facet_col="State Name",
                     facet_col_wrap=3, barmode="group", template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT, ACCENT2])
        fig.update_xaxes(type="category")
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        st.plotly_chart(fig, width="stretch")
        insight(f"Among the top-5 rice+wheat producing states (<b>{', '.join(top5_combo)}</b>), "
                f"the mix between rice and wheat varies sharply by region — Punjab/UP skew wheat-heavy, "
                "while eastern/southern states skew rice-heavy.")
        data_table(q10)

# ============================================================================
# MODE 2 : INDIA MAP EXPLORER (PhonePe-Pulse style)
# ============================================================================
else:
    import requests

    GEOJSON_URLS = [
        "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea3af1/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States",
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
    ]

    # Common spelling differences between various India geojson sources and the
    # ICRISAT dataset's state names — normalized so every state matches correctly
    # and none of them are silently dropped from the map.
    GEOJSON_NAME_ALIASES = {
        "Orissa": "Odisha",
        "Uttaranchal": "Uttarakhand",
        "Pondicherry": "Puducherry",
        "NCT of Delhi": "Delhi",
        "Delhi Ut": "Delhi",
        "Jammu & Kashmir": "Jammu and Kashmir",
        "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
        "Andaman & Nicobar": "Andaman and Nicobar Islands",
        "Dadra And Nagar Haveli": "Dadra and Nagar Haveli",
        "Dadra and Nagar Haveli and Daman and Diu": "Dadra and Nagar Haveli",
        "Arunanchal Pradesh": "Arunachal Pradesh",
    }

    @st.cache_data(show_spinner="Loading India state boundaries...")
    def load_geojson():
        for url in GEOJSON_URLS:
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200:
                    gj = r.json()
                    # detect the property key holding the state name
                    sample_props = gj["features"][0]["properties"]
                    key = None
                    for cand in ["ST_NM", "NAME_1", "st_nm", "name"]:
                        if cand in sample_props:
                            key = cand
                            break
                    if key is None:
                        key = list(sample_props.keys())[0]
                    # normalize state-name spelling so every feature lines up with
                    # both the dataset AND gets picked up for the "full India" base layer
                    for feat in gj["features"]:
                        nm = feat["properties"].get(key)
                        if nm in GEOJSON_NAME_ALIASES:
                            feat["properties"][key] = GEOJSON_NAME_ALIASES[nm]
                    return gj, key
            except Exception:
                continue
        return None, None

    def _feature_centroid(geometry):
        """Rough (non area-weighted) centroid for placing a state name label."""
        pts = []

        def _walk(node):
            if isinstance(node[0], (int, float)):
                pts.append(node)
            else:
                for sub in node:
                    _walk(sub)

        _walk(geometry["coordinates"])
        if not pts:
            return None
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)

    geojson, geo_key = load_geojson()

    st.sidebar.subheader("Map Filters")
    category = st.sidebar.selectbox("Crop Category", list(CROP_CATEGORIES.keys()))
    crop_options = [f"All {category} (Total)"] + list(CROP_CATEGORIES[category].keys())
    crop_choice = st.sidebar.selectbox("Crop", crop_options)
    metric = st.sidebar.radio("Metric", ["Production", "Area", "Yield"], horizontal=True)
    sel_year = st.sidebar.slider("Year", YEAR_MIN, YEAR_MAX, YEAR_MAX)
    state_pick_manual = st.sidebar.selectbox("Or pick a state directly", ["(none)"] + ALL_STATES)

    # District picker — once a state is picked above, only show that state's
    # districts here. If no state is picked yet, show every district.
    if state_pick_manual != "(none)":
        districts_for_dropdown = sorted(df_full.loc[df_full["State Name"] == state_pick_manual, "Dist Name"].dropna().unique().tolist())
        district_label = f"Or pick a district in {state_pick_manual}"
    else:
        districts_for_dropdown = sorted(df_full["Dist Name"].dropna().unique().tolist())
        district_label = "Or pick a district directly (select a state above to narrow this list)"
    district_pick_manual = st.sidebar.selectbox(district_label, ["(none)"] + districts_for_dropdown)

    # Resolve columns for the chosen crop/category + metric
    is_total = crop_choice.startswith("All ")
    if is_total:
        area_col = category_metric_col(category, "AREA")
        prod_col = category_metric_col(category, "PRODUCTION")
        yield_col = category_metric_col(category, "YIELD")
    else:
        area_col, prod_col, yield_col = get_crop_cols(crop_choice)

    metric_col_map = {"Area": area_col, "Production": prod_col, "Yield": yield_col}
    value_col = metric_col_map[metric]

    if value_col is None or (category in AREA_ONLY_CATEGORIES and metric != "Area"):
        st.sidebar.warning(f"⚠️ {metric} isn't available for this crop in the source data — showing Area instead.")
        metric = "Area"
        value_col = area_col

    st.title("🗺️ India Agriculture Explorer")
    st.caption(f"{crop_choice} · {metric} · Year {sel_year} — hover a state for details, click to drill into districts")

    df_year = df_full[df_full["Year"] == sel_year]

    if metric == "Yield":
        state_agg = df_year.groupby("State Name").apply(
            lambda g: (g[prod_col].sum() / g[area_col].sum() * 1000) if (area_col and g[area_col].sum() > 0) else np.nan
        ).reset_index(name=value_col)
    else:
        state_agg = df_year.groupby("State Name", as_index=False)[value_col].sum()

    state_agg = state_agg.rename(columns={value_col: "value"})

    # Make sure every state shows up on the map (even ones with no data for this
    # crop/year) so the whole country gets colored in, not just a handful of states.
    state_agg = pd.DataFrame({"State Name": ALL_STATES}).merge(state_agg, on="State Name", how="left")
    state_agg["value"] = state_agg["value"].fillna(0)

    # enrich hover info: area, production, yield side by side (when available)
    if area_col:
        state_agg = state_agg.merge(df_year.groupby("State Name", as_index=False)[area_col].sum().rename(columns={area_col: "Area (1000 ha)"}), on="State Name", how="left")
    if prod_col:
        state_agg = state_agg.merge(df_year.groupby("State Name", as_index=False)[prod_col].sum().rename(columns={prod_col: "Production (1000 tons)"}), on="State Name", how="left")
    state_agg["Rank"] = state_agg["value"].rank(ascending=False, method="min").astype("Int64")
    state_agg = state_agg.sort_values("value", ascending=False)

    col_map, col_side = st.columns([2.1, 1])

    selected_state = None
    selected_district = None

    with col_map:
        if geojson is not None:
            all_geo_names = sorted({
                f["properties"].get(geo_key) for f in geojson["features"] if f["properties"].get(geo_key)
            })

            fig = go.Figure()

            # Base layer: every state/UT in the geojson, light grey, so the full
            # India outline (incl. J&K, NE states, islands) always renders even
            # for states the ICRISAT dataset has no data for.
            fig.add_trace(go.Choropleth(
                geojson=geojson, locations=all_geo_names, z=[0] * len(all_geo_names),
                featureidkey=f"properties.{geo_key}",
                colorscale=[[0, "#e9ebee"], [1, "#e9ebee"]],
                showscale=False, marker_line_color="black", marker_line_width=0.9,
                hoverinfo="skip",
            ))

            # Data layer: only the states present in the ICRISAT dataset, colored
            # by the selected crop/metric.
            hover_extra = ""
            customdata_cols = []
            if "Area (1000 ha)" in state_agg.columns:
                hover_extra += "Area: %{customdata[0]:,.1f} (1000 ha)<br>"
                customdata_cols.append("Area (1000 ha)")
            if "Production (1000 tons)" in state_agg.columns:
                idx = len(customdata_cols)
                hover_extra += f"Production: %{{customdata[{idx}]:,.1f}} (1000 tons)<br>"
                customdata_cols.append("Production (1000 tons)")

            fig.add_trace(go.Choropleth(
                geojson=geojson, locations=state_agg["State Name"], z=state_agg["value"],
                featureidkey=f"properties.{geo_key}",
                colorscale=px.colors.sequential.Turbo,
                marker_line_color="black", marker_line_width=0.9,
                colorbar=dict(title=metric),
                customdata=state_agg[customdata_cols].values if customdata_cols else None,
                text=state_agg["State Name"],
                hovertemplate="<b>%{text}</b><br>" + metric + ": %{z:,.1f}<br>" + hover_extra + "<extra></extra>",
            ))

            # State-name labels directly on the map (like a reference political map)
            label_lons, label_lats, label_names = [], [], []
            for feat in geojson["features"]:
                nm = feat["properties"].get(geo_key)
                c = _feature_centroid(feat["geometry"])
                if nm and c:
                    label_lons.append(c[0])
                    label_lats.append(c[1])
                    label_names.append(nm)
            fig.add_trace(go.Scattergeo(
                lon=label_lons, lat=label_lats, text=label_names, mode="text",
                textfont=dict(size=8, color="black"), hoverinfo="skip", showlegend=False,
            ))

            fig.update_geos(
                visible=False,
                projection_type="mercator",
                lataxis_range=[5, 39],
                lonaxis_range=[66, 99],
                resolution=50,
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=650)
            event = st.plotly_chart(fig, width="stretch", on_select="rerun", key="india_map",
                                     selection_mode="points")
            if event and event.get("selection", {}).get("points"):
                pt = event["selection"]["points"][0]
                loc = pt.get("location") or pt.get("hovertext")
                if loc in ALL_STATES:
                    selected_state = loc
        else:
            st.warning("Couldn't load India map boundaries (no internet access / source unavailable). "
                       "Showing a state ranking instead.")
            fig = px.bar(state_agg.head(20), x="value", y="State Name", orientation="h",
                         color="value", color_continuous_scale=px.colors.sequential.Turbo, template=PLOT_TEMPLATE)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False, height=560)
            st.plotly_chart(fig, width="stretch")

    if state_pick_manual != "(none)":
        selected_state = state_pick_manual

    # If a district was picked directly, resolve its parent state and jump straight
    # to that district's drill-down.
    if district_pick_manual != "(none)":
        selected_district = district_pick_manual
        dist_state_lookup = df_full.drop_duplicates("Dist Name").set_index("Dist Name")["State Name"]
        selected_state = dist_state_lookup.get(district_pick_manual, selected_state)

    with col_side:
        st.markdown("#### 🏆 State Ranking")
        top_display = state_agg[["State Name", "value", "Rank"]].rename(columns={"value": metric}).head(10)
        st.dataframe(top_display, width="stretch", hide_index=True)

    st.markdown("---")

    if selected_state:
        st.subheader(f"📍 District Drill-down — {selected_state} ({sel_year})")
        dist_year = df_year[df_year["State Name"] == selected_state]
        if metric == "Yield":
            dist_agg = dist_year.groupby("Dist Name").apply(
                lambda g: (g[prod_col].sum() / g[area_col].sum() * 1000) if (area_col and g[area_col].sum() > 0) else np.nan
            ).reset_index(name=metric)
        else:
            dist_agg = dist_year.groupby("Dist Name", as_index=False)[value_col].sum().rename(columns={value_col: metric})
        dist_agg = dist_agg.sort_values(metric, ascending=False)

        # add extra hover context (area/production) for the district bar chart
        dist_hover_cols = []
        if area_col:
            dist_agg = dist_agg.merge(
                dist_year.groupby("Dist Name", as_index=False)[area_col].sum().rename(columns={area_col: "Area (1000 ha)"}),
                on="Dist Name", how="left")
            dist_hover_cols.append("Area (1000 ha)")
        if prod_col:
            dist_agg = dist_agg.merge(
                dist_year.groupby("Dist Name", as_index=False)[prod_col].sum().rename(columns={prod_col: "Production (1000 tons)"}),
                on="Dist Name", how="left")
            dist_hover_cols.append("Production (1000 tons)")

        # highlight the district chosen from the sidebar dropdown (if any)
        dist_agg["Selected"] = dist_agg["Dist Name"] == selected_district if selected_district else False

        d1, d2 = st.columns([1.4, 1])
        with d1:
            fig = px.bar(dist_agg, x=metric, y="Dist Name", orientation="h", color=metric,
                         color_continuous_scale=px.colors.sequential.Turbo, template=PLOT_TEMPLATE,
                         hover_data=dist_hover_cols)
            fig.update_layout(coloraxis_showscale=False, yaxis_title="",
                               yaxis={"categoryorder": "total ascending"},
                               height=max(420, 26 * len(dist_agg)))
            if selected_district and selected_district in dist_agg["Dist Name"].values:
                fig.add_hline(y=selected_district, line_width=2, line_dash="dash", line_color=ACCENT)
            st.plotly_chart(fig, width="stretch")
        with d2:
            state_trend = df_full[df_full["State Name"] == selected_state]
            if metric == "Yield" and area_col and prod_col:
                trend = state_trend.groupby("Year").apply(
                    lambda g: (g[prod_col].sum() / g[area_col].sum() * 1000) if g[area_col].sum() > 0 else np.nan
                ).reset_index(name=metric)
            elif value_col:
                trend = state_trend.groupby("Year", as_index=False)[value_col].sum().rename(columns={value_col: metric})
            else:
                trend = pd.DataFrame()
            if len(trend):
                fig2 = px.line(trend, x="Year", y=metric, template=PLOT_TEMPLATE, color_discrete_sequence=[ACCENT])
                fig2.update_layout(height=300, title=f"{selected_state} — {metric} trend")
                st.plotly_chart(fig2, width="stretch")

        if selected_district and selected_district in dist_agg["Dist Name"].values:
            drow = dist_agg[dist_agg["Dist Name"] == selected_district].iloc[0]
            insight(f"<b>{selected_district}</b> (picked from the sidebar) recorded {crop_choice} {metric.lower()} "
                    f"of {drow[metric]:,.1f} in {selected_state} for {sel_year}.")
        elif not dist_agg.empty:
            insight(f"<b>{dist_agg.iloc[0]['Dist Name']}</b> is the leading district in {selected_state} for "
                    f"{crop_choice} {metric.lower()} in {sel_year} ({dist_agg.iloc[0][metric]:,.1f}).")
        data_table(dist_agg, "📄 View district-level data")
    else:
        st.info("👆 Click a state on the map, or pick a state/district from the sidebar, to see its district-wise "
                "breakdown, top districts, and multi-year trend.")

    data_table(state_agg, "📄 View state-level data for this year")
