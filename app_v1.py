# Importing Streamlit for interactive web applications
import streamlit as st

# Importing Pandas for data manipulation and analysis
import pandas as pd

# Importing Matplotlib for basic plotting
import matplotlib.pyplot as plt

# Importing Plotly for interactive visualizations
import plotly.express as px
import plotly.graph_objs as go

# Importing Seaborn for statistical data visualization
import seaborn as sns

# Importing Regular Expressions for pattern matching
import re

# Importing NumPy for numerical operations
import numpy as np

# Importing time
import time

# Setting page configuration
st.set_page_config(
    page_title="Bank Statement Analyzer",  # Title of the webpage
    page_icon="📊",  # Emoji or icon displayed in the browser tab
    layout="centered",  # Layout of the main content (options: 'centered', 'wide')
    initial_sidebar_state="expanded"  # State of the sidebar when the app starts (options: 'auto', 'expanded', 'collapsed')
)

# Title and Introduction
st.title("Bank Statement Analysis and Visualization")


# Initialize session state for documentation toggle if not already set
if 'show_documentation' not in st.session_state:
    st.session_state.show_documentation = False

# Add the "Documentation" link to the sidebar
with st.sidebar:
    st.caption('Please go through the documentation here')
    if st.button('Documentation'):
        st.session_state.show_documentation = not st.session_state.show_documentation
    st.caption('---')
if st.session_state.show_documentation:
    # Display documentation
    with open('documentation.md', 'r') as f:
        st.caption(f.read())

@st.cache_data
def load_df():
    file_path = 'merged_data.csv'
    df = pd.read_csv(file_path)
    return df

# Load data using the caching function
data = load_df()

@st.cache_data
def process_data(df):
    # Formatting column names
    df.columns = df.columns.str.replace(' ', '_')\
                           .str.replace('-', '_')\
                           .str.replace('/', '_')\
                           .str.replace('.', '')\
                           .str.lower()

    # Check and replace '/' in dates if present
    if df['transaction_date'].str.contains('/').any():
        df['transaction_date'] = df['transaction_date'].str.replace('/', '-')
    if df['value_date'].str.contains('/').any():
        df['value_date'] = df['value_date'].str.replace('/', '-')
    
    # Formatting dates
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], format='%d-%m-%Y')
    df['value_date'] = pd.to_datetime(df['value_date'], format='%d-%m-%Y')
    
    # Splitting and mapping transaction details as boolean values
    df[['transaction_type', 'transaction_number']] = df['chq___ref_no'].str.split('-', expand=True)
    mapping = {'CR': 1, 'DR': -1}
    df['credit_debit_value'] = df['dr___cr'].map(mapping)
    
    # Adjusting net balance
    df['net_balance'] = df['balance'] * df['credit_debit_value']
    
    return df

# Apply the processing function to the data
data = process_data(data)

import re

# Define the extract_name function
def extract_name(description):
    # Regular expression to match names enclosed by slashes
    slash_pattern = re.compile(r'/([A-Za-z\s]+?)/')
    # Regular expression to match names within a longer string
    embedded_pattern = re.compile(r'([A-Za-z]+(?:\s[A-Za-z]+)+)')
    
    # First, try to find names enclosed by slashes
    matches = slash_pattern.findall(description)
    
    if matches:
        extracted_name = matches[0].title()
    else:
        # If no matches with slashes, try to find embedded names
        matches = embedded_pattern.findall(description)
        extracted_name = matches[0].title() if matches else 'Other'
    
    # Categorize the extracted name
    categorized_name = categorize_names(extracted_name)
    if categorized_name != 'Other':
        return categorized_name
    else:
        return extracted_name

# Define the categorize_names function
def categorize_names(description):
    patterns = {
        'Vyom': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697|9958121100|fd booked|rd booked|vyomdeepansh-1@)\b',
        'Kanishq Sharma': r'\b(muzicmapass|kanishq|kanishq sharma|kan |9873683245|8433204684)\b',
        'Kasturi Sharma': r'\b(kast |kastoorisha|kastoori|kasturi|8789816580)\b',
        'Ajay Sharma': r'\b(ajay sharma|9833640145)\b',
        'Deepak Vishwakarma': r'\b(deepak vi|deepak kumar vi)\b',
        'Anandita Jangra': r'\b(ananditajangra1|anandita|anandita jangra|8979655500)\b',
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
        'Paytm Wallet': r'\b(@payt|add-money)\b'
    }
    for category, pattern in patterns.items():
        if re.search(pattern, description, re.IGNORECASE):
            return category
    return 'Other'

# Define the categorize_brands function
def categorize_brands(description):
    name = extract_name(description)
    if name == 'Other':
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
            'Airtel': r'\b(airtel|bharti|BhartiAirte)\b',
            'Paytm': r'\bpaytm\b',
            'GPay': r'\b(gpay|google)\b',
            'Aditya Birla': r'\b(aditya birla fa)\b'
        }
        for category, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                return category
        return 'Other'
    else:
        return name

def categorize_buckets(description):
    name = extract_name(description)
    patterns = {
        'Self': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697|fd booked|rd booked)\b',
        'Family': r'\b(muzicmapass|kanishq|kanishq sharma|kan |kast |kastoorisha|kastoori|kasturi|deepak vi|deepak kumar vi)\b',
        'Friends': r'\b(ananditajangra1|anandita|vivek|vivektanti5|vishal|tanti|hites|bhaga)\b',
        'Utilities': r'\b(bharti|airtel|paytmairtelrecharge|dakshin|dbhvn|rento|mojo|airtelin|paytm_airtelrecharge)\b',
        'Misc': r'\b(thapa|ricky)\b',
        'Fuel': r'\b(gas|petro|pump|station|petrol|fuel|auto|care|filling)\b',
        'Groceries': r'\b(grofers|fast n fresh|sandeep|vandanachawla|7015758745)\b',
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
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, description, re.IGNORECASE):
            return category
    
    # If no match is found, categorize using categorize_brands
    return categorize_brands(description)


# Defining payment method categorization
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

# Defining payment method categorization acronyms for visuals
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


# Applying categorization functions
# Define the combined function
def combined_function_name(description):
    name = extract_name(description)
    if name == 'Other':
        name = categorize_names(description)
    return name

# Apply the combined function to the 'description' column
data['transaction_names'] = data['description'].apply(combined_function_name)
data['payment_method'] = data['description'].apply(categorize_payment_method)
data['payment_method_acronym'] = data['description'].apply(categorize_payment_method_acronyms)
data['transaction_category'] = data['description'].apply(categorize_buckets)

def format_numeric_columns(df, columns):
    # Removing the ',' values for numeric compatibility
    def format_numeric_values(numeric_values):
        numeric_values = numeric_values.str.replace(',', '')
        return numeric_values

    # Applying the function to the relevant numeric columns
    df[columns] = df[columns].apply(format_numeric_values)
    
    # Converting those columns to appropriate data types
    df[columns] = df[columns].apply(pd.to_numeric)
    
    return df

# Columns to format
numeric_columns = ['amount', 'balance', 'net_balance']

# Apply the numeric formatting function to the data
data = format_numeric_columns(data, numeric_columns)

st.sidebar.markdown('<h1 class="sidebar-title">Report Configuration</h1>', unsafe_allow_html=True)

with st.sidebar:
    # Add a placeholder for the status message
    status_message = st.empty()
    status_message.caption('Computing transactions...')
    
    # Add a placeholder for the iteration text
    latest_iteration = st.empty()
    bar = st.progress(0)

    for i in range(100):
        # Update the progress bar with each iteration
        latest_iteration.text(f'{i+1} %')
        bar.progress(i + 1)
        time.sleep(0.01)

    # Update the status message to 'Done' after the loop
    status_message.caption('Computation complete')

# Date Range Slider
max_start = data['transaction_date'].min()
max_end = data['transaction_date'].max()

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
start_date = (max_start + pd.Timedelta(days=slider_range_date[0])).normalize()
end_date = (max_start + pd.Timedelta(days=slider_range_date[1])).normalize()

# Convert start_date and end_date to strings with only the date part
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Create three columns
col1, col2, col3 = st.columns([1, 1, 1])

# Check if the selected dates are at their maximum values
max_start_date = data['transaction_date'].min()
max_end_date = data['transaction_date'].max()

start_date_color = "gray" if start_date == max_start_date else "white"
end_date_color = "gray" if end_date == max_end_date else "white"

# Convert the dates to string
start_date_str = start_date.strftime('%d-%m-%Y')
end_date_str = end_date.strftime('%d-%m-%Y')

# Create columns
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown(f'<p style="color:{start_date_color}; text-align: left;" title="The start date of the selected period">Start Date: {start_date_str}</p>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<p style="color:{end_date_color}; text-align: right;" title="The end date of the selected period">End Date: {end_date_str}</p>', unsafe_allow_html=True)


# Filter transaction data based on the selected date range
transaction_date_data = data[(data['transaction_date'] >= start_date) & (data['transaction_date'] <= end_date)]

# Amount Slider
min_amount = 0
max_amount = 50000

# Create a single seekbar handle for the amount range
slider_value_amount = st.sidebar.slider(
    'Amount',
    min_value=min_amount,
    max_value=max_amount,
    value=(min_amount + max_amount) // 2  # Initial value in the middle
)

# Filter the transaction data based on the selected amount value
filtered_1data = transaction_date_data[transaction_date_data['amount'] <= slider_value_amount]

# Balance Slider
min_balance = 0
max_balance = 75000

# Create a single seekbar handle for the amount range
slider_value_amount = st.sidebar.slider(
    'Balance',
    min_value=min_balance,
    max_value=max_balance,
    value=(min_balance + max_balance) // 2  # Initial value in the middle
)

# Filter the transaction data based on the selected amount value
amount_filtered_data = filtered_1data[filtered_1data['amount'] <= slider_value_amount]

def search_transactions(keyword, amount_filtered_data):
    # Convert keyword to lowercase for case-insensitive search
    keyword = keyword.lower()
    
    # Filter the DataFrame based on the keyword
    result = amount_filtered_data[
        amount_filtered_data['description'].str.lower().str.contains(keyword) |
        amount_filtered_data['transaction_names'].str.lower().str.contains(keyword) |
        amount_filtered_data['transaction_category'].str.lower().str.contains(keyword)

    ]
    return result

# Sidebar input for the search query
keyword = st.sidebar.text_input("Please enter your query:")

# Display the search results
if keyword:
    results = search_transactions(keyword, amount_filtered_data)
    num_results = len(results)  # Get the number of search results
    if not results.empty:
        result_text = f"Search Results: {keyword} ({num_results} results)"
        result_color = "white"
    else:
        result_text = "No matching transactions found."
        result_color = "white"
else:
    # Count the "Other" values in the entire 'transaction_names' column
    unattributed_names = amount_filtered_data['transaction_names'].value_counts().get('Other', 0)
    
    result_text = f"Please enter a query to search for transactions | There are {unattributed_names} unattributed names"
    result_color = "gray"

st.markdown(f'<p style="color:{result_color};">{result_text}</p>', unsafe_allow_html=True)

name_filtered_data = search_transactions(keyword, amount_filtered_data)
balance_filtered_data = name_filtered_data[(name_filtered_data['amount'] >= min_amount) & (name_filtered_data['amount'] <= max_amount)]

# Dropping redundant columns
columns_to_preview = ['number_days', 'value_date', 'credit_debit_value','net_balance','payment_method_acronym', 'tag', 'name', 'sl_no', 'chq___ref_no', 'transaction_number', 'dr___cr', 'dr___cr1', 'payment_type', 'transaction_type', 'transaction_number']
columns_to_analyze = ['sl_no', 'transaction_number', 'dr___cr', 'dr___cr1', 'transaction_type']

visible_data = balance_filtered_data.drop(columns=columns_to_preview)
processed_data = balance_filtered_data.drop(columns=columns_to_analyze)

@st.cache_data
def get_preview_data(visible_data, processed_data, balance_filtered_data, min_balance, max_amount):
    return visible_data[(processed_data['balance'] >= min_balance) & (balance_filtered_data['balance'] <= max_amount)]

preview_data = get_preview_data(visible_data, processed_data, balance_filtered_data, min_balance, max_amount)
filtered_data = processed_data[(processed_data['balance'] >= min_balance) & (balance_filtered_data['balance'] <= max_amount)]

# Function to create gradient based on transaction_date rank
def color_date_gradient(val):
    color = f'background-color: rgba(5, 50, 10, {val})'
    return color

def apply_gradient_to_transaction_dates(dataframe):
    def color_date_gradient(value):
        return f'background: rgba(255, {int(255 * value)}, 0, 0.5)'

    styled_data = dataframe.style.background_gradient(cmap='turbo_r')
    styled_data = styled_data.apply(lambda x: x.rank(pct=True).apply(color_date_gradient), subset=['transaction_date'])
    
    return styled_data

styled_data = apply_gradient_to_transaction_dates(visible_data)
st.dataframe(styled_data)

# Function to configure the visuals for distribution plots
update_display_main = lambda fig: st.plotly_chart(
    fig.update_layout(
        width=1000,
        height=600,
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=0,
        showlegend=False,
        coloraxis=dict(colorscale='Jet') #Options:
        # Blackbody,Bluered,Blues,Cividis,Earth,Electric,
        # Greens,Greys,Hot,Jet,Picnic,Portland,Rainbow,RdBu,Reds,Viridis,YlGnBu,YlOrRd.
    )
    .update_xaxes(
        showgrid=False,
        gridwidth=1,
        gridcolor='blue',
        tickfont=dict(size=10)
    )
    .update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='blue',
        tickfont=dict(size=10)
    )
)
line_graph = px.line(filtered_data, x='transaction_date', y='amount')
update_display_main(line_graph)

# Generating ripples for visualization
def generate_ripple_effect(filtered_data, n_points=300):

    transaction_count = filtered_data['transaction_names'].nunique()

    x_ripple = np.random.uniform(filtered_data['balance'].min(), filtered_data['balance'].max(), n_points)
    y_ripple = np.random.uniform(filtered_data['amount'].min(), filtered_data['amount'].max(), n_points)
    z_ripple = np.random.uniform(0, transaction_count, n_points)
    size_ripple = np.random.uniform(75, 4, n_points)

    # Generate distinguishable colors for the ripple effect
    color_ripple = np.random.choice(px.colors.qualitative.Plotly, n_points)

    return x_ripple, y_ripple, z_ripple, size_ripple, color_ripple

# Generate ripple effect data
x_ripple, y_ripple, z_ripple, size_ripple, color_ripple = generate_ripple_effect(filtered_data)

# Create the base scatter plot
scatter_plot = px.scatter_3d(
    filtered_data,
    x='balance',
    y='amount',
    z=filtered_data.index,
    color='balance',
    size='amount',
    title='Distribution of transaction values against balance over time',
    opacity=1,
    labels={'amount': 'Amount spent', 'balance': 'Remaining balance', 'index': 'Days'}
)

# Add a 3D surface plot (Commented out in the original code)
scatter_plot.add_trace(go.Surface(
     z=z_ripple.reshape((75, 4)),  # Reshape for surface plot
     x=x_ripple.reshape((75, 4)),
     y=y_ripple.reshape((75, 4)),
     opacity=0.01,
     showscale=False
 ))
update_display_main(scatter_plot)

# Distribution visualizations
st.header("Distribution Visualizations")
bucket_counts = filtered_data['transaction_category'].value_counts()
name_counts = filtered_data['transaction_names'].value_counts()

df = bucket_counts.reset_index()
df.columns = ['Bucket', 'Count']

# Function to configure the visuals for distribution plots
update_display_dist = lambda fig: st.plotly_chart(
    fig.update_layout(
        width=966,
        height=644, 
        xaxis_tickangle=90,
        showlegend=False,
        coloraxis=dict(colorscale='Jet')
    )
    .update_xaxes(
        showgrid=False,
        gridwidth=1,
        gridcolor='blue',
        tickfont=dict(size=10)
    )
    .update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='blue',
        tickfont=dict(size=10)
    )
)

# Distribution Visualization 1
distribution_count = px.bar(df, x='Bucket', y='Count', title='Transaction Category Count', 
             labels={'Bucket': 'Bucket', 'Count': 'Count'}, 
             color='Count')

update_display_dist(distribution_count)

# Distribution Visualization 3

df = name_counts.reset_index()
df.columns = ['Name', 'Count']

distribution_names = px.bar(df, x='Name', y='Count', title='Transaction Names Count', 
             labels={'Name': 'Name', 'Count': 'Count'}, 
             color='Count')

update_display_dist(distribution_names)

 # Create and display the parallel categories plot with labels
labels = {
            "transaction_date": "Transaction Date",
            "transaction_names": "Transaction Names",
            "transaction_category": "Transaction Category",
            "payement_method_acronym": "Payment Method"
        }

# Parallel categories        
fig = px.parallel_categories(
            filtered_data,
            dimensions=['transaction_names', 'transaction_category', 'payment_method_acronym'],
            labels=labels,
            title='Parallel categories plot between transaction date, transaction category and payment method'
        )
update_display_main(fig)

# Function to convert DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Main part of the app
st.write("Here is the preview of the original data")

# Add a download button at the bottom of the page
csv = convert_df_to_csv(filtered_data)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)

st.sidebar.markdown(
    """
    <style>
    .sidebar-link {
        font-size: 12px; /* Adjust the font size as needed */
        font-family: 'Arial', sans-serif; /* Adjust the font style as needed */
        color: #00BFFF; /* Adjust the color as needed */
        text-decoration: none;
        transition: color 0.3s, text-decoration 0.3s; /* Smooth transition */
    }
    .sidebar-link:hover {
        color: #FF5733; /* Change color on hover */
        text-decoration: underline;
    }
    </style>
    <a class="sidebar-link" href="https://thebluesurf3r.github.io" target="_blank">You can view my resume here</a>
    """,
    unsafe_allow_html=True
)
