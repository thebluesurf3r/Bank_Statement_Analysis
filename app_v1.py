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


# Define the combined function
def combined_function_name(description):
    name = extract_name(description)
    if name == 'Other':
        name = categorize_name(description)  # Categorize the description as a name
        if name == 'Other':
            name = categorize_brands(description)  # Categorize the description as a brand
    return name
