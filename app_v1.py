import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import re
import numpy as np

st.set_page_config(
    page_title="Bank Statement Analzer",
    page_icon="📊",  # Bar Chart emoji
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.markdown(
    """
    <style>
    .sidebar-link {
        font-size: 20px; /* Adjust the font size as needed */
        color: white; /* Adjust the color as needed */
        text-decoration: none;
        transition: color 0.3s, text-decoration 0.3s; /* Smooth transition */
    }
    .sidebar-link:hover {
        color: #FF5733; /* Change color on hover */
        text-decoration: underline;
    }
    </style>
    <a class="sidebar-link" href="https://thebluesurf3r.github.io" target="_blank">My Resume</a>
    """,
    unsafe_allow_html=True
)

# Title and Introduction
st.title("Bank Statement Analysis and Visualization")
st.markdown("""
**Bank Statement Analysis and Visualization**

Welcome to the Bank Statement Analysis and Visualization App! This intuitive tool is designed to help you effortlessly analyze and visualize your bank transactions. Whether you're tracking your spending habits, budgeting for the future, or just curious about where your money goes, our app provides the insights you need.

**Key Features:**
- **Date Range Selection**: Filter your transactions by custom date ranges to focus on specific periods.
- **Amount Filtering**: Easily identify transactions above or below certain amounts to pinpoint large or small expenditures.
- **Balance Tracking**: Monitor your account balance over time to ensure you're always aware of your financial status.
- **Categorization**: Automatically categorize your transactions into various types like groceries, utilities, travel, and more for a clear view of your spending patterns.
- **Entity Extraction**: Extract and analyze the names or entities from your transaction descriptions to understand who you're paying and receiving money from.
- **Interactive Visualizations**: Enjoy dynamic and interactive charts and graphs that make understanding your financial data a breeze.
""")

# Sample data loading function with caching
@st.cache_data
def load_data():
    # Replace with your actual data loading logic
    data = pd.read_csv('merged_data.csv')
    return data

# Load data
data = load_data()

def format_column_names(column_names):
    return column_names.str.replace(' ', '_').str.replace('-', '_').str.replace('/', '_').str.replace('.', '').str.lower()

data.columns = format_column_names(data.columns)

# Clean and format columns
data['transaction_date'] = data['transaction_date'].str.replace('-', '/', regex=False)
data['value_date'] = data['value_date'].str.replace('-', '/', regex=False)

# Convert dates
data['transaction_date'] = pd.to_datetime(data['transaction_date'], format='%d/%m/%Y')
data['value_date'] = pd.to_datetime(data['value_date'], format='%d/%m/%Y')

# Split and map transaction details
data[['transaction_type', 'transaction_number']] = data['chq___ref_no'].str.split('-', expand=True)
mapping = {'CR': 1, 'DR': -1}
data['credit_debit_value'] = data['dr___cr'].map(mapping)

# Adjust net balance
data['net_balance'] = data['balance'] * data['credit_debit_value']

# Define categorization functions
def categorize_payment_method(description):
    patterns = {
        'Immediate Payment Service [IMPS]': r'IMPS',
        'National Electronic Funds Transfer [NEFT]': r'NEFT',
        'Unified Payments Interface [UPI]': r'UPI',
        'Automated Teller Machine [ATM]': r'ATM|DEBIT|CARD|VISA',
        'Mobile Banking [MB]': r'MB|MOBILE BANKING',
        'Point of Sale Card Transaction [PCD]': r'PCD',
    }
    for method, pattern in patterns.items():
        if re.search(pattern, description):
            return method
    return 'Other'

# Define categorization functions
def categorize_payment_method_acronyms(description):
    patterns = {
        'IMPS': r'IMPS',
        'NEFT': r'NEFT',
        'UPI': r'UPI',
        'ATM': r'ATM|DEBIT|CARD|VISA',
        'MB': r'MB|MOBILE BANKING',
        'PCD': r'PCD',
    }
    for method, pattern in patterns.items():
        if re.search(pattern, description):
            return method
    return 'Other'

def categorize_buckets(description):
    patterns = {
        'Self': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697)\b',
        'Family': r'\b(muzicmapass|kanishq|kanishq sharma|kan |kast |kastoorisha|kastoori|kasturi|deepak vi|deepak kumar vi)\b',
        'Friends': r'\b(vivek|vishal|tanti|hites|bhaga)\b',
        'Utilities': r'\b(bharti|airtel|dakshin|dbhvn|rento|mojo)\b',
        'Misc': r'\b(thapa|ricky)\b',
        'Fuel': r'\b(gas|petro|pump|station|petrol|fuel|auto|care|filling)\b',
        'Groceries': r'\b(grofers|fast n fresh|vandanachawla|7015758745)\b',
        'ATM Withdrawal': r'\b(atm|card)\b',
        'Salary Credit': r'\b(rcvd|cognizant|fis)\b',
        'Ecommerce': r'\b(amazon|flipk|kart)\b',
        'Liquor': r'\b(liquor|wine|country)\b',
        'Loan': r'\b(loan|SPLN|Ins Debit)\b',
        'House Rent': r'\b(bhupesh|darsh|jing|ICICX7180|landlord)\b',
        'Trading': r'\b(nextbillion|groww)\b',
        'Travel': r'\b(makemy|travel|bnb|oyo)\b',
        'Movies': r'\b(bookmy|pvr|cinepolis|cinema|movi|ny cinemas)\b',
        'Food': r'\b(9891020216|twenty four seven|chick po|paan|dhaba|restaurant|food|food court|tea|zomato|the ducktales|vendiman)\b',
    }
    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category
    return 'Other'

def categorize_brands(description):
    patterns = {
        'Zomato': r'\bzomato\b',
        'Amazon': r'\bamazon\b',
        'Rento Mojo': r'\b(rento|mojo)\b',
        'DBHVN': r'\b(dakshin|dbhvn)\b',
        'Bookmyshow': r'\bbookmyshow\b',
        'Makemytrip': r'\bmakemytrip\b',
        'Flipkart': r'\b(flipka|flipkart)\b',
        'Swiggy': r'\bswiggy\b',
        'Blinkit': r'\b(grofers|blinkit)\b',
        'Airtel': r'\b(airtel|bharti)\b',
        'Paytm': r'\bpaytm\b',
        'GPay': r'\b(gpay|google)\b',
    }
    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category
    return 'Other'

def categorize_names(description):
    patterns = {
        'Vyom': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697|9958121100)\b',
        'Kanishq Sharma': r'\b(muzicmapass|kanishq|kanishq sharma|kan |9873683245|8433204684)\b',
        'Kasturi Sharma': r'\b(kast |kastoorisha|kastoori|kasturi|8789816580)\b',
        'Ajay Sharma': r'\b(ajay sharma|9833640145)\b',
        'Deepak Vishwakarma': r'\b(deepak vi|deepak kumar vi)\b',
        'Anandita Jangra': r'\b(anandita|anandita jangra|8979655500)\b',
        'Dhruv Parashar': r'\b(dhruv parashar)\b',
        'Karanveer': r'\b(karancr8999|karanveer |karanveer|971585216969|9646862136)\b',
        'Karan Talwar': r'\b(karan talwar)\b',
        'Pragun Magan': r'\b(pragun magan|8447783423)\b',
        'Yawar Rashid': r'\b(yawar rashid|9956394027)\b',
        'Hitesh Bhagat': r'\b(hit |hitesh|hitesh bhagat|hiteshbhaga|ICICX5879|8447299009)\b',
        'Akhriebu Pucho': r'\b(akhriebu pucho|akhriebu|9582384807)\b',
        'Bhupesh Jingar': r'\b(bhupesh jingar|darsh jing|ICICX7180)\b',
        'Vivek Tanti': r'\b(vivek|vivek tanti|vivektanti|vivektanti5|9172603649)\b',
        'Vishal Tanti': r'\b(vishal|vishal tanti|vishaltanti|vishal.tant|UTIBX8285|9774973923)\b',
        'Gaurav Yadav': r'\b(1993ygaurav|Gaurav Yadav)\b',
        'Jegendra': r'\b(jegendermn7)\b',
        'Parth Singh': r'\b(parth singh|9910270502)\b',
        'Cognizant': r'\b(COGNIZANT SAL|Cogniz)\b',
        'Paytm Wallet': r'\b(@payt|add-money)\b',
        'Zomato': r'\b(zomato|zomato-orde|zomato limited|razorpayzomato|zomato ltd|zomato online|zomato swiggy)\b',
        'Zomato Money': r'\b(zomatomoney|@zoma)\b',
        'Gpay': r'\b(google)\b',
        'Payu Payment': r'\b(payu)\b',
    }
    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category
    return 'Other'

# Apply categorization functions
data['payment_method'] = data['description'].apply(categorize_payment_method)
data['payment_method_acronym'] = data['description'].apply(categorize_payment_method_acronyms)
data['transaction_category'] = data['description'].apply(categorize_buckets)
data['transaction_brands'] = data['description'].apply(categorize_brands)
data['transaction_names'] = data['description'].apply(categorize_names)

# Define the function to format numeric values
def format_numeric_values(numeric_values):
    # Remove commas
    numeric_values = numeric_values.str.replace(',', '')
    return numeric_values

# Apply the function to the specified columns
data[['amount', 'balance', 'net_balance']] = data[['amount', 'balance', 'net_balance']].apply(format_numeric_values)

# Convert the columns to numeric data types
data[['amount', 'balance', 'net_balance']] = data[['amount', 'balance', 'net_balance']].apply(pd.to_numeric)

st.sidebar.title("Report Configuration")

Keyword = st.sidebar.text_input("Enter a keyword to search:")

# Date Range Slider

max_start = pd.to_datetime(data['transaction_date'].min())
max_end =pd.to_datetime(data['transaction_date'].max())

# Calculate the number of days from the start date
data['number_days'] = (data['transaction_date'] - max_start).dt.days + 1

# Convert max_start and max_end to days since max_start
days_index_start = 0
days_index_end = (max_end - max_start).days

# Create a slider for the date range
slider_range_date = st.sidebar.slider(
    'Date Range',
    min_value=days_index_start,
    max_value=days_index_end,
    value=(days_index_start, days_index_end)
)

# Convert the slider range back to dates
start_date = max_start + pd.Timedelta(days=slider_range_date[0])
end_date = max_start + pd.Timedelta(days=slider_range_date[1])

st.write(f'Selected Start Date: {start_date}')
st.write(f'Selected End Date: {end_date}')

transaction_date_data = data[(data['transaction_date'] >= start_date) & (data['transaction_date'] <= end_date)]

# Amount Slider

min_amount = transaction_date_data['amount'].min()
max_amount = transaction_date_data['amount'].max()

# Create a slider for the date range
slider_range_amount = st.sidebar.slider(
    'Amount',
    min_value=min_amount,
    max_value=max_amount,
    value=(min_amount, max_amount)
)

amount_filtered_data = transaction_date_data[(transaction_date_data['amount'] >= min_amount) & (transaction_date_data['amount'] <= max_amount)]

# Balance Slider

min_balance = amount_filtered_data['balance'].min()
max_balance = amount_filtered_data['balance'].max()

# Create a slider for the date range
slider_range_amount = st.sidebar.slider(
    'Balance',
    min_value=min_balance,
    max_value=max_balance,
    value=(min_balance, max_balance)
)

balance_filtered_data = amount_filtered_data[(amount_filtered_data['amount'] >= min_amount) & (amount_filtered_data['amount'] <= max_amount)]

# Drop redundant columns
columns_to_drop = ['chq___ref_no', 'transaction_number', 'dr___cr', 'dr___cr1', 'payment_type', 'transaction_type', 'transaction_number']

processed_data = data.drop(columns=columns_to_drop)

filtered_data = balance_filtered_data[(balance_filtered_data['balance'] >= min_balance) & (balance_filtered_data['balance'] <= max_amount)]


fig = px.box(filtered_data, x='payment_method_acronym', y='transaction_category')
# Customize the layout
fig.update_layout(
    width=966,
    height=644,              
    template='plotly_dark',  # Dark theme
    #plot_bgcolor='rgba(0,0,0,1)',  # Plot background color
    #paper_bgcolor='rgba(0,0,0,1)',  # Paper background color
    xaxis_title='Payment Method',
    yaxis_title='Transaction Category',
        scene=dict(
        yaxis=dict(
            range=[days_index_start, days_index_end]
        )
    )
)
# Refine the grid
fig.update_xaxes(
    showgrid=True,  # Show gridlines on the x-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='black',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the x-axis
)

fig.update_yaxes(
    showgrid=True,  # Show gridlines on the y-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='blue',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the y-axis
)

st.plotly_chart(fig)


fig = px.box(filtered_data, x='payment_method_acronym', y='transaction_category', )
# Customize the layout
fig.update_layout(
    width=966,
    height=644,              
    template='plotly_dark',  # Dark theme
    #plot_bgcolor='rgba(0,0,0,1)',  # Plot background color
    #paper_bgcolor='rgba(0,0,0,1)',  # Paper background color
    xaxis_title='Payment Method',
    yaxis_title='Transaction Category',
        scene=dict(
        #xaxis=dict(
        #    range=[min_amount, max_amount]
        #),
        yaxis=dict(
            range=[days_index_start, days_index_end]
        )
    )
)

# Refine the grid
fig.update_xaxes(
    showgrid=True,  # Show gridlines on the x-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='black',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the x-axis
)

fig.update_yaxes(
    showgrid=True,  # Show gridlines on the y-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='blue',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the y-axis
)

st.plotly_chart(fig)

# Generate data points for the ripple effect
n_points = 1000
x_ripple = np.random.uniform(filtered_data['balance'].min(), filtered_data['balance'].max(), n_points)
y_ripple = np.random.uniform(filtered_data['amount'].min(), filtered_data['amount'].max(), n_points)
z_ripple = np.random.uniform(filtered_data['number_days'].min(), filtered_data['number_days'].max(), n_points)
size_ripple = np.random.uniform(5, 100, n_points)

# Generate distinguishable colors for the ripple effect
color_ripple = np.random.choice(px.colors.qualitative.Plotly, n_points)

# Create the base scatter plot with adjusted date range
fig = px.scatter_3d(
    filtered_data,
    x='balance',
    y='amount',
    z=filtered_data.index,
    color='balance',
    size='amount',
    width=966,
    height=644,
    title='Distribution of transaction values against balance over time',
    color_continuous_scale=px.colors.sequential.Jet,
    opacity=1,  # Adjust the base scatter plot transparency
    range_color=(500, 50000),
    labels={'transaction_date': 'Transaction Date'},  # Label for the y-axis
)

# Customize the layout
fig.update_layout(
    width=966,
    height=644,              
    template='plotly_dark',  # Dark theme
    #plot_bgcolor='rgba(0,0,0,1)',  # Plot background color
    #paper_bgcolor='rgba(0,0,0,1)',  # Paper background color
    xaxis_title='Amount',
    yaxis_title='Balance',
        scene=dict(
        xaxis=dict(
            range=[min_amount, max_amount]
        ),
        yaxis=dict(
            range=[days_index_start, days_index_end]
        )
    )
)

# Refine the grid
fig.update_xaxes(
    showgrid=True,  # Show gridlines on the x-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='black',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the x-axis
)

fig.update_yaxes(
    showgrid=True,  # Show gridlines on the y-axis
    gridwidth=1,  # Width of the gridlines
    gridcolor='blue',  # Color of the gridlines
    tickfont=dict(size=10)  # Font size of the ticks on the y-axis
)

fig.update_traces(
    line=dict(width=6),
    marker=dict(size=3, symbol='circle'),
)
st.plotly_chart(fig)

# Distribution visualizations
st.header("Distribution Visualizations")
bucket_counts = filtered_data['transaction_category'].value_counts()
brand_counts = filtered_data['transaction_brands'].value_counts()
name_counts = filtered_data['transaction_names'].value_counts()

# Transaction buckets count
plt.figure(figsize=(10, 5))
sns.barplot(x=bucket_counts.index, y=bucket_counts.values, palette='viridis')
plt.title('Transaction Category Count')
plt.xlabel('Bucket')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt)

# Transaction brands count
plt.figure(figsize=(10, 5))
sns.barplot(x=brand_counts.index, y=brand_counts.values, palette='viridis')
plt.title('Transaction Brands Count')
plt.xlabel('Brand')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt)

# Transaction names count
plt.figure(figsize=(10, 5))
sns.barplot(x=name_counts.index, y=name_counts.values, palette='viridis')
plt.title('Transaction Names Count')
plt.xlabel('Name')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt)
