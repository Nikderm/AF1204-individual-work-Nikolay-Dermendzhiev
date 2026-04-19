# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyzmq>=27.1.0",
#     "streamlit>=1.52.2",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    # Import necessary libraries

    import marimo as mo
    import pandas as pd
    import plotly.express as px

    return mo, pd, px


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## My First Dashboard App

    - A dashboard is a visual interface to provide an at-a-glance view of key metrics and data points
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### 1. **Load** Data
    """)
    return


@app.cell
def _(pd):
    # --- 1: Load Data ---

    df_DB = pd.read_csv('public/sp500_ZScore_AvgCostofDebt.csv')
    df_DB = df_DB.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])

    # Filter outliers to reduce bias and improve visualizations
    df_DB = df_DB[(df_DB['AvgCost_of_Debt'] < 5)]   # 5 means 500%
    #df_DB = df_DB[(df_DB['AvgCost_of_Debt'] > 0) & (df_DB['Z_Score_lag'] < 20)]
    df_DB['Debt_Cost_Percent'] = df_DB['AvgCost_of_Debt'] * 100
    return (df_DB,)


@app.cell
def _(mo):
    mo.md(r"""
    #### 2. Create **UI Controls**
    """)
    return


@app.cell
def _(df_DB, mo):
    # --- 2: Create UI Controls ---

    # Create a multiselect widget using mo.ui
    sector_options = list(df_DB['Sector_Key'].unique())
    sector_selector = mo.ui.multiselect(
        options=sector_options,
        value=sector_options, # Default to selecting all
        label="**Select Sectors to Analyze:**"
    )
    return (sector_selector,)


@app.cell
def _(mo):
    mo.md(r"""
    #### 3. Set Selector to **Filter Data Reactively** (`.isin(sector_selector.value)`)
    """)
    return


@app.cell
def _(df_DB, sector_selector):
    # --- 3: Filter Data (Reactive) ---

    # This cell listens to 'sector_selector'. 
    # When the user changes the selection, this cell re-runs automatically.
    df_filtered = df_DB[df_DB['Sector_Key'].isin(sector_selector.value)]

    # Calculate metrics based on the filtered data
    company_count = len(df_filtered)
    avg_cost = df_filtered['Debt_Cost_Percent'].mean()
    return avg_cost, company_count, df_filtered


@app.cell
def _(mo):
    mo.md(r"""
    #### 4. Create the **Interactive Plot** on the Dashboard
    """)
    return


@app.cell
def _(df_filtered, px):
    # --- 4: Create the Plot --- 
    # This also updates automatically when df_filtered changes 

    #==============================================
    import textwrap

    title = "Are higher Z-Scores last year associated with lower average costs of debt this year?"
    wrapped_title = "<br>".join(textwrap.wrap(title, width=50))
    #==============================================

    # Note: template='presentation' below gives a clean look with larger fonts, ideal for dashboards.
    DB_fig = px.scatter(
        df_filtered,
        x='Z_Score_lag', 
        y='Debt_Cost_Percent',
        range_x=[-5, 20],  
        range_y=[-1, 15],  
        color='Sector_Key',           # Color dots by Sector
        size='Market_Cap',            # Size dots by Market Cap 
        hover_name='Name',            # Hover to see Company Name
        hover_data=['Ticker'],
        title=wrapped_title,
        #title='Are higher Z-Scores last year associated with lower average costs of debt this year?',
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='presentation',    # 'presentation' # plotly_white  # 'plotly' (default) 
        width=900,
        height=600
    )

    #==============================================
    # Adjust y position to add top spacing and also left-align title
    DB_fig.update_layout(title=dict(y=0.95, x=0, xanchor='left'))  
    #==============================================

    # Add a vertical line for the "Distress" threshold (1.81)
    DB_fig.add_vline(x=1.81, line_dash="dash", line_color="red", 
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
    DB_fig.add_vline(x=2.99, line_dash="dash", line_color="green", 
        annotation=dict(
            text="Safe Threshold (Z-Score = 2.99)",
            font=dict(color="green"),
            x=3.10, xref="x",
            y=1.02, yref="paper", 
            showarrow=False,
            yanchor="top"
            ) 
        )


    #==============================================
    # Use df_filtered to dynamically calculate regression line points
    import numpy as np
    # use the same dataframe used for the scatter (df_filtered) and plotted y (Debt_Cost_Percent)
    #   after filtering out extreme outliers (with Debt_Cost_Percent >= 5, i.e., 500%)
    df_regline = df_filtered[
       (df_filtered['Debt_Cost_Percent'] < 5) # Assuming decimal format (0.15 = 15%)
       ]

    # Only calculate regression if there are data points
    if not df_regline.empty:
        x = df_regline['Z_Score_lag'].astype(float)
        y = df_regline['Debt_Cost_Percent'].astype(float)

        # get slope & intercept of the regression line
        slope, intercept = np.polyfit(x, y, 1)

        # create x-range for a smooth line
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = intercept + slope * x_line

        # add regression line to existing fig
        line_trace = px.line(x=x_line, y=y_line#, labels={'x':'Z_Score_lag','y':'Debt_Cost_Percent'}
        ).data[0]
        line_trace.update(line=dict(width=0.5, color='black'))

        DB_fig.add_trace(line_trace)
    #==============================================

    print("  ")  # Add this to prevent the plot from appearing immediately before the Dashboard, rather than inside it
    return (DB_fig,)


@app.cell
def _(mo):
    mo.md(r"""
    #### 5. Define the **Dashboard Layout** (using `mo.md()`)
    """)
    return


@app.cell
def _(DB_fig, avg_cost, company_count, mo, sector_selector):
    # --- 5: The Dashboard Layout ---
    # In marimo, you use mo.md() (Markdown) to organize your UI elements, metrics, and plots into a webpage.

    # Note the use of f-string for dynamic content (see f""" below)
    dashboard = mo.md(
        f"""                
    
        # 📊 SP500 Credit Risk Analyzer (Built with marimo)

        This dashboard analyzes the relationship between **Altman Z-Score** and **Cost of Debt**.

        ---

        {sector_selector}   <!-- multiselect widget for sectors as previously defined -->

        ---

        ## Key Metrics

        | Companies Analyzed | Avg. Cost of Debt |
        | :---: | :---: |
        | **{company_count}** | **{avg_cost:.2f}%** |

        ---

        ## Visualization

        {mo.as_html(DB_fig)}    <!-- Embed the Plotly figure as HTML in the dashboard -->
        """
    )
    return (dashboard,)


@app.cell
def _(mo):
    mo.md(r"""
    #### 6: **Display** the Dashboard

    - Select the `consumer-cyclical` sector and then the `basic-materials` sector to see an interesting contrast in the cost of debt
    """)
    return


@app.cell
def _(dashboard):
    # Display the dashboard
    dashboard
    return


if __name__ == "__main__":
    app.run()
