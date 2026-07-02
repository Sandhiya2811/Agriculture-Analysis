# 🌾 India Agriculture Interactive Dashboard

An interactive **Streamlit + Plotly** dashboard built on the **ICRISAT District Level Data** (1966–2017), covering 311 districts across 20 Indian states. It offers rich exploratory analysis, answers to key agricultural questions, and a PhonePe-Pulse-style interactive India map for drilling down into state and district-level crop data.

---

## 📸 Screenshots

### Insights & Questions Dashboard
Exploratory analysis with 15 EDA charts and 10 key-question deep dives, each with an auto-generated insight callout.

![Insights & Questions Dashboard]
<img width="1920" height="1140" alt="Screenshot 2026-07-01 125719" src="https://github.com/user-attachments/assets/79c18efb-8995-4389-9402-0327f9f3e5b3" />



### India Map Explorer (PhonePe-Pulse style)
A full India choropleth map — pick a crop, category, metric, and year, then click any state to drill into its districts.

![India Map Explorer]
<img width="1920" height="1140" alt="Screenshot 2026-07-01 125814" src="https://github.com/user-attachments/assets/54e3d9fa-408b-4415-8883-fcdbf20558f2" />



---

## ✨ Features

- **20 states · 311 districts · 1966–2017** of ICRISAT crop data
- **6 crop categories** — Food Grains, Pulses, Oilseeds, Commercial/Cash Crops, Horticulture, Fodder
- **15 Exploratory Data Analysis charts** — top producers, trends, correlations, composition, and more
- **10 Key Question deep-dives** — growth rates, yield changes, district rankings, and more
- **Interactive India map** with:
  - Full country outline (including J&K, North-East states, and island UTs)
  - Choropleth coloring by Production / Area / Yield
  - State name labels directly on the map
  - Click-to-drill into district-level breakdowns and multi-year trends
  - Dropdowns to jump directly to a state or a district (auto-scoped to the selected state)
- Auto-generated **insight callouts** under every chart
- Expandable **data tables** for every chart

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) — app framework & UI
- [Plotly Express / Graph Objects](https://plotly.com/python/) — charts & choropleth map
- [Pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — data processing
- [Requests](https://docs.python-requests.org/) — fetching India state GeoJSON boundaries

---

## 📂 Project Structure

```
agriculture_project/
├── app.py                          # Main Streamlit app
├── ICRISAT-District Level Data - ICRISAT-District Level Data.csv   # Dataset
├── Agri_data_Analysis.ipynb
├── Agriculture_explorer.pbix
├── requirement.txt
└── README.md
```
---

## 📈 Power BI Dashboard
A companion **Power BI** dashboard for quick, interactive insights on the ICRISAT district-level data.

![Power BI Dashboard]

<img width="1372" height="776" alt="Screenshot 2026-07-02 134440" src="https://github.com/user-attachments/assets/c8fce8bf-ff56-4424-b92a-61fe2ded32c7" />

---

<img width="1366" height="764" alt="Screenshot 2026-07-02 134454" src="https://github.com/user-attachments/assets/588b6267-9856-4a6e-b4da-ab6632db6f94" />

---

<img width="1368" height="759" alt="Screenshot 2026-07-02 134521" src="https://github.com/user-attachments/assets/6dca2b53-1cf5-46ef-9e94-a2e6bd1e10bf" />


---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Sandhiya2811/agriculture_project.git
cd agriculture_project
```

### 2. Install dependencies
```bash
pip install streamlit pandas numpy plotly requests
```

### 3. Add the dataset
Place `ICRISAT-District Level Data - ICRISAT-District Level Data.csv` in the project root (same folder as `agriculture_dashboard.py`).

### 4. Run the app
```bash
streamlit run agriculture_dashboard.py
```

The app will open at **http://localhost:8501**.

> ℹ️ The India Map Explorer view fetches state boundary GeoJSON files from the internet on first load — an active internet connection is required for the map to render.

---

## 📊 Data Source

**ICRISAT District Level Data** — a long-running agricultural dataset covering area, production, and yield for major crops across Indian districts from 1966 to 2017.

---

## 📝 Notes

- `-1` values in the raw dataset are treated as missing (`NaN`).
- "Orissa" is normalized to "Odisha" for consistency with current naming.
- States/UTs not present in the ICRISAT dataset (e.g. J&K, North-East states) still render on the map as a neutral grey base layer so the full India outline is always visible, even though no crop data exists for them in this dataset.

---

## 📄 License

This project is for educational and analytical purposes. Please check the ICRISAT data usage terms before redistributing the dataset.
