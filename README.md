# 🗺️ India State Explorer — Streamlit App

An interactive India map dashboard built with Streamlit, pandas, and Plotly.

## Features
- **Hover to zoom** — states scale up with a spring animation on hover
- **Choropleth coloring** — map automatically color-codes states by any chosen metric
- **5 data categories** — Demographics, Economy, Health, Education, Agriculture
- **Click any state** — detailed stats panel updates instantly
- **3 charts** — Top 10 bar chart, radar profile, and distribution histogram
- **Full data table** — sortable, with min/max highlighting

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**
   ```bash
   streamlit run app.py
   ```

3. Open your browser at `http://localhost:8501`

## Project Structure
```
india_map_app/
├── app.py              ← Main Streamlit app
├── india_clean.svg     ← Cleaned India SVG map
├── requirements.txt    ← Python dependencies
└── README.md
```

## Using Your Own Data
Replace the `load_data()` function in `app.py` with:
```python
@st.cache_data
def load_data():
    df = pd.read_csv("your_data.csv")   # or read_excel()
    return df
```
Make sure your CSV has a `State` column with state names matching the ones in the app,
and an `ID` column with codes like `INMH`, `INUP` etc.
