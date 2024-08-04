# Importing necessary libraries
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import seaborn as sns
import re
import numpy as np
import time

# Page configuration
st.set_page_config(
    page_title="Bank Statement Analyzer",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Title and Introduction with custom CSS
st.markdown("""
    <style>
    .title-container {
        padding: 10px;
        background-color: black;
        border-radius: 10px;
        text-align: center;
    }
    .title-text {
        font-size: 2em;
        font-weight: bold;
        color: white;
    }
    </style>
    <div class="title-container"><div class="title-text">Financial Transaction Explorer</div></div>
""", unsafe_allow_html=True)

# Initialize session state for documentation toggle if not already set
if 'show_documentation' not in st.session_state:
    st.session_state.show_documentation = True

# Sidebar for documentation toggle
with st.sidebar:
    if st.button('Documentation'):
        st.session_state.show_documentation = not st.session_state.show_documentation
    st.markdown('<hr>', unsafe_allow_html=True)

# Display documentation if toggled on
if st.session_state.show_documentation:
    with open('documentation.md', 'r') as f:
        doc_content = f.read()
    st.markdown(f'''
        <div id="documentation" style="padding: 30px; background-color: black; border-radius: 10px;">
            {doc_content}
    ''', unsafe_allow_html=True)

# Caching data loading function
@st.cache_data
def load_df():
    file_path = 'merged_data.csv'
    return pd.read_csv(file_path)

data = load_df()

# Cleaning data
def process_data(df):
    # Formatting column names
    df.columns = (df.columns.str.replace(' ', '_')
                              .str.replace('-', '_')
                              .str.replace('/', '_')
                              .str.replace('.', '')
                              .str.lower())

    # Check and replace '/' in dates if present
    date_columns = ['transaction_date', 'value_date']
    for col in date_columns:
        if df[col].str.contains('/').any():
            df[col] = df[col].str.replace('/', '-')

    # Formatting dates
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], format='%d-%m-%Y')
            
        except ValueError:
            st.warning(f"Error parsing dates in column {col}. Ensure dates are in 'dd-mm-yyyy' format.")
            return None

    # Splitting and mapping transaction details as boolean values
    try:
        df[['transaction_type', 'transaction_number']] = df['chq___ref_no'].str.split('-', expand=True)
    except KeyError:
        st.error("Column 'chq___ref_no' not found in the dataframe.")
        return None

    # Mapping 'dr___cr' to numerical values
    mapping = {'CR': 1, 'DR': -1}
    df['credit_debit_value'] = df['dr___cr'].map(mapping).fillna(0)

    # Adjusting net balance
    try:
        df['net_balance'] = df['balance'] * df['credit_debit_value']
    except KeyError:
        st.error("Column 'balance' not found in the dataframe.")
        return None

    return df

# Apply the processing function to the data
data = process_data(data)

if data is None:
    st.error("Data processing failed. Please check the input data and try again.")

st.divider()
# Streamlit app
def main():

    # Create a multi-select box for toggle
    transaction_types = st.multiselect(
        "Select transaction types:",
        ['Credit', 'Debit', 'Both']
    )
    
    # Determine which values to set based on selection
    if 'Both' in transaction_types:
        toggle_values = [1, -1]
    elif 'Credit' in transaction_types:
        toggle_values = [1]
    elif 'Debit' in transaction_types:
        toggle_values = [-1]
    else:
        toggle_values = []

    # Update DataFrame based on selected values
    if 'Both' in transaction_types:
        data['credit_debit_value'] = data['credit_debit_value'].apply(lambda x: x if x in toggle_values else None)
    else:
        data['credit_debit_value'] = data['credit_debit_value'].apply(lambda x: x if x in toggle_values else None)

if __name__ == "__main__":
    main()


def extract_name(description):
    # Define regex patterns
    slash_pattern = re.compile(r'/([A-Za-z\s]+?)/')
    embedded_pattern = re.compile(r'([A-Za-z]+(?:\s[A-Za-z]+)+)')
    specific_pattern = re.compile(r'SentIMPS\d+(\w+)\b')
    youtube_pattern = re.compile(r'\b(?:sold by\s+)?youtube\b', re.IGNORECASE)
    debit_card_pattern = re.compile(
        r'\b(?:DEBIT CARD ANNUAL FEE \w{4}\d{4} FOR \d{4}|'
        r'Chrg: Debit Card Annual Fee \d{4} For \d{4}|'
        r'Rem Chrgs:Debit Card Annual Fee \d{4} For \d{4}|'
        r'UPI/\w+/[\d\/]+/Debit Money Usi|'
        r'Ins Debit A\\c SPLN \d+ dt \d{2}/\d{2}/\d{2,4}|'
        r'Ins Debit A\\c PDL \d+ dt \d{2}/\d{2}/\d{2,4})', re.IGNORECASE
    )
    name_pattern = re.compile(r'\b[A-Z][a-z]+(?: [A-Z][a-z]+)*\b')
    cognizant_pattern = re.compile(r'\bCOGNIZANT\b|\bCOGNIZ.*?\b', re.IGNORECASE)
    amazon_pattern = re.compile(
        r'\b(?:UPI/amazon(?:@apl|\.refu)?/\d+/.*|'
        r'PCD/1186/(?:WWW\s)?AMAZON\s(?:IN|Seller\sServices|Pay)|'
        r'PG\sAMAZON\sPAY\sINDIA\sPRI|'
        r'UPI/Amazon\s(?:India|Prime\sRe(?:fund)?|Seller\sServices|Pay|Package)|'
        r'UPI/AMAZON\sSELLER\sS(?:\s|/|UPI|MB\sUPI)?|'
        r'UPI/AMAZON(?:\sSELLER\sS)?(?:/|UPI|MB\sUPI)?|'
        r'PCD/1186/Amazon\s(?:Seller\sServices|Pay)|'
        r'UPI/Amazon\s(?:India|Prime\sRe(?:fund)?)|'
        r'UPI/AMAZON\s(?:SELLER\sS|SELLER\sS\s(?:UPI|MB\sUPI))\b'
        r')',
        re.IGNORECASE
    )

    # Try to find names with the Amazon pattern first
    amazon_match = amazon_pattern.search(description)
    if amazon_match:
        extracted_name = 'Amazon'
    else:
        # Try to find names with the Cognizant pattern
        cognizant_match = cognizant_pattern.search(description)
        if cognizant_match:
            extracted_name = cognizant_match.group(0).title()
        else:
            # Check for YouTube patterns
            youtube_match = youtube_pattern.search(description)
            if youtube_match:
                extracted_name = youtube_match.group(0).title()
            else:
                # Check for debit card patterns
                debit_card_match = debit_card_pattern.search(description)
                if debit_card_match:
                    extracted_name = debit_card_match.group(0)
                else:
                    # If no matches with debit card pattern, try to find names enclosed by slashes
                    slash_matches = slash_pattern.findall(description)
                    if slash_matches:
                        extracted_name = slash_matches[0].title()
                    else:
                        # If no matches with slashes, try to find names with specific patterns
                        specific_matches = specific_pattern.findall(description)
                        if specific_matches:
                            extracted_name = specific_matches[0].title()
                        else:
                            # If no matches with specific patterns, try to find names with the name pattern
                            name_matches = name_pattern.findall(description)
                            if name_matches:
                                extracted_name = name_matches[0].title()
                            else:
                                # If no matches with name pattern, try to find embedded names
                                embedded_matches = embedded_pattern.findall(description)
                                extracted_name = embedded_matches[0].title() if embedded_matches else 'Other'

    # Categorize the extracted name
    categorized_name = categorize_name(extracted_name)
    return categorized_name if categorized_name != 'Other' else extracted_name

# Define the categorize_names function
def categorize_name(extracted_name):
    patterns = {
        'Vyom': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697|9958121100|fd booked|rd booked|vyomdeepansh-1)\b',
        'Kanishq Sharma': r'\b(muzicmapass|kanishq(?: sharma)?|kan|9873683245|8433204684)\b',
        'Kasturi Sharma': r'(?i)\b(kast(?:oori(?:sharma)?|oorisha)?|8789816580|KASTURI SHAR)\b',
        'Ajay Sharma': r'\b(ajay sharma|9833640145)\b',
        'Deepak Vishwakarma': r'\b(deepak (?:vishwakarma|kumar vi))\b',
        'Anandita Jangra': r'\b(anandita(?: jangra)?|8979655500|ananditajangra1)\b',
        'Dhruv Parashar': r'\b(dhruv parashar)\b',
        'Karanveer': r'\b(karancr8999|karanveer|971585216969|9646862136)\b',
        'Karan Talwar': r'\b(karan talwar)\b',
        'Pragun Magan': r'\b(pragun magan|8447783423)\b',
        'Yawar Rashid': r'\b(yawar rashid|9956394027)\b',
        'Hitesh Bhagat': r'\b(hitesh(?: bhagat|bhaga)?|hit|ICICX5879|8447299009)\b',
        'Akhriebu Pucho': r'\b(akhriebu(?: pucho)?|9582384807)\b',
        'Bhupesh Jingar': r'\b(bhupesh jingar|darsh jing|ICICX7180)\b',
        'Vivek Tanti': r'\b(vivek(?: tanti|tanti5)?|9172603649)\b',
        'Vishal Tanti': r'\b(vishal(?: tanti|tanti|\.tant)?|UTIBX8285|9774973923)\b',
        'Gaurav Yadav': r'\b(1993ygaurav|Gaurav Yadav)\b',
        'Jegendra': r'\b(jegendermn7)\b',
        'Parth Singh': r'\b(parth singh|9910270502)\b',
        
        'Dominos': r'\b(dominos)\b',
        'Bagril Biotech': r'(bagril)',
        'Balaji Store': r'balaji|bala ji',
        'Cognizant': r'\bCOGNIZANT\b|\bCOGNIZ.*?\b',
        'Zomato': r'\bZomato\b(?: Media Pr| Ltd)?',
        'Amazon': r'\amazon|amazon@apl|you are pay|amazon india|amazon pay|amazon seller\b',
        'Rento Mojo': r'\b(edunetwork|rento|rentomojo|rentomojorazorp|rentomojorentpa)\b',
        'DBHVN': r'\b(dakshin|dbhvn)\b',
        'Bookmyshow': r'\b(bookmyshow)\b',
        'Makemytrip': r'\b(makemytrip)\b',
        'Flipkart': r'\b(flipka|flipkart)\b',
        'Swiggy': r'\b(swiggy)\b',
        'Blinkit': r'\b(grofers|blinkit)\b',
        'Licious': r'\b(licious)\b',
        'Vendiman': r'vendiman(?: pvt ltd)?',

        'Airtel': r'\b(airtel|bharti|BhartiAirte)\b',
        'Aditya Birla': r'\b(aditya birla fa|ABFL)\b',
        'Uber': r'\b(uberrides|uber)\b',
        'Ola': r'\bola\s+(money|financial)\b',
        'Netflix': r'\bnetflix(?:\scom)?\b',
        'YouTube': r'\b(?:sold by\s+youtube|youtube(?:\s?prem)?)\b',
        'Google': r'\b(google india di)\b',
        'Paytm Wallet': r'\b(payt|add-money)\b',
        'Personal Loan': r'\b(SPLN|PDL)\b',
        'Kotak': r'\bchr?gs?|annual fee|cw fee\b',
    }
    
    for category, pattern in patterns.items():
        if re.search(pattern, extracted_name, re.IGNORECASE):
            return category
    return 'Other'

# Define the categorize_brands function
def categorize_brands(extracted_name):
    name = extract_name(extracted_name)
    if name == 'Other':
        patterns = {
            
        }
        for category, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                return category
        return 'Other'
    else:
        return name

def categorize_buckets(name):
    name = extract_name(name)
    patterns = {
        'Self': r'\b(vyomdeepans|vyom|vyom deepansh|8447156697|fd booked|rd booked)\b',
        'Family': r'\b(muzicmapass|kanishq|kanishq sharma|kan |kast |kastoorisha|kastoori|kasturi|deepak vi|deepak kumar vi)\b',
        'Friends': r'\b(ananditajangra1|anandita|vivek|vivektanti5|vishal|tanti|hites|bhaga)\b',
        'Utilities': r'\b(bharti|airtel|paytmairtelrecharge|dakshin|dbhvn|rento|mojo|airtelin|airtelrecharge)\b',
        'Misc': r'\b(thapa|ricky)\b',
        'Fuel': r'\b(?:Hpcl Auto Care Center|Auto Care Centre Hpcl|Fuel Junction|Gupta Service Station|Enroute Sahays Filling|City Fuels|Jawala Service Station|Spr Petro|Rama Filling Station|M S Suraj Auto|Meer Singh Fuel Point|Navyug Fuels|Shree Shyam Petro|Petro Mall|Dhruvika Petro|H P Hira Fuels|Infinity Fuels|Pauls Petro Mar|Raghunandan Filling St|Rama Filling St|Meer Singh Fuel|Hello Fuels)\b',
        'Groceries': r'\b(?:grofers|fast\s*n\s*fresh|sandeep|bala ji|balaji\s*(?:super|distribu)?|vandanachawla|7015758745)\b',
        'ATM Withdrawal': r'\b(atm|card)\b',
        'Wikimedia': r'\b(wikimedia)\b',
        'Salary Credit': r'\b(rcvd|cognizant|fis)\b',
        'Ecommerce': r'\b(amazon|flipk|kart)\b',
        'Liquor': r'\b(?:LIQUOR|WINE|WINES|WINE & BEER|LIQUORLAND|VINTAGE WINES|LAKE FOREST WINES|DISCOVERY LIQUOR|ABOHAR LIQUOR|SHIVAM WINES|G TOWN WINES|TIME FOR WINE)\b',
        
        'Loan': r'\b(loan|SPLN|Ins Debit)\b',
        'House Rent': r'\b(bhupesh|darsh|jing|ICICX7180|landlord)\b',
        'Trading': r'\b(nextbillion|groww)\b',
        'Travel': r'\b(makemy|travel|bnb|oyo)\b',
        'Movies': r'\b(bookmy|pvr|cinepolis|cinema|movi|ny cinemas)\b',
        'Food': r'\b(9891020216|twenty four seven|foods|chick po|paan|dhaba|restaurant|food|food court|tea|zomato|the ducktales|vendiman)\b',
    }
    for category, pattern in patterns.items():
        if re.search(pattern, name, re.IGNORECASE) or re.search(pattern, name, re.IGNORECASE):
            return category
    
    # Check each pattern against the name
    for category, pattern in patterns.items():
        if re.search(pattern, name, re.IGNORECASE):
            return category
    
    # If no match is found, return 'Other'
    return 'Other'


# Defining payment method categorization
def categorize_payment_method(transaction_type):
    patterns = {
        'Immediate Payment Service [IMPS]': r'IMPS',
        'National Electronic Funds Transfer [NEFT]': r'NEFT|KKBKH|MB|MOBILE BANKING|TBMS|PDL|SPLN',
        'Unified Payments Interface [UPI]': r'UPI',
        'Automated Teller Machine [ATM]': r'ATL|DEBIT|CARD|VISA',
        'Point of Sale Card Transaction [PCD]': r'PCD',
        }
    for method, pattern in patterns.items():
        if re.search(pattern, transaction_type):
            return method
    return 'Other'

# Defining payment method categorization acronyms for visuals
def categorize_payment_method_acronyms(description):
    patterns = {
        'IMPS': r'IMPS',
        'NEFT': r'NEFT|MB|TBMS',
        'UPI': r'UPI',
        'ATM': r'ATM|DEBIT|CARD|VISA',
        'PCD': r'PCD',
    }
    for method, pattern in patterns.items():
        if re.search(pattern, description):
            return method
    return 'Other'


# Define the combined function
def combined_function_name(description):
    name = extract_name(description)
    if name == 'Other':
        name = categorize_name(description)  # Categorize the description as a name
        if name == 'Other':
            name = categorize_brands(description)  # Categorize the description as a brand
    return name

# Apply the combined function to the 'description' column
data['transaction_names'] = data['description'].apply(combined_function_name)
data['payment_method'] = data['description'].apply(categorize_payment_method)
data['payment_method_acronym'] = data['description'].apply(categorize_payment_method_acronyms)
data['transaction_category'] = data['transaction_names'].apply(categorize_buckets)

def format_numeric_columns(data, columns):
    # Function to remove commas and convert to integer
    def format_numeric_values(numeric_values):
        numeric_values = numeric_values.str.replace(',', '')
        return numeric_values

    # Applying the function to the relevant numeric columns
    data[columns] = data[columns].apply(format_numeric_values)
    
    # Converting those columns to appropriate data types (integer)
    data[columns] = data[columns].apply(lambda x: pd.to_numeric(x).astype(int))
    
    return data

# Example usage:
data = format_numeric_columns(data, ['amount', 'balance'])

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
        latest_iteration.text(f'{i+1}%')
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
max_amount = 70000

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
max_balance = 90000

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
        result_color = "grey"
else:
    # Count the "Other" values in the entire 'transaction_names' column
    unattributed_names = amount_filtered_data['transaction_names'].value_counts().get('Other', 0)
    
    result_text = f"Please enter a query to search for transactions | There are {unattributed_names} unattributed names"
    result_color = "gray"

st.markdown(f'<p style="color:{result_color};">{result_text}</p>', unsafe_allow_html=True)

name_filtered_data = search_transactions(keyword, amount_filtered_data)
balance_filtered_data = name_filtered_data[(name_filtered_data['amount'] >= min_amount) & (name_filtered_data['amount'] <= max_amount)]

# Dropping redundant columns
columns_to_preview = ['number_days', 'value_date','net_balance','payment_method_acronym', 'sl_no', 'chq___ref_no', 'transaction_type', 'transaction_number', 'dr___cr', 'dr___cr1', 'transaction_number']
columns_to_analyze = ['sl_no', 'transaction_number', 'dr___cr1', 'transaction_type']

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

    styled_data = dataframe.style.background_gradient(cmap='viridis')
    styled_data = styled_data.apply(lambda x: x.rank(pct=True).apply(color_date_gradient), subset=['transaction_date'])
    
    return styled_data

gradient_data = apply_gradient_to_transaction_dates(preview_data)

# Function to apply color coding based on 'credit_debit_value'
def color_based_on_credit_debit(val, color_map):
    return f'color: {color_map.get(val, "")}'

# Define a function to color the 'amount' column based on the 'credit_debit_value'
def color_credit_debit_amount(df):
    # Create a color map based on 'credit_debit_value' column
    color_map = {1: 'blue', -1: 'red'}
    
    # Apply color to 'credit_debit_value' column
    credit_debit_styles = df['credit_debit_value'].map(lambda x: color_based_on_credit_debit(x, color_map))
    
    # Apply color to 'amount' column based on 'credit_debit_value' column
    amount_styles = df['credit_debit_value'].map(lambda x: color_based_on_credit_debit(x, color_map))
    
    return credit_debit_styles, amount_styles

# Get the styles
credit_debit_styles, amount_styles = color_credit_debit_amount(visible_data)

# Create a copy of the DataFrame without the columns to be hidden
visible_data_styled = visible_data.copy()

# Apply the styles
styled_data = (visible_data_styled.style
                .apply(lambda x: credit_debit_styles, subset=['credit_debit_value'])
                .apply(lambda x: amount_styles, subset=['amount']))

# Display the styled DataFrame
st.dataframe(styled_data, hide_index=True)

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
    labels={'amount': 'Amount spent', 'balance': 'Remaining balance', 'index': 'Transaction Count'}
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
        coloraxis=dict(colorscale='BlackBody')
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
