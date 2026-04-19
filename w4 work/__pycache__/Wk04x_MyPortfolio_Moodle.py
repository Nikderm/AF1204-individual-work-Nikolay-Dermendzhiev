# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.22.4",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## 🎓 Personal Portfolio Webpage
    Combine everything learned so far (e.g., data loading, preparation, and visualization) into a multi-tabbed webpage featuring interactive chart and dashboard
    """)
    return


@app.cell
def _():

    import marimo as mo
    import pandas as pd

    # Require micropip to install packages in the WASM environment
    import micropip

    return micropip, mo, pd


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
    return (df_final,)


@app.cell
def _(df_final, mo):
    # 2: Define the UI Controls (The "Inputs")

    # create the widgets here. In marimo, assigning them to a variable makes them available globally.

    # 1. A Dropdown to select Sectors
    all_sectors = sorted(df_final['Sector_Key'].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3], # Default to first 3
        label="Filter by Sector",
        )

    # 2. A Slider for Market Cap (Size of company)
    # Convert Market Cap to Billions for easier reading
    df_final['Market_Cap_B'] = df_final['Market_Cap'] / 1e9
    max_cap = int(df_final['Market_Cap_B'].max())

    cap_slider = mo.ui.slider(
        start=0, 
        stop=200,   # int(0.05*max_cap), 
        step=10, 
        value=0, # initial value
        label="Min Market Cap ($ Billions)"
        )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    # 3: The Filter Logic (Reactive Data)

    # This cell re-runs automatically when the user changes the slider or dropdown

    # Filter the dataframe based on the UI inputs
    filtered_portfolio = df_final[
        (df_final['Sector_Key'].isin(sector_dropdown.value)) &
        (df_final['Market_Cap_B'] >= cap_slider.value)
        ]

    # Calculate a quick summary metric
    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
async def _(micropip):
    # Await installation of plotly in the WASM environment
    await micropip.install('plotly');

    # What does await do here? 
    # It pauses execution of the code until the package is installed, 
    # considering that installing a package is an asynchronous operation 
    # (which means taking some time to complete)

    import plotly.express as px

    return (px,)


@app.cell
def _(count, filtered_portfolio, mo, pd, px):
    # 4: The Visualizations

    # Create the plots based on the filtered data.

    #=========================================
    # Plot 1: The Financial Analysis (Scatter)
    #=========================================
    fig_portfolio = px.scatter(
        filtered_portfolio,
        x='Z_Score_lag', 
        y='Debt_Cost_Percent',
        color='Sector_Key',
        size='Market_Cap_B',
        hover_name='Name',
        title=f"Cost of Debt vs. Z-Score ({count} observations)",
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        # template='presentation' gives a clean look with larger fonts
        template='presentation',    # 'presentation' # plotly_white  # 'plotly' (default) 
        width=900,
        height=600
        )

    # Add a vertical line for the "Distress" threshold (1.81)
    fig_portfolio.add_vline(x=1.81, line_dash="dash", line_color="red", 
        annotation=dict(
            text="Distress Threshold (Z-Score = 1.81)",
            font=dict(color="red"),
            x=1.5, xref="x",
            # x is interpreted in the x-axis data coordinates (or category label)
            y=1.07, yref="paper",
            # y is interpreted as a fraction of the plotting area (0 = bottom, 1 = top).
            showarrow=False,
            yanchor="top"
            ) 
        )

    # Add a vertical line for the "Safe" threshold (2.99)
    fig_portfolio.add_vline(x=2.99, line_dash="dash", line_color="green", 
        annotation=dict(
            text="Safe Threshold (Z-Score = 2.99)",
            font=dict(color="green"),
            x=3.10, xref="x",
            y=1.02, yref="paper",
            showarrow=False,
            yanchor="top"
            ) 
        )


    # #==============================================
    # # Calculate regression line points
    # import numpy as np
    # # use the same dataframe used for the scatter (filtered_portfolio) and plotted y (Debt_Cost_Percent)
    # #   after filtering out extreme outliers (with Debt_Cost_Percent >= 5, i.e., 500%)
    # df_regline = filtered_portfolio[
    #    (filtered_portfolio['Debt_Cost_Percent'] < 5) # Assuming decimal format (0.15 = 15%)
    #    ]
    # 
    # # Only calculate regression if there are data points
    # if not df_regline.empty:
    #     x = df_regline['Z_Score_lag'].astype(float)
    #     y = df_regline['Debt_Cost_Percent'].astype(float)

    #     # get slope & intercept of the regression line
    #     slope, intercept = np.polyfit(x, y, 1)

    #     # create x-range for a smooth line
    #     x_line = np.linspace(x.min(), x.max(), 100)
    #     y_line = intercept + slope * x_line

    #     # add regression line to existing fig
    #     line_trace = px.line(x=x_line, y=y_line#, labels={'x':'Z_Score_lag','y':'Debt_Cost_Percent'}
    #     ).data[0]
    #     line_trace.update(line=dict(width=0.5, color='black'))

    #     fig_portfolio.add_trace(line_trace)
    # #==============================================

    # Wrap the plot in a marimo UI element
    chart_element = mo.ui.plotly(fig_portfolio)


    #=========================================
    # Plot 2: Personal Travel Map (Hardcoded demo data for the 'Hobbies' tab)
    #=========================================
    # This simulates travel history data  
    travel_data = pd.DataFrame({
        'City': ['London', 'New York', 'Tokyo', 'Sydney', 'Paris'],
        'Lat': [51.5, 40.7, 35.6, -33.8, 48.8],
        'Lon': [-0.1, -74.0, 139.6, 151.2, 2.3],
        'Visit_Year_str': ['2022', '2023', '2024', '2021', '2023']
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
def _(mo):
    # 5: Tab Content - About Me
    tab_cv = mo.md(
        """
        ### Aspiring Financial Analyst | Data Science Enthusiast

        **Summary:**
        - Great interest in the financial and investment world. 
        - Retail trader managing a personal portfolio.

        **Education:**
        *   **BSc Accounting & Finance**, Bayes Business School (2025 - Present)
        *   *Relevant Modules:* Introduction to Data Science and AI Tools, Financial Accounting.
        *   **Stanmore college**, BTEC business Level 3 Diploma (2023-2025).
        *   *Diploma in Business, with Distinction* (equivalent to A* grades in A-levels).
        *   **Kensington park school**, GCSEs (2022-2023).
        *   *GCSEs in Maths (Grade 7), English (Grade 5)*
        *   **Royal school of Wolverhampton**, GCSEs (2020-2022).

        **Skills:**
        *   Financial Analysis
        *   Data Visualization
        *   Networking

        **Career**
        *   Moderately successful career in **Modelling**
        *   Worked with brands including: **Alexander Mcqueen, Uniqlo, Amiri, YSL**
        """
    )
    return (tab_cv,)


@app.cell
def _(mo):
    # Tab 2: Passion Projects with Sub-tabs
    tab_stock_pitch = mo.md(
        """
        ## Stock pitch
        *(Current content is temporarily disabled.)*

        Add your stock pitch details here.
        """
    )

    tab_insert_later = mo.md(
        """
        ## inster later
        *(Content coming soon.)*

        Replace this placeholder when ready.
        """
    )

    tab_data_content = mo.ui.tabs({
        "Stock pitch": tab_stock_pitch,
        "inster later": tab_insert_later
    })

    return (tab_data_content,)


@app.cell
def _(fig_travel, mo):
    # Tab 3: Hobbies & Interests
    tab_personal = mo.vstack([
        mo.md("## 🌍 My Hobbies: Travel & Photography"),
        mo.md("When I'm not analyzing company financials, I love exploring the world."),
        mo.ui.plotly(fig_travel)
    ])

    return (tab_personal,)


@app.cell
def _(mo, tab_cv, tab_data_content, tab_personal):
    # 6: Assemble the multi-tab webpage
    app_tabs = mo.ui.tabs({
        "📄 About Me": tab_cv,
        "📊 Passion Projects": tab_data_content,
        "✈️ Personal Interests": tab_personal
    })

    return


@app.cell
def _():
    # Display the final app
    return


if __name__ == "__main__":
    app.run()
