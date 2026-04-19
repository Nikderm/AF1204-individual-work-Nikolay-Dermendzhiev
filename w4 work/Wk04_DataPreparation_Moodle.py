# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "matplotlib>=3.10.8",
#     "pandas>=2.3.3",
#     "plotly>=6.5.0",
#     "pyzmq>=27.1.0",
#     "seaborn>=0.13.2",
#     "statsmodels>=0.14.6",
#     "streamlit>=1.52.2",
#     "yahooquery>=2.4.1",
#     "yfinance>=1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    **Note:**

    - To create a new marimo notebook in Codespaces / VS Code, use the command palette (`Ctrl + Shift + P` or `Cmd + Shift + P`) and select `Create: New marimo notebook`".
        - This will open a new marimo notebook where you can start writing and executing your code.
    - To execute a code cell in a marimo notebook, a kernel must have been selected first.
        - Select a kernel by clicking on the `Select Kernel` button in the top right corner of the marimo notebook and choose `marimo sandbox` from the dropdown list.
    - If you are annoyed by inlay hints, such as type annotations (e.g., `: str`), displayed inline in the editor, this can be turned off by setting `editor.inlayHints.enabled` in Codespaces's Settings to `offUnlessPressed` (`Ctrl + Alt`)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    _**Prompt for AI:**_

    Elaborate this into step-by-step instructions for GitHub Codespaces:

    - If you are annoyed by inlay hints, such as type annotations (e.g., `: str`), displayed inline in the editor, this can be turned off by setting `editor.inlayHints.enabled` in Codespaces's Settings to `offUnlessPressed` (`Ctrl + Alt`)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    # **Data Preparation** (cont'd)

    ---
    """)
    return


@app.cell
def _():
    # Import necessary libraries

    import marimo as mo
    import pandas as pd

    # The warnings package below is used to suppress specific warnings that are annoying and not required to learn for this module
    import warnings

    # Suppress non-critical warnings
    warnings.filterwarnings('ignore', message='Mean of empty slice')
    return mo, pd


@app.cell
def _(mo):
    mo.md(r"""
    ### Let's start from where we left off
    """)
    return


@app.cell
def _(pd):

    # Read the S&P 500 panel data stored in a CSV file into a pandas dataFrame df
    df = pd.read_csv('public/sp500_raw_data_Backup.csv')

    # Replace missing Total_Debt values with 0
    df['Total_Debt'] = df['Total_Debt'].fillna(0)

    df  # Display the DataFrame
    return (df,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## **Variable Construction**

    ### Examples

    - Construct two new variables:
        - Altman Z-Score
        - Average cost of debt
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Construct new variable: **Altman Z-Score**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### The Magic of **Pandas**: Vectorization (vs. Scalar operation)

    <img src="img/Vectorized_computation_visualization_Moodle.png" alt="Vectorized computation visualization" width="600"/>
    <!-- This Markdown syntax does not work on GitHub Codespaces
    ![Vectorized computation visualization](img/Vectorized_computation_visualization_Moodle.png){width=600px}
     -->

    - **Vectorization** refers to the operations inside a function using array-like computations (e.g., `a` / `b` on entire arrays/Series) **rather than loops**.
        - The function itself can be written to accept scalars, Series, or arrays.
        - Pandas simply enables the function to work vectorized when applied to **Series**.
    - The `Zscore` function defined below is scalar in design (takes floats, does float ops),
        - but pandas vectorizes it automatically when Series data is passed into it.
        - The "vectorization" happens at the pandas level, not in the function code.
    """)
    return


@app.function
# Define the Altman Z-Score function
# (Note: This time without the try-except block!)

def Zscore(
    total_assets,
    current_assets,
    current_liab,
    retained_earnings,
    ebit,
    total_liab,
    sales,
    market_cap
    ):

    # Altman Z-Score Components (vectorized)
    WkCap2TA = (current_assets - current_liab) / total_assets
    RE2TA = retained_earnings / total_assets
    EBIT2TA = ebit / total_assets
    preferred_market_cap = 0  # Assuming no preferred stock (scalar, broadcasted)
    MVofStock2BVofTL = (market_cap + preferred_market_cap) / total_liab
    Sales2TA = sales / total_assets

    # Formula
    zscore = 1.2 * WkCap2TA + 1.4 * RE2TA + 3.3 * EBIT2TA + 0.6 * MVofStock2BVofTL + 1.0 * Sales2TA

    return zscore


@app.cell
def _(mo):
    mo.md(r"""
    #### Why **no try-except** this time?

    - `try-except` is a good practice in general:
        - It catches expected errors (e.g., `ZeroDivisionError`, `ValueError`),
            - allowing the program to continue without disruption by errors.
    - However, **pandas handles invalid operations automatically**:
        - When vectorizing operations on `Series` (like `(current_assets - current_liab) / total_assets`),
            - pandas produces `NaN` for invalid cases (e.g., 0/0, x/0) without raising exceptions.
            - This is by design — pandas assumes you'll clean or handle `NaN`s later (e.g., with `dropna()` or `fillna()`).
    - Adding `try-except` disrupts this:
        - If you wrap the vectorized code in `try-except`, it would catch all exceptions
        - but you'd have to manually insert `NaN` values, which is inefficient and error-prone.
    - Performance hit:
        - Vectorized operations are fast because they avoid Python loops.
        - Adding `try-except` forces more Python-level intervention,
            - slowing things down and making the code less "pandastic."
    - pandas is unique in its "pandas-like" error tolerance for vectorized ops:
        - Older libraries (pre-2000s) often require explicit error checking,
            - making them less "plug-and-play" for messy real-world data.
    """)
    return


@app.cell
def _(df):
    # Apply the Zscore function to the input columns in dataframe df to create a new 'Z_Score' column

    df['Z_Score'] = Zscore(
        total_assets=df['Total_Assets'],
        current_assets=df['Current_Assets'],
        current_liab=df['Current_Liab'],
        retained_earnings=df['Retained_Earnings'],
        ebit=df['EBIT'],
        total_liab=df['Total_Liab'],
        sales=df['Sales'],
        market_cap=df['Market_Cap']
    )
    return


@app.cell
def _(df):
    # Display rows with missing values of Z-Score (shown as NaN) -- due to missing values in some inputs
    df[df['Z_Score'].isna()]
    return


@app.cell
def _(df):
    # Display rows with non-missing Z-Score values
    df[df['Z_Score'].notna()]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ###  Construct new variable: **Average cost of debt**

    #### **Complication**

    - Conceptually,
        - Average cost of debt = Interest expense / Total debt
    - In practice, we often define
        - Average cost of debt = Interest expense / **avg.** Total debt
            - where **avg.** Total debt = (**year-end** Total debt + **year-beg** Total debt) **/ 2**
        - **Why?**
    - For example,
        - Average cost of debt 2025 = Interest expense 2025 / avg. Total debt 2025
            - where avg. Total debt 2025 = (Total debt 2025 + Total debt 2024) / 2
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### If there is **only one company** (say, Microsoft `MSFT`) ...
    """)
    return


@app.cell
def _(df):
    # Filter the DataFrame to only include rows for MSFT
    df_msft = df[df['Ticker'] == 'MSFT'].copy()
    df_msft
    return (df_msft,)


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    - `.copy()` creates a new, independent dataFrame, ensuring that subsequent modifications (e.g., adding columns or changing values) are safe without triggerring a warning.
        - In Python, without explicitly creating **a copy**, a filtered dataframe can just be **a view** of the orignial dataframe (like viewing it from a window).
        - Consequently, modifications on the filtered dataframe will modify the original dataframe as well because there was **never a separate copy**.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### Create a `prev_debt` column for only one company ...

    - To eventually create an **Average cost of debt** column (`AvgCost_of_Debt`),
        - the **avg.** Total debt must be in place:
            - **avg.** Total debt = (**year-end** Total debt + **year-beg** Total debt) **/ 2**
        - which requires **year-beg** Total debt to be in place first
    - Since the **year-beg** Total debt of a year is simply the **year-end** Total debt of the previous year,
        - the first step toward creating the `AvgCost_of_Debt` column is to create
            - a `prev_debt` column for the **year-end** Total debt of the previous year
    - `prev_debt` is known as the lagged value of `Total debt`, or simply **lagged** `Total debt`
    """)
    return


@app.cell
def _(df_msft):
    # Step 1: Sort the filtered DataFrame by Year to ensure chronological order
    # (Note: Doesn't hurt if the data is already sorted, but good practice to ensure correct order)

    df_msft_sorted = df_msft.sort_values('Year')
    df_msft_sorted
    return (df_msft_sorted,)


@app.cell
def _(df_msft_sorted):
    # Step 2: Use shift(1) to create a lagged version of Total_Debt (previous year's value)
    # (Note: shift(1) shifts the data down by 1 row, so each row gets the value from the previous year)
    df_msft_sorted['prev_debt'] = df_msft_sorted['Total_Debt'].shift(1)

    # Display the Ticker, Year, Total_Debt, and prev_debt columns to verify
    df_msft_sorted[['Ticker', 'Year', 'Total_Debt', 'prev_debt']]
    return


@app.cell
def _(df_msft_sorted):
    # Step 3: Compute average debt as the mean of current and previous year's Total_Debt
    df_msft_sorted['avg_debt'] = 0.5 * (df_msft_sorted['Total_Debt'] + df_msft_sorted['prev_debt'])

    # Display the Ticker, Year, Total_Debt, prev_debt, and avg_debt columns to verify
    df_msft_sorted[['Ticker', 'Year', 'Total_Debt', 'prev_debt', 'avg_debt']]
    return


@app.cell
def _(df_msft_sorted):
    # Step 4: Compute the average cost of debt as Interest Expense divided by average debt
    df_msft_sorted['AvgCost_of_Debt'] \
        = df_msft_sorted['Int_Exp'] / df_msft_sorted['avg_debt']

    # Display the Ticker, Year, Int_Exp, and AvgCost_of_Debt columns to verify
    df_msft_sorted[['Ticker', 'Year', 'Int_Exp', 'avg_debt', 'AvgCost_of_Debt']]
    return


@app.cell
def _(mo):
    mo.md(r"""
    _**Note:**_

    -  In Python, you can **split long lines of code** across multiple lines for readability using
        - backslashes (`\`) or
        - implicit line continuation within parentheses, brackets, or braces.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### When there are **multiple companies** over multiple years in `df` ...

    - Compute previous year's Total_Debt **for each Ticker** (i.e., a **`groupby`** step)
        - after sorting by Ticker and Year (with `sort_values`) for proper shifting (with `shift(1)`)

    #### **`Groupby`**:
    """)
    return


@app.cell
def _(df):
    # Chaining sort_values(), groupby(), and shift() functions in pandas

    df['prev_debt'] = df.sort_values(['Ticker', 'Year']).groupby('Ticker')['Total_Debt'].shift(1)

    # Display the Total_Debt and prev_debt columns for verification after sorting by Ticker and Year
    df.sort_values(['Ticker', 'Year'])[['Ticker', 'Year', 'Total_Debt', 'prev_debt']]
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### With `prev_debt` in place, now ready to construct the new variable `AvgCost_of_Debt`
    """)
    return


@app.cell
def _(df):
    # Compute average debt as the mean of current and previous year's Total_Debt
    df['avg_debt'] = 0.5 * (df['Total_Debt'] + df['prev_debt'])

    # Compute the average cost of debt as Interest Expense divided by average debt
    df['AvgCost_of_Debt'] = df['Int_Exp'] / df['avg_debt']

    # Display the relevant columns for verification after sorting by Ticker and Year
    df.sort_values(['Ticker', 'Year'])[['Ticker', 'Year', 'AvgCost_of_Debt', 'Int_Exp', 'avg_debt', 'Total_Debt', 'prev_debt']]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### Two reasons for **missing values** of `avg_debt` (and `AvgCost_of_Debt` as well)

    #### Reason 1: Missing values of `prev_debt` for the **first year** of each `Ticker`
    """)
    return


@app.cell
def _(df):
    # Display the relevant columns for rows with missing values of `avg_debt`, after sorting by Ticker and Year
    df[df['avg_debt'].isna()] \
        .sort_values(['Ticker', 'Year'])[
            ['Ticker', 'Year', 'AvgCost_of_Debt', 'Int_Exp', 'avg_debt', 'Total_Debt', 'prev_debt']
            ]
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Reason 2: **Zero values** of `Total_Debt` (due to **originally missing** values in the raw data)
    """)
    return


@app.cell
def _(df):
    # Display the relevant columns for rows with missing values of `Total_Debt`, after sorting by Ticker and Year
    df[df['Total_Debt'] == 0] \
        .sort_values(['Ticker', 'Year'])[
            ['Ticker', 'Year', 'AvgCost_of_Debt', 'Int_Exp', 'avg_debt', 'Total_Debt', 'prev_debt']
            ]
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Data **Analysis** and Results **Presentation**

    ### Example

    To answer **the question:**

    - _Is credit risk positively associated with borrowing costs (i.e., higher risk → higher borrowing costs)?_
        - **borrowing costs:** measured by a company's average cost of debt
        - **credit risk:** measured inversely by a company's Z-Score of the previous year (i.e., **lagged** Z-Score)
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    _**Prompt for AI:**_

    - **Why** examining the _credit risk-borrowing costs_ relationship
        - using **lagged** Z-Score, rather than **current** Z-Score?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    - Using a **lagged Z-Score** (from the previous year) instead of the current Z-Score helps establish a clearer causal relationship and avoids potential biases in the analysis:

        - **Temporal precedence:** Borrowing costs in the current year are influenced by credit risk assessed in the prior year (e.g., lenders base decisions on last year's financial health). This ensures the risk measure comes before the cost outcome.

        - **Avoid reverse causality:** If using the current Z-Score, borrowing costs (e.g., higher interest rates) could simultaneously affect the Z-Score (e.g., by impacting earnings or debt levels), leading to misleading correlations.

    - In short, it aligns with real-world timing in financial markets, where risk assessments lag behind cost adjustments.
      -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ###  Construct new variable: **Lagged Z-Score**
    """)
    return


@app.cell
def _(df):
    # Compute previous year's Z-Score for each Ticker after sorting by Ticker and Year for proper shifting

    df['Z_Score_lag'] = df.sort_values(['Ticker', 'Year']).groupby('Ticker')['Z_Score'].shift(1)

    # Display the relevant columns, including the measures for credit risk and borrowing costs, after sorting by Ticker and Year
    df.sort_values(['Ticker', 'Year'])[['Ticker', 'Year', 'Z_Score_lag', 'AvgCost_of_Debt']]
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Save the `df` with newly constructed variables to a csv file (`sp500_ZScore_AvgCostofDebt.csv`) in the `public/` folder
    """)
    return


@app.cell
def _(df):
    # Save dataframe with new columns to a csv file
    df.to_csv("public/sp500_ZScore_AvgCostofDebt.csv", index=False)

    print("\nData saved to sp500_ZScore_AvgCostofDebt.csv in the 'public' folder")
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Preparing data** for analysis and presentation
    """)
    return


@app.cell
def _(df):
    # 0. Load the data (if not already loaded)
    #df = pd.read_csv('public/sp500_ZScore_AvgCostofDebt.csv')

    # 1. Clean the data: Drop rows where the key variables are missing
    df_clean = df.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag', 'Sector_Key'])

    # 2. Filter out extreme outliers to reduce bias and improve visualization
    # (e.g., removing Z_Score_lag >= 50 or AvgCost_of_Debt >= 500%)
    df_clean = df_clean[
       (df_clean['Z_Score_lag'] < 50)    
       #& (df_clean['AvgCost_of_Debt'] < 5) # Assuming decimal format (0.15 = 15%)
    ]

    # 3. Convert Debt to % for prettier reading
    df_clean['Debt_Cost_Percent'] = df_clean['AvgCost_of_Debt'] * 100

    # 4. Compute the number of unique companies in the cleaned data
    Num_companies = len(df_clean['Name'].unique())

    print(f"Data ready! Analysis covers {len(df_clean)} observations (with {Num_companies} unique companies).")
    return (df_clean,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### **Contingency Table**
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### **Preparing data** for tabularization
    """)
    return


@app.cell
def _(df_clean):
    # Create a copy of df_clean for tabularizing contingency table results
    tb = df_clean.copy()  

    # Calculate Medians
    median_cost = tb['AvgCost_of_Debt'].median()
    median_z = tb['Z_Score_lag'].median()

    # Create labels for this year's Average Cost of Debt (row)
    tb['AvgCost_of_Debt (row)'] = tb['AvgCost_of_Debt'].apply(
        lambda x: 'Higher (Above Med.)' if x > median_cost else 'Lower (Below Med.)'
        )

    # Create labels for previous year's Z-Score (column) 
    tb['Z_Score_lag (col)'] = tb['Z_Score_lag'].apply(
        lambda x: 'Less Risky (Above Med.)' if x > median_z else 'More Risky (Below Med.)'
        )

    # Create Risk-Zone labels for previous year's Z-Score (column) 
    tb['Risk Zone (col)'] = tb['Z_Score_lag'].apply(
        lambda x: 'Safe Zone' if x > 2.99 else 'Distress Zone' if x < 1.81 else 'Grey Zone' 
        )
    return (tb,)


@app.cell
def _(mo):
    mo.md(r"""
    #### What do `.apply()` and `lambda x:` do in this command?

    ```python
    tb['AvgCost_of_Debt (row)'] = tb['AvgCost_of_Debt'].apply(
        lambda x: 'Higher (Above Med.)' if x > median_cost else 'Lower (Below Med.)'
        )
    ```

    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    In pandas, the `.apply()` method is used on a Series (like a DataFrame column) to apply a function to each element individually. It returns a new Series with the transformed values.

    - `.apply(function)`: This applies the specified function to every value in the 'AvgCost_of_Debt' column of the DataFrame tb, creating a new column 'AvgCost_of_Debt (row)' with the results.

    - `lambda x:`: This defines an anonymous (inline) function that takes a single argument `x` (representing each value from the Series). The function performs a conditional check:
        - If `x` > median_cost, it returns the string 'Higher (Above Med.)'.
        - Otherwise, it returns 'Lower (Below Med.)'.

    This effectively categorizes each value in 'AvgCost_of_Debt' as above or below the median, without needing a separate named function -- a concise way to transform data element-wise in pandas.
     -->

    ---
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Contingency Table by **Median Split** of lagged Z-Score
    """)
    return


@app.cell
def _(pd, tb):
    # Create Above/Below Median Contingency Table
    partition_table = pd.crosstab(
        index=tb['AvgCost_of_Debt (row)'], 
        columns=tb['Z_Score_lag (col)'],
        margins=True, # Adds row/column totals
        margins_name="Total"
    )

    print("=================================================================")
    print("Observation Counts in 4 Contingencies: \nAbove/Below Median of AvgCost_of_Debt (row) and Z_Score_lag (col)")
    print("=================================================================\n")
    print(partition_table)
    return


@app.cell
def _(mo):
    mo.md(r"""
    #### Contingency Table by **Risk Zone** of lagged Z-Score
    """)
    return


@app.cell
def _(pd, tb):
    # Create Risk Zone Contingency Table
    riskzone_table = pd.crosstab(
        index=tb['AvgCost_of_Debt (row)'], 
        columns=tb['Risk Zone (col)'],
        margins=True, # Adds row/column totals
        margins_name="Total"
    )

    print("=================================================================")
    print("Contingency Table: \nAbove/Below Median of AvgCost_of_Debt (row) and 3 Risk Zones (col)")
    print("=================================================================\n")
    print(riskzone_table)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ### Pooled **Regression** of Average Cost of Debt on lagged Z-Score
    """)
    return


@app.cell
def _(df_clean):
    # If needed: %pip install statsmodels
    # (Note: use %, not !, to install in the exact Python environment of the notebook)

    import statsmodels.api as sm

    # 1) Prepare data 
    # Note: drop rows of df_clean where AvgCost_of_Debt or Z_Score_lag has missing values
    reg_df = df_clean.dropna(subset=['AvgCost_of_Debt', 'Z_Score_lag']).copy()

    # 2. Filter out extreme outliers for better regression fit
    # (e.g., removing Cost of Debt >= 500%)
    reg_df = reg_df[
       (reg_df['AvgCost_of_Debt'] < 5)     # Assuming decimal format (0.15 = 15%)
       ]

    # 2) Regression: AvgCost_of_Debt on Z_Score_lag (with intercept)
    Y = reg_df['AvgCost_of_Debt']
    X = sm.add_constant(reg_df['Z_Score_lag']) # In general, multiple columns here for a multivariate regression
    # Note: add_constant() adds a column of 1's to X to estimate the intercept in the regression

    model = sm.OLS(Y, X).fit()   
    print(model.summary())
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    #### How to **interpret** the regression results?
    - In particular, the **Adj. R-squared** and `Z_Score_lag`'s **t statistic** and **p-value** (P>|t|)?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    The **regression** is like a math equation that predicts how one thing (average cost of debt) changes based on another (lagged Z-Score, which measures credit risk from the previous year). It looks like:

    **Cost of Debt = Starting Point + (Effect of Risk) × Credit Risk Measure + Random Noise**

    - **Adj. R-squared**:
        - This shows how much of the **variation** in debt costs **the model explains, adjusted for simplicity**. If it's 0.10, it means 10% of the differences in costs are explained by the credit risk measure; the rest is due to other factors not included in the model. **Higher is better**.

    - **t-statistic** for Z_Score_lag:
        - This checks if the "effect of risk" is real **or just luck**. A number big in the magnitude (like -10) means the credit risk measure strongly affects debt costs — higher lagged Z-Scores (less risky companies) lead to lower costs. If it's bigger than **about 2 in absolute value**, it's probably not random.

    - **p-value** (P>|t|) for Z_Score_lag:
        - This is the chance that the effect we see **happened by accident**. A tiny number (like 0.000) means it's very unlikely to be random — the credit risk measure really does predict debt costs. **Less than 0.05** is usually considered "real."
      -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ###  Risk Zones **Box Plot**
    """)
    return


@app.cell
def _(df_clean):
    import plotly.express as px

    # Define a function to categorize Z-Scores based on Altman's theory
    def categorize_zscore(z):
        if z < 1.81:
            return '1. Distress Zone (< 1.81)'
        elif z <= 2.99:
            return '2. Grey Zone (>= 1.81 and <= 2.99)'
        else:
            return '3. Safe Zone (> 2.99)'

    # Apply the function
    df_clean['Risk_Zone'] = df_clean['Z_Score_lag'].apply(categorize_zscore)

    # Define color mapping for risk zones
    color_map = {
        '1. Distress Zone (< 1.81)': 'red',
        '2. Grey Zone (>= 1.81 and <= 2.99)': 'grey',
        '3. Safe Zone (> 2.99)': 'green'
    }

    # --- PLOTLY BOX PLOT ---
    boxplot = px.box(
        df_clean, 
        x="Risk_Zone", 
        y="Debt_Cost_Percent",
        range_y=[-1, 15],  
        points="outliers",      # only plot extreme points
        #points="all",          # Optional: shows the raw dots alongside the box
        hover_data=["Name"], 
        color="Risk_Zone",
        color_discrete_map=color_map,
        title="Distribution of Cost of Debt by Credit Risk Zone",
        labels={'Debt_Cost_Percent': 'Avg. Cost of Debt (%)', 'Risk_Zone': 'Altman Z-Score (lagged)'}
    )

    # Update the hover label for the grey zone to use white text on grey background for better visibility
    # boxplot.update_traces(
    #     selector=dict(name='2. Grey Zone (>= 1.81 and <= 2.99)'),
    #     hoverlabel=dict(bgcolor='grey', font_color='white')
    # )

    # Hide legend as X-axis labels are sufficient
    boxplot.update_layout(showlegend=False) 

    boxplot  
    return (px,)


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ###  **Interactive Scatter Plot**
    """)
    return


@app.cell
def _(df_clean, px):
    # Create the interactive plot
    fig = px.scatter(
        df_clean, 
        x='Z_Score_lag', 
        y='Debt_Cost_Percent',
        range_x=[-5, 20],  
        range_y=[-1, 15],  
        color='Sector_Key',           # Color dots by Sector
        size='Market_Cap',            # Size dots by Market Cap  
        hover_name='Name',            # Hover to see Company Name
        hover_data=['Ticker'],
        title='Cost of Debt vs. Credit Risk (Interactive)',
        labels={'Z_Score_lag': 'Altman Z-Score (lagged)', 'Debt_Cost_Percent': 'Avg. Cost of Debt (%)'},
        template='plotly_white',    # 'presentation' # plotly_white  # 'plotly' (default) 
        width=900,
        height=600
    )

    # Add a vertical line for the "Distress" threshold (1.81)
    fig.add_vline(x=1.81, line_dash="dash", line_color="red", 
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
    fig.add_vline(x=2.99, line_dash="dash", line_color="green", 
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
    # Calculate regression line points
    import numpy as np
    # use the same dataframe used for the scatter (df_clean) and plotted y (Debt_Cost_Percent)
    #   after filtering out extreme outliers (with Debt_Cost_Percent >= 5, i.e., 500%)
    df_regline = df_clean[
       (df_clean['Debt_Cost_Percent'] < 5) # Assuming decimal format (0.15 = 15%)
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
        line_trace = px.line(x=x_line, y=y_line).data[0]
        line_trace.update(line=dict(width=0.5, color='black'))
        fig.add_trace(line_trace)
    #==============================================

    fig   
    return


@app.cell
def _(mo):
    mo.md(r"""
    \* Hidden **bonus content** here (_**double-click**_ to view; _**uncomment**_ the lines to reveal them permanently).

    <!--
    #### What does `.data[0]` do in this command?
    `px.line(x=x_line, y=y_line#, labels={'x':'Z_Score_lag','y':'Debt_Cost_Percent'}).data[0]`

    &nbsp;

    - In Plotly, `px.line(x=x_line, y=y_line)` creates a figure object containing one or more traces (data series).
        - The `.data `attribute is a list of these traces, and `[0]` selects the first trace (index 0).
        - This is used to extract the trace for customization (e.g., updating line properties) before adding it to an existing figure with `fig.add_trace(line_trace)`.
    - For **simple plots**, there's typically **only one trace**, so `[0]` gets it directly.
        - If the figure had multiple traces, they can be accessed by index (e.g., `[1]` for the second).
      -->
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## My First **Dashboard App**

    - A **dashboard** is a visual interface to provide an at-a-glance view of key metrics and data points

    - Open the marimo notebook `Wk04w_Dashboard_Moodle.py` to see the demo code for a dashboard app
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---

    ## Deploying the Dashboard App

    _**Note:**_

    - To deploy various elements covered in this marimo notebook as a **dashboard app**,
        - Click the hamburger button (≡) in the top-left corner of GitHub Codespaces and select `Terminal | New Terminal` to start a new terminal, followed by entering the command  below:

        ```bash
            marimo run Wk04w_Dashboard_Moodle.py --sandbox
        ```
    - In case the app does not open automatically,
        - Click the `PORTS` tab (next to the `TERMINAL` tab) in the bottom panel of GitHub Codespaces
        - Find the `Marimo App (2718)` entry in the tab and move horizontally to the right end of the cell under the `Forwarded Address` column to find the globe icon (🌐) and click on it to open the app
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ---

    ## My First **Multi-tabbed Webpage**

    - Open the marimo notebook `Wk04x_MyPortfolio_Moodle.py` to see the demo code for a **multi-tabbed webpage**
    - Unlike the dashboard deployed as a marimo app,
        - an html-wasm webpage created by marimo can be **accessed over the Internet** by **modern browsers**
        - (no dependency on marimo on the viewer side or requirement to view via `molab`: https://molab.marimo.io/)

    _**Note:**_

    - For the marimo-created **html-wasm** webpage to work, the data in the csv file `sp500_ZScore_AvgCostofDebt.csv` must be put on **Gist** (https://gist.github.com/[yourGitHubUsername]) and loaded using a **raw gist URL** approach
    - To **create a new gist** to store your data secretly,
        - go to your own Gist page (i.e., replacing `[yourGitHubUsername]` in the Gist "placeholder" URL above by your GitHub username)
        - click the **`+` button** in the top-right corner of the page to initiate the process of creating a new gist
        - After clicking the `+` button, a page will open with a cell `Filename including extension...` for entering the name of the gist to be created
            - put down `sp500_ZScore_AvgCostofDebt.csv` in that cell (or another name you prefer)
        - Then go back to the `Explorer panel` of your GitHub Codespace,
            - find the csv file under the `public/` folder and double-click to open it
            - click anywhere in the file and use the key sequence `Ctrl + A` to select all the data in the file, followed by `Ctrl + C` to copy the data (use `Cmd` in Mac, instead of `Ctrl`; can also try the right-click menu to see if there are choices for `Copy` and `Paste`)
        - Next, go back to the `Gist` page and click on the large box in the center of the page
            - use `Ctrl + V` to paste the previously copied data into the large box
            - click the green `Create secret gist` button in the lower-right corner to finish creating the secret gist for the data
            - on the next page that loads, find the `Raw` button in the upper-right corner of the data box in the center
            - click the `Raw` button to open the gist in the raw-data form
            - **copy the URL** of that page for later use in loading the data with a **raw gist URL** approach
            - go to the notebook `Wk04x_MyPortfolio_Moodle.py` and look at the second code cells to see **how to load data remotely** from the raw gist URL
    - <span style="color: red;">_**Warning!**_</span>
        - Do **NOT** use this approach for data with privacy concerns
        - The gist's URL is secret and hard to guess. However, the current approach puts the URL directly in the source code of the html-wasm file to be exported from a marimo notebook, exposing it to whoever looking at the file's source code
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ### 🏆 **Publishing the multi-tabbed webpage to the world (Free):**

    Since we are using tools in the GitHub ecosystem, you can turn the notebook `Wk04x_MyPortfolio_Moodle.py` with the code for a multi-tabbed webpage into a real website in 3 steps:

    1.  **Export:** Click the hamburger button (≡) in the top-left corner of GitHub Codespaces and select `Terminal | New Terminal` to start a new terminal, followed by entering the terminal command below to export the notebook to the subfolder `docs` (with an `index.html` file created there):
        ```bash
        marimo export html-wasm Wk04x_MyPortfolio_Moodle.py -o docs --sandbox --force
        ```
        - _Note_: data files must be placed in the `public/` folder (if the data are not loaded remotely)

    2.  **Push to GitHub:**
        *   Click the **Source Control** icon (on the left sidebar).
        *   Click the `+` sign at the end of the row `Changes` to **stage all changed files** (the `+` sign will appear when hovering over there)
        *   Type a message (e.g., "My first website") and click **Commit**.
        *   Click **Sync Changes** (or click the triple dots sign `...` at the end of the row **`CHANGES`** and select `Push`).

    3.  **Activate Website:**
        *   Go to the repository page of your own forked repo on **GitHub.com**
            - For example, `https://github.com/BayesUG-AI/repoAF1204-[yourGitHubUsername]`
        *   Click **Settings** (in the top bar), then **Pages** (in the left sidebar).
        *   Under "Branch" of the `Build and deployment` section, select `main` | `docs` and click **Save**.
            - _Note:_ If `main` | `docs` have already been selected, then first change `main` to `None` and click **Save** to reset  before doing the above again
        *   Wait several minutes, refresh the page, and a link will appear near the top of that page (e.g., `https://bayesug-ai.github.io/repoAF1204-[yourGitHubUsername]/`).
            - _Note:_ If you are not creating the link for the first time, then click **Actions** (in the top bar of your GitHub repo page) and patiently wait for the latest brown dot(s) to turn green before accessing the link of the generated webpage

    **You can now send that link to anyone, and your dynamic multi-tabbed webpage will work on their phone or laptop!**

    ---
    """)
    return


if __name__ == "__main__":
    app.run()
