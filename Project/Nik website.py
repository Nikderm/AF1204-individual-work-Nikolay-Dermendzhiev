# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.23.1",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyodide-http>=0.2.2",
#     "requests>=2.33.1",
#     "tabulate>=0.10.0",
#     "yfinance>=0.2.54",
#     "pypdf>=6.0.0",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():

    import marimo as mo
    import pandas as pd

    # Require micropip to install packages in the WASM environment
    try:
        import micropip
    except ImportError:
        micropip = None  # Not available when running locally (only in WASM/Pyodide)
    return mo, pd


@app.cell
def _(pd):
    # 1: Setup & Data Prep

    # Get data ready for the dynamic webpage

    # Note: The local-data-loading approach below does not work due to GitHub Pages compression issue
    #===============================================================================================
    # Must place data file in subfolder 'public' of the folder where the marimo notebook is located
    # (required to locate and include the data when exporting as html-wasm)
    # 
    #filename = mo.notebook_location() / "public" / 'sp500_ZScore_AvgCostofDebt.csv'
    #df_final = pd.read_csv(str(filename))

    # Instead, use a raw gist URL approach to remotely load the data (already hosted online)  
    #=======================================================================================
    csv_url = "https://gist.githubusercontent.com/DrAYim/80393243abdbb4bfe3b45fef58e8d3c8/raw/ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/sp500_ZScore_AvgCostofDebt.csv"

    df_final = pd.read_csv(csv_url)  # as opposed to pd.read_csv('public/sp500_ZScore_AvgCostofDebt.csv')

    df_final = df_final.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])
    # Filter outliers to reduce distortion in visualizations
    df_final = df_final[(df_final['AvgCost_of_Debt'] < 5)]   # 5 means 500%
    #df_final = df_final[(df_final['AvgCost_of_Debt'] > 0) & (df_final['Z_Score_lag'] < 20)]
    df_final['Debt_Cost_Percent'] = df_final['AvgCost_of_Debt'] * 100

    # For AFKLM tab, use European airline stocks dataset
    # Create a simulated dataset for European airlines
    european_airlines_data = {
        'Name': [
            'Air France-KLM', 'Lufthansa Group', 'Ryanair Holdings', 'EasyJet',
            'IAG (British Airways)', 'Airbus', 'Safran', 'Thales',
            'Turkish Airlines', 'Wizz Air', 'SAS AB', 'Finnair',
            'Norwegian Air', 'Aegean Airlines', 'TAP Air Portugal', 'Icelandair'
        ],
        'Sector_Key': ['Airlines'] * 16,
        'Market_Cap': [
            5.2e9, 8.1e9, 18.5e9, 4.3e9, 12.7e9, 85.6e9, 52.3e9, 28.9e9,
            9.8e9, 3.1e9, 1.2e9, 1.0e9, 2.4e9, 1.5e9, 2.8e9, 0.9e9
        ],  # in USD
        'AvgCost_of_Debt': [
            0.045, 0.038, 0.025, 0.042, 0.048, 0.032, 0.029, 0.035,
            0.051, 0.055, 0.062, 0.041, 0.058, 0.033, 0.047, 0.044
        ],  # decimal
        'Z_Score_lag': [
            2.1, 2.8, 3.5, 2.3, 1.9, 3.2, 3.0, 2.7,
            2.5, 1.7, 1.3, 2.0, 1.5, 2.9, 2.2, 2.4
        ]
    }
    df_airlines = pd.DataFrame(european_airlines_data)
    df_airlines['Debt_Cost_Percent'] = df_airlines['AvgCost_of_Debt'] * 100
    df_airlines['Market_Cap_B'] = df_airlines['Market_Cap'] / 1e9

    # Add Yahoo Finance ticker symbols for detail lookups
    _airline_tickers = {
        'Air France-KLM': 'AF.PA',
        'Lufthansa Group': 'LHA.DE',
        'Ryanair Holdings': 'RYAAY',
        'EasyJet': 'EZJ.L',
        'IAG (British Airways)': 'IAG.L',
        'Airbus': 'AIR.PA',
        'Safran': 'SAF.PA',
        'Thales': 'HO.PA',
        'Turkish Airlines': 'THYAO.IS',
        'Wizz Air': 'WIZZ.L',
        'SAS AB': 'SAS-B.ST',
        'Finnair': 'FIA1S.HE',
        'Norwegian Air': 'NAS.OL',
        'Aegean Airlines': 'AEGN.AT',
        'TAP Air Portugal': None,
        'Icelandair': 'ICEAIR.IC',
    }
    df_airlines['Ticker'] = df_airlines['Name'].map(_airline_tickers)

    # Detect ticker column in S&P 500 data (may be named Symbol, Ticker, etc.)
    _ticker_col = next(
        (c for c in df_final.columns if c.lower() in ['symbol', 'ticker', 'stock']), None
    )
    if _ticker_col and _ticker_col != 'Ticker':
        df_final = df_final.rename(columns={_ticker_col: 'Ticker'})
    elif _ticker_col is None:
        df_final['Ticker'] = None
    return df_airlines, df_final


@app.cell
def _(df_airlines, df_final, mo):
    # 2: Define the UI Controls (The "Inputs")

    # create the widgets here. In marimo, assigning them to a variable makes them available globally.

    # Convert Market Cap to Billions for easier reading
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9

    # AFKLM-specific controls
    company_options = sorted(df_airlines['Name'].unique().tolist())
    comparison_companies = mo.ui.multiselect(
        options=company_options,
        value=company_options,  # Default to all airlines
        label="Compare Companies",
    )
    risk_threshold = mo.ui.slider(
        start=0,
        stop=40,
        step=1,
        value=12,
        label="Risk zone threshold (% Borrowing Cost)"
    )
    afklm_cap_slider = mo.ui.slider(
        start=0,
        stop=100,
        step=1,
        value=0,
        label="Min Market Cap ($ Billions)"
    )
    dataset_toggle = mo.ui.dropdown(
        options=["European Airlines", "S&P 500"],
        value="European Airlines",
        label="Dataset"
    )
    search_input = mo.ui.text(
        placeholder="Search companies...",
        label="🔍 Search Companies"
    )
    # 4. Groq AI controls
    ai_api_key = mo.ui.text(
        kind="password",
        placeholder="gsk_...",
        label="🔑 Groq API Key",
    )
    ai_question = mo.ui.text_area(
        placeholder="e.g. What are the main financial risks for Air France-KLM?",
        label="💬 Question",
        rows=7,
    )
    ask_button = mo.ui.run_button(label="Ask AI")
    pdf_upload = mo.ui.file(
        filetypes=[".pdf"],
        multiple=False,
        label="📄 Upload Earnings Report PDF",
    )
    return (
        afklm_cap_slider,
        ai_api_key,
        ai_question,
        ask_button,
        comparison_companies,
        dataset_toggle,
        pdf_upload,
        risk_threshold,
        search_input,
    )


@app.cell
async def _(micropip):
    # Await installation of packages in the WASM environment
    # Install each package individually so one failure doesn't block the rest
    if micropip is not None:
        for _pkg in ['plotly', 'requests', 'yfinance', 'pypdf']:
            try:
                await micropip.install(_pkg, keep_going=True)
            except Exception:
                pass
    # pyodide_http re-routes requests through XMLHttpRequest so HTTP calls work client-side
    try:
        import pyodide_http
        pyodide_http.patch_all()
    except ImportError:
        pass  # Running locally — requests works natively, no patch needed

    import plotly.express as px
    import requests
    try:
        import yfinance as yf
    except ImportError:
        yf = None  # yfinance not available in this environment
    return px, requests, yf


@app.cell
def _(pd, px):
    # 4: The Visualizations

    #=========================================
    # Plot 2: Personal Travel Map (Hardcoded demo data for the 'Hobbies' tab)
    #=========================================
    # This simulates travel history data  
    travel_data = pd.DataFrame({
        'City': ['London', 'Sofia', 'Croatia', 'Sydney', 'Paris', 'Milan', 'Montenegro', 'Columbia', 'Serbia', 'Romania', 'Dubai', 'Hong Kong', 'Germany', 'Austria', 'North Macedonia', 'Spain', 'Turkey', 'Monaco', 'greece'],
        'Lat': [51.5, 42.69, 45.1, -33.8, 48.8, 45.4, 42.5, 4.6, 44.8, 45.7, 24.5, 22.3, 51.1, 48.2, 41.6, 36.7, 39.9, 43.7, 37.9],
        'Lon': [-0.1, 23.32, 15.2, 151.2, 2.3, 8.9, 19.2, -74.0, 20.0, 28.6, 55.1, 114.1, 10.4, 16.3, 21.0, -4.4, 35.2, 7.4, 23.7],
        'Visit_Year_str': ['2026', '2020', '2022', '2018', '2025', '2025', '2022', '2012', '2022', '2023', '2019', '2024', '2023', '2025', '2025', '2023', '2022', '2024', '2024']
    })

    years = sorted(travel_data['Visit_Year_str'].unique(), key=int)  # -> ['2021','2022','2023','2024']

    fig_travel = px.scatter_geo(
        travel_data,
        lat='Lat', lon='Lon',
        hover_name='City',
        color='Visit_Year_str',
        category_orders={'Visit_Year_str': years},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        projection="natural earth",
        title="My Travel Footprint",
        #template='plotly_white',
        labels={'Visit_Year_str': 'Visit Year'}
    )

    fig_travel.update_traces(marker=dict(size=12)); # use trailing semicolon to suppress output
    return (fig_travel,)


@app.cell
def _(
    afklm_cap_slider,
    comparison_companies,
    dataset_toggle,
    df_airlines,
    df_final,
    mo,
    px,
    risk_threshold,
):
    # 5a: Build AFKLM Credit Risk Charts (Reactive cell that accesses widget values)

    # Choose dataset based on toggle
    if dataset_toggle.value == "S&P 500":
        base_df = df_final.copy()
    else:
        base_df = df_airlines.copy()

    # Filter by selected companies and market cap
    selected_companies = base_df[
        (base_df['Name'].isin(comparison_companies.value)) &
        (base_df['Market_Cap_B'] >= afklm_cap_slider.value)
    ]
    if selected_companies.empty:
        selected_companies = base_df.copy()

    # Highlight Air France-KLM
    selected_companies = selected_companies.copy()
    selected_companies['Is_AFKLM'] = selected_companies['Name'].apply(
        lambda x: 'Air France-KLM' if x == 'Air France-KLM' else 'Other'
    )

    high_risk = selected_companies[selected_companies['Debt_Cost_Percent'] >= risk_threshold.value]
    low_risk = selected_companies[selected_companies['Debt_Cost_Percent'] < risk_threshold.value]
    risk_summary = (
        f"{len(selected_companies)} selected companies · "
        f"{len(high_risk)} above risk threshold · "
        f"{len(low_risk)} below risk threshold"
    )

    dataset_label = dataset_toggle.value
    fig_afklm_zscore = px.scatter(
        selected_companies,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        color='Name',
        size='Market_Cap_B',
        hover_name='Name',
        title=f'{dataset_label}: Altman Z-Score vs Borrowing Cost',
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)', 'Market_Cap_B': 'Market Cap ($B)'},
        template='presentation',
        width=900,
    )
    fig_afklm_zscore.add_vline(
        x=1.81,
        line_dash='dash',
        line_color='grey',
        annotation=dict(text='Distress threshold', showarrow=False, yanchor='bottom', y=1.02, yref='paper')
    )
    fig_afklm_zscore.add_vline(
        x=2.99,
        line_dash='dash',
        line_color='grey',
        annotation=dict(text='Safe threshold', showarrow=False, yanchor='bottom', y=0.98, yref='paper')
    )

    # Box-and-whisker plot of borrowing costs by risk zone (all selected companies)
    risk_zone_df = selected_companies.copy()
    risk_zone_df['Risk_Zone'] = risk_zone_df['Z_Score_lag'].apply(
        lambda z: 'Distress' if z < 1.81 else ('Safe' if z > 2.99 else 'Grey')
    )
    zone_order = ['Grey', 'Safe', 'Distress']
    zone_colors = {'Grey': '#636EFA', 'Safe': '#EF553B', 'Distress': '#00CC96'}
    fig_cost_dist = px.box(
        risk_zone_df,
        x='Risk_Zone',
        y='Debt_Cost_Percent',
        color='Risk_Zone',
        category_orders={'Risk_Zone': zone_order},
        color_discrete_map=zone_colors,
        title='Borrowing Cost Distribution by Risk Zone',
        labels={'Debt_Cost_Percent': 'Average Cost of Debt (%)', 'Risk_Zone': 'Risk Zone'},
        template='presentation',
        width=900,
        height=450
    )

    fig_3d_firmsize = px.scatter_3d(
        selected_companies,
        x='Z_Score_lag',
        y='Debt_Cost_Percent',
        z='Market_Cap_B',
        color='Name',
        hover_name='Name',
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)', 'Market_Cap_B': 'Market Cap ($B)'},
        width=900,
        height=600
    )
    fig_3d_firmsize.update_traces(marker=dict(opacity=0.8))

    # --- Data Summary Card ---
    _afklm_row = selected_companies[selected_companies['Name'] == 'Air France-KLM']
    _peers = selected_companies[selected_companies['Name'] != 'Air France-KLM']

    if not _afklm_row.empty:
        _afklm_zscore = _afklm_row['Z_Score_lag'].iloc[0]
        _afklm_cod = _afklm_row['Debt_Cost_Percent'].iloc[0]
        _peer_median_cod = _peers['Debt_Cost_Percent'].median() if not _peers.empty else float('nan')

        # Z-Score zone classification
        if _afklm_zscore < 1.81:
            _zone = "**Distress Zone** (Z < 1.81)"
            _zone_color = "danger"
            _zscore_interp = "the company is statistically at elevated risk of financial distress"
        elif _afklm_zscore < 2.99:
            _zone = "**Grey Zone** (1.81 ≤ Z < 2.99)"
            _zone_color = "warn"
            _zscore_interp = "the company sits in an ambiguous zone — neither clearly safe nor in imminent distress"
        else:
            _zone = "**Safe Zone** (Z ≥ 2.99)"
            _zone_color = "success"
            _zscore_interp = "the company is in a financially stable position according to the Altman model"

        # Cost of debt vs peers interpretation
        if not _peers.empty and _peer_median_cod == _peer_median_cod:  # nan check
            _cod_diff = _afklm_cod - _peer_median_cod
            if abs(_cod_diff) < 0.5:
                _cod_interp = f"broadly in line with the peer median of **{_peer_median_cod:.2f}%**"
            elif _cod_diff > 0:
                _cod_interp = f"**{_cod_diff:.2f}pp above** the peer median of **{_peer_median_cod:.2f}%**, suggesting higher perceived credit risk"
            else:
                _cod_interp = f"**{abs(_cod_diff):.2f}pp below** the peer median of **{_peer_median_cod:.2f}%**, suggesting lower perceived credit risk"
            _peer_median_str = f"{_peer_median_cod:.2f}%"
        else:
            _cod_interp = "peer comparison not available (no peers in current filter)"
            _peer_median_str = "N/A"

        summary_card = mo.callout(
            mo.md(
                f"### 📋 Air France-KLM — Summary\n\n"
                f"| Metric | Value |\n"
                f"|---|---|\n"
                f"| Lagged Altman Z-Score | **{_afklm_zscore:.2f}** — {_zone} |\n"
                f"| Average Cost of Debt | **{_afklm_cod:.2f}%** |\n"
                f"| Peer Median Cost of Debt | **{_peer_median_str}** |\n\n"
                f"**Interpretation:** With a Z-Score of {_afklm_zscore:.2f}, {_zscore_interp}. "
                f"Its average borrowing cost of {_afklm_cod:.2f}% is {_cod_interp}."
            ),
            kind=_zone_color,
        )
    else:
        summary_card = mo.callout(
            mo.md("Air France-KLM is not present in the current filter. Adjust the dataset or company selection to see its summary."),
            kind="info",
        )

    tab_afklm_credit_risk = mo.vstack([
        mo.md("## AFKLM Credit Risk"),
        mo.callout(mo.md(f"Comparing Air France-KLM against {dataset_label} peers using credit risk metrics."), kind='info'),
        mo.callout(mo.md(risk_summary), kind='warn'),
        mo.hstack([dataset_toggle, comparison_companies, risk_threshold, afklm_cap_slider], justify='center', gap=2),
        mo.ui.plotly(fig_afklm_zscore),
        mo.ui.plotly(fig_cost_dist),
        mo.ui.plotly(fig_3d_firmsize),
        summary_card,
    ])
    return (tab_afklm_credit_risk,)


@app.cell
def _(fig_travel, mo, pd, tab_afklm_credit_risk):
    # 5b: The "Portfolio" Layout (a Multi-Tab Webpage)

    # Combine everything into a polished, tabbed interface using Markdown and mo.ui.tabs.

    # Define the content for each tab

    # --- Tab 1: CV / Profile ---
    # Using standard Markdown for formatting
    tab_cv = mo.md(
        """
        ### Aspiring Financial Analyst
        **Summary:**
        - Great interest in the financial and investment world. 
        - Retail trader managing a personal portfolio.

        **Education:**
        *   **BSc Accounting & Finance**, Bayes Business School (2025 - Present)
        *   *Relevant Modules:* Introduction to Data Science and AI Tools, Financial Accounting.
        *   **Stanmore College**, BTEC Business Level 3 Diploma (2023-2025).
        *   *Diploma in Business, with Distinction* (equivalent to A* grades in A-levels).
        *   **Kensington Park School**, GCSEs (2022-2023).
        *   *GCSEs in Maths (Grade 7), English (Grade 5)*
        *   **Royal School of Wolverhampton**, GCSEs (2020-2022).

        **Skills:**
        *   Financial Analysis
        *   Data Visualization
        *   Networking

        **Career**
        *   Moderately successful career in **Modelling**
        *   Worked with brands including: **Alexander Mcqueen, Uniqlo, Amiri, YSL**
        """
        )


    # --- Tab 2b: Stock Pitch ---
    tab_stock_pitch = mo.md(
        """
        📈 Stock Pitch

    .I am presenting an investment opportunity involving the gradual accumulation of a 5% minority stake in Air France–KLM (AF-KLM), listed on Euronext Paris.  

    AF-KLM owns irreplaceable assets, most notably key airport hubs at Paris Charles de Gaulle (CDG) and Amsterdam Schiphol (AMS). These assets represent a substantial hidden value that is not captured in the company's book value. The company's competitive position is further reinforced by its national importance and infrastructural monopoly. France holds 28% of the company, while Netherlands own 9.1%.  

    Although the company accumulated significant debt during the pandemic, meaningful progress has been made toward debt reduction. 	A Debt/EBITDA ratio of 1.7x shows that operating cash flows are sufficient to manage current debt. An investment today will represents a purchase of future net equity at an incredibly low price. Additionally, a P/E ratio of 3.4 at the end of Q3 2025 is unusually low, especially after a year of the company fulfilling its plans for debt reduction and fleet modernization. Overall, management seems good, and the company is decreasing its debts while generating good profits  

    My proposal is as follows:  

    To gradually accumulate approximately 5% of the company's equity (roughly €150–180 million) over a 4–5 month period, in order to minimize market impact. My goal is not control, but rather to take advantage of the value recovery, while the company returns to its historically (positive) capital size  

    My analysis shows that if there is a successful acquisition of a 5% stake in Air France–KLM over the next 2–4 years, the price will increase exponentially to a fair level and we will have taken advantage of the momentarily undervalued worth of the company.  

    Key risks to consider:  

    Their debt remains as the primary problem. Currently the total debt is around €15 billion, while net debt is around €7.8 billion, which is managed well with the high revenue that the company's is successfully generating  

    The company is also undergoing a significant fleet renewal program, involving massive capital expenditures (CAPeX), with completion planned by 2028–2030. This leads to a lower free cash flow (FCF) in the short term and increases the risk for revenue downturns over the next 2-3 years. However, upon completion, this modernization will provide a massive advantage and a high future FCF  

    AF-KLM is exposed to fuel price volatility and macroeconomic shocks such as recessions, global disruptions or the pandemic. That being said, the company's hedging programs mitigates these risks pretty well.  

    Of course these risks are unavoidable, however the positive long-term prospects outweigh them, and that the company's fair value is clearly way above its current market valuation.   

    I do not believe there is a risk of capital loss; rather, the risk lies in achieving a lower return than initially projected, with the worst-case scenario being a longer time period required for the investment to be realized. 
        """
    )

    # --- Tab 2f: Company Financials (loaded from CSV files) ---
    data_dir = str(mo.notebook_location() / "public")

    df_income_stmt = pd.read_csv(data_dir + "/Data (Sheet3).csv", encoding='latin-1')
    df_balance_sheet = pd.read_csv(data_dir + "/Data (Sheet2).csv", encoding='latin-1')
    df_comprehensive = pd.read_csv(data_dir + "/Data (Sheet1).csv", encoding='latin-1')
    df_equity = pd.read_csv(data_dir + "/Data (in).csv", encoding='latin-1')

    tab_company_financials = mo.vstack([
        mo.md("## Company Financials"),
        mo.md("### Income Statement"),
        mo.ui.table(df_income_stmt),
        mo.md("### Balance Sheet"),
        mo.ui.table(df_balance_sheet),
        mo.md("### Comprehensive Income"),
        mo.ui.table(df_comprehensive),
        mo.md("### Equity Breakdown"),
        mo.ui.table(df_equity),
    ])

    # Create nested tabs for Passion Projects
    tab_passion_projects = mo.ui.tabs({
        "Stock Pitch": tab_stock_pitch,
        "AFKLM credit risk": tab_afklm_credit_risk,
        "Company Financials": tab_company_financials
    })


    # --- Tab 3: Hobbies & Interests ---

    # Combining text and the travel map
    tab_personal = mo.vstack([
        mo.md("## 🌍 My Hobbies: Travel & Fashion"),
        mo.md("My two main hobbies are Travel and Fashion. The exploration of different cultures and styles inspires me both personally and professionally."),
        mo.md("*   *I take pride in the fact that I've been able to travel as much as I have, seeing most of europe has shown me a lot of different cultures and introduced me to people and cuisine that I would never had imagined earlier."),
        mo.ui.plotly(fig_travel),
        mo.md("## Fashion"),
        mo.md("I take a great interest in fashion, this interest arose when I started working within the fashion industry. I've had nothing but good experiences within that industry and it has tought me a lot about how to communicate with people. In addition to that it has allowed me to travel to places and attend events I would never have imagined I'd find myself at.")
    ])
    return tab_cv, tab_passion_projects, tab_personal


@app.cell
def _(df_airlines, df_final, mo, pd, search_input):
    # 5d-A: Search Tab — filter & build the results table
    search_query = search_input.value.strip().lower()

    _base_cols = ['Name', 'Ticker', 'Sector_Key', 'Market_Cap_B', 'Debt_Cost_Percent', 'Z_Score_lag']

    if search_query:
        _sp_cols  = [c for c in _base_cols if c in df_final.columns]
        _air_cols = [c for c in _base_cols if c in df_airlines.columns]
        _r_sp  = df_final[df_final['Name'].str.lower().str.contains(search_query, na=False)][_sp_cols]
        _r_air = df_airlines[df_airlines['Name'].str.lower().str.contains(search_query, na=False)][_air_cols]
        all_results = pd.concat([_r_sp, _r_air], ignore_index=True)
        all_results = all_results.drop_duplicates(subset=["Name"])
        all_results = all_results.rename(columns={
            'Sector_Key': 'Sector',
            'Market_Cap_B': 'Market Cap ($B)',
            'Debt_Cost_Percent': 'Avg Cost of Debt (%)',
            'Z_Score_lag': 'Z-Score (lagged)',
        }).round(2)
    else:
        all_results = pd.DataFrame()

    if not all_results.empty:
        search_table = mo.ui.table(all_results, selection="single")
        count_msg = mo.callout(
            mo.md(f"**{len(all_results)} result(s)** — click a row to view detailed financials"),
            kind='info'
        )
    else:
        search_table = None
        count_msg = mo.md("_Enter a company name above to search._" if not search_query else "_No results found._")

    search_panel = mo.vstack([
        mo.md("## 🔍 Search Companies"),
        mo.md("Search across the S&P 500 and European Airlines datasets. **Click a row** to load the company\'s live financials."),
        search_input,
        count_msg,
        search_table if search_table is not None else mo.md(""),
    ])
    return search_panel, search_table


@app.cell
def _(mo, pd, pdf_upload, px, search_table, yf):
    # 5d-B: Company detail panel — reacts whenever the user selects a row

    def _v(info, key, pct=False, decimals=2):
        """Safely extract and format a value from a yfinance info dict."""
        val = info.get(key)
        if val is None or (isinstance(val, float) and str(val) == 'nan'):
            return "N/A"
        if pct:
            return f"{val * 100:.{decimals}f}%"
        try:
            v = float(val)
        except (TypeError, ValueError):
            return str(val)
        if abs(v) >= 1e12:
            return f"${v / 1e12:.{decimals}f}T"
        if abs(v) >= 1e9:
            return f"${v / 1e9:.{decimals}f}B"
        if abs(v) >= 1e6:
            return f"${v / 1e6:.{decimals}f}M"
        return f"{v:.{decimals}f}"

    _selected = search_table.value if search_table is not None else pd.DataFrame()

    if _selected is None or (hasattr(_selected, "__len__") and len(_selected) == 0):
        company_detail = mo.md("")
    elif yf is None:
        company_detail = mo.callout(
            mo.md("**yfinance** is not available in this environment. Run the notebook locally to see live data."),
            kind="warn",
        )
    else:
        _row    = _selected.iloc[0]
        _name   = _row.get("Name",   "Unknown") if hasattr(_row, "get") else str(_row.iloc[0])
        _ticker = _row.get("Ticker", None)       if hasattr(_row, "get") else None

        if not _ticker or (isinstance(_ticker, float) and pd.isna(_ticker)):
            company_detail = mo.callout(
                mo.md(f"**{_name}** — no ticker symbol mapped for this company."),
                kind="warn",
            )
        else:
            try:
                stock = yf.Ticker(str(_ticker))
                info  = stock.info

                # ── Key statistics table ───────────────────────────────────────
                currency = info.get("currency", "")
                _stats = {
                    "Current Price":        f"{info.get('currentPrice', 'N/A')} {currency}",
                    "Market Cap":           _v(info, "marketCap"),
                    "P/E Ratio (TTM)":      _v(info, "trailingPE"),
                    "Forward P/E":          _v(info, "forwardPE"),
                    "EPS (TTM)":            _v(info, "trailingEps"),
                    "Forward EPS":          _v(info, "forwardEps"),
                    "Revenue (TTM)":        _v(info, "totalRevenue"),
                    "EBITDA":               _v(info, "ebitda"),
                    "Free Cash Flow":       _v(info, "freeCashflow"),
                    "Gross Margin":         _v(info, "grossMargins",         pct=True),
                    "Profit Margin":        _v(info, "profitMargins",        pct=True),
                    "Return on Equity":     _v(info, "returnOnEquity",       pct=True),
                    "Debt / Equity":        _v(info, "debtToEquity"),
                    "Total Debt":           _v(info, "totalDebt"),
                    "Dividend Rate":        _v(info, "dividendRate"),
                    "Dividend Yield":       _v(info, "dividendYield",        pct=True),
                    "52-Week High":         _v(info, "fiftyTwoWeekHigh"),
                    "52-Week Low":          _v(info, "fiftyTwoWeekLow"),
                    "Beta":                 _v(info, "beta"),
                    "Shares Outstanding":   _v(info, "sharesOutstanding"),
                }

                _stats_items = list(_stats.items())
                _half = len(_stats_items) // 2 + len(_stats_items) % 2
                stats_panel = mo.hstack(
                    [
                        mo.vstack([mo.md(f"**{k}**: {v}") for k, v in _stats_items[:_half]]),
                        mo.vstack([mo.md(f"**{k}**: {v}") for k, v in _stats_items[_half:]]),
                    ],
                    gap=3,
                )

                # ── Price history chart (all time) ────────────────────────────
                hist = stock.history(period="max")
                if not hist.empty:
                    hist = hist.reset_index()
                    hist = hist[hist["Close"] > 0]  # drop erroneous non-positive adjusted prices
                    _fig_price = px.line(
                        hist, x="Date", y="Close",
                        title=f"{_name} ({_ticker}) — Price History",
                        labels={"Close": f"Price ({currency})"},
                        template="presentation",
                        width=900, height=400,
                    )
                    _fig_price.update_traces(line_color="#636EFA")
                    _fig_price.update_xaxes(
                        rangeselector=dict(buttons=[
                            dict(count=1,  label="1M",  step="month", stepmode="backward"),
                            dict(count=3,  label="3M",  step="month", stepmode="backward"),
                            dict(count=6,  label="6M",  step="month", stepmode="backward"),
                            dict(count=1,  label="1Y",  step="year",  stepmode="backward"),
                            dict(count=5,  label="5Y",  step="year",  stepmode="backward"),
                            dict(step="all", label="All"),
                        ])
                    )
                    price_chart = mo.ui.plotly(_fig_price)
                else:
                    price_chart = mo.callout(mo.md("Price history not available."), kind="warn")

                # ── Earnings report PDF extractor ─────────────────────────────
                if pdf_upload.value:
                    try:
                        import io
                        try:
                            import pypdf
                        except ImportError:
                            import subprocess, sys
                            subprocess.run([sys.executable, "-m", "pip", "install", "pypdf"], check=True, capture_output=True)
                            import pypdf
                        _pdf_bytes = pdf_upload.value[0].contents
                        _reader = pypdf.PdfReader(io.BytesIO(_pdf_bytes))
                        _pages = min(len(_reader.pages), 40)
                        import re as _re
                        # Pattern: label followed by 2+ spaces then numeric values
                        _fin_pattern = _re.compile(
                            r"^(.+?)\s{2,}([\-\(]?[\d][\d,\.]*[MBK%]?\)?(?:\s+[\-\(]?[\d][\d,\.]*[MBK%]?\)?)*)\s*$"
                        )
                        # Collect all text first, then find year tokens for column headers
                        _all_text = "\n".join(
                            _reader.pages[_pi].extract_text() or "" for _pi in range(_pages)
                        )
                        # Find unique years mentioned in the document (in order of appearance)
                        _year_tokens = list(dict.fromkeys(_re.findall(r"\b(20\d{2}|19\d{2})\b", _all_text)))
                        # Detect unit label: lines like "(in EUR millions)", "€ thousands", "USD billions" etc.
                        _unit_match = _re.search(
                            r"\(?in\s+([A-Za-z€$£¥]+\s*(?:millions?|billions?|thousands?|'000s?))\)?|"
                            r"([€$£¥][A-Za-z]*\s*(?:millions?|billions?|thousands?|'000s?))|"
                            r"((?:millions?|billions?|thousands?)\s+of\s+[A-Za-z€$£¥]+)",
                            _all_text,
                            _re.IGNORECASE,
                        )
                        _unit_label = next(
                            (g for g in (_unit_match.groups() if _unit_match else []) if g),
                            "Item"
                        ).strip()
                        _rows = []
                        for _line in _all_text.splitlines():
                            _line = _line.strip()
                            if not _line:
                                continue
                            _m = _fin_pattern.match(_line)
                            if _m:
                                _label = _m.group(1).strip()
                                _vals = _m.group(2).strip()
                                _vcols = _re.split(r"\s{2,}", _vals)
                                _rows.append([_label] + _vcols)
                        if _rows:
                            _max_cols = max(len(r) for r in _rows)
                            _col_count = _max_cols - 1
                            # Use year tokens as column headers if count matches
                            if len(_year_tokens) >= _col_count:
                                _headers = [_unit_label] + _year_tokens[:_col_count]
                            else:
                                _headers = [_unit_label] + _year_tokens + [f"Val {i+1}" for i in range(_col_count - len(_year_tokens))]
                            _rows = [r + [""] * (_max_cols - len(r)) for r in _rows]
                            _fin_df = pd.DataFrame(_rows, columns=_headers)
                            pdf_block = mo.vstack([
                                mo.callout(mo.md(f"**{len(_rows)} financial line(s)** extracted from `{pdf_upload.value[0].name}` ({_pages} pages)"), kind="success"),
                                mo.ui.table(_fin_df, show_column_summaries=False, pagination=False),
                            ])
                        else:
                            pdf_block = mo.callout(
                                mo.md("No structured financial data found in this PDF. Try a report with tabular financials."),
                                kind="warn",
                            )
                    except Exception as _pdf_err:
                        pdf_block = mo.callout(mo.md(f"Could not read PDF: `{_pdf_err}`"), kind="danger")
                else:
                    pdf_block = mo.callout(
                        mo.md("Upload an earnings report PDF to extract and read it here (last 2 years recommended)."),
                        kind="info",
                    )

                # ── Dividend history chart (annual totals) ────────────────────
                divs = stock.dividends
                if len(divs) > 0:
                    _div_df = divs.reset_index()
                    _div_df.columns = ["Date", "Dividend"]
                    _div_df = _div_df[_div_df["Dividend"] > 0]  # drop negative adjustments
                    _div_df["Year"] = pd.to_datetime(_div_df["Date"]).dt.year
                    _annual = _div_df.groupby("Year", as_index=False)["Dividend"].sum()
                    _fig_div = px.bar(
                        _annual, x="Year", y="Dividend",
                        title=f"{_name} — Annual Dividends Paid",
                        labels={"Dividend": f"Total Dividend ({currency})", "Year": "Year"},
                        template="presentation",
                        text_auto=".2f",
                        width=900, height=380,
                    )
                    _fig_div.update_traces(marker_color="#EF553B", textposition="outside")
                    _fig_div.update_xaxes(type="category")
                    _fig_div.update_layout(bargap=0.3, yaxis=dict(rangemode="nonnegative"))
                    div_chart = mo.ui.plotly(_fig_div)
                else:
                    div_chart = mo.callout(mo.md("No dividend history on record."), kind="info")

                # ── EPS trend chart (from quarterly earnings) ──────────────────
                try:
                    eps_df = stock.quarterly_income_stmt
                    if eps_df is not None and not eps_df.empty and "Basic EPS" in eps_df.index:
                        _eps_series = eps_df.loc["Basic EPS"].dropna()
                        _eps_plot = pd.DataFrame({
                            "Quarter": _eps_series.index,
                            "EPS": _eps_series.values,
                        }).sort_values("Quarter")
                        _fig_eps = px.bar(
                            _eps_plot, x="Quarter", y="EPS",
                            title=f"{_name} — Quarterly EPS",
                            labels={"EPS": f"Basic EPS ({currency})"},
                            template="presentation",
                            color="EPS",
                            color_continuous_scale=["#EF553B", "#636EFA", "#00CC96"],
                            width=900, height=350,
                        )
                        eps_chart = mo.ui.plotly(_fig_eps)
                    else:
                        eps_chart = mo.callout(mo.md("EPS data not available for this ticker."), kind="info")
                except Exception:
                    eps_chart = mo.callout(mo.md("EPS data not available for this ticker."), kind="info")

                # ── Business summary ───────────────────────────────────────────
                summary = info.get("longBusinessSummary", "")
                summary_block = mo.callout(mo.md(summary), kind="info") if summary else mo.md("")

                company_detail = mo.vstack([
                    mo.md(f"---\n### {_name} &ensp; `{_ticker}` &ensp; _{info.get('sector', '')} / {info.get('industry', '')}_"),
                    summary_block,
                    mo.md("#### Key Statistics"),
                    stats_panel,
                    mo.md("#### Price History"),
                    price_chart,
                    mo.md("#### Earnings Report"),
                    pdf_upload,
                    pdf_block,
                    mo.md("#### Dividend History"),
                    div_chart,
                    mo.md("#### Quarterly EPS"),
                    eps_chart,
                ])

            except Exception as _e:
                company_detail = mo.callout(
                    mo.md(f"Could not load data for **{_ticker}**: `{_e}`"),
                    kind="danger",
                )
    return (company_detail,)


@app.cell
def _(company_detail, mo, search_panel):
    # 5d-C: Assemble the full Search tab
    tab_search = mo.vstack([search_panel, company_detail])
    return (tab_search,)


@app.cell
def _(ai_api_key, ai_question, ask_button, mo, requests):
    # 5e: AI Tab — Groq LLM integration
    ai_response = ""
    ai_error = ""

    if ask_button.value:
        if not ai_api_key.value:
            ai_error = "Please enter your Groq API key."
        elif not ai_question.value.strip():
            ai_error = "Please enter a question."
        else:
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {ai_api_key.value}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a financial analyst assistant. "
                                    "Answer questions about companies, markets, financial statements, "
                                    "and investment analysis. Be concise, accurate, and professional."
                                ),
                            },
                            {"role": "user", "content": ai_question.value},
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.7,
                    },
                    timeout=30,
                )
                data = resp.json()
                if resp.status_code == 200:
                    ai_response = data["choices"][0]["message"]["content"]
                else:
                    ai_error = data.get("error", {}).get("message", f"API error (HTTP {resp.status_code})")
            except Exception as e:
                ai_error = str(e)

    response_block = mo.callout(mo.md(ai_response), kind="success") if ai_response else mo.md("")
    error_block = mo.callout(mo.md(f"**Error:** {ai_error}"), kind="danger") if ai_error else mo.md("")


    tab_ai = mo.vstack([
        mo.md("## 🤖 AI Company Analyst"),
        mo.callout(
            mo.md(
                "Powered by **Groq**. Get your free API key at "
                "[console.groq.com/keys](https://console.groq.com/keys). "
                "Your key is only used client-side and never stored."
            ),
            kind="info",
        ),
        mo.hstack([ai_api_key, ask_button], justify="start", gap=2),
        ai_question,
        error_block,
        response_block,
    ])
    return (tab_ai,)


@app.cell
def _(mo, tab_ai, tab_cv, tab_passion_projects, tab_personal, tab_search):
    # 6: Assemble and display the multi-tab webpage

    # Create the clickable menu of tabs and assign contents defined above to each tab
    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Passion Projects": tab_passion_projects,
        "✈️ Personal Interests": tab_personal,
        "🔍 Search": tab_search,
        "🤖 AI": tab_ai
        })

    # Display the final app
    mo.md(
        f"""
         <h1 style="margin-bottom: 0.2em;"><strong>Nikolay Dermendzhiev</strong></h1>
         <div style="font-size: 1em; margin: 0; line-height: 1.1;"> TEL: +44 7933 038 950 | EMAIL: Nikolay.Dermendzhiev@bayes.city.ac.uk</div>
        ---
        {app_tabs}
        """)
    return


if __name__ == "__main__":
    app.run()
