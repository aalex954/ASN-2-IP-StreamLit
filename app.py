import streamlit as st
import requests
import pandas as pd
import time

# Set page config
st.set_page_config(page_title="ASN-2-IP: IP Range Finder", layout="wide", initial_sidebar_state="expanded")

# Sidebar for inputs
st.sidebar.title("Settings")
organization_name = st.sidebar.text_input("Organization Name", value="microsoft")

# Function to get ASN information from BGPView API
def get_asn_info(organization_name):
    url = f"https://api.bgpview.io/search?query_term={organization_name}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/112.0.0.0 safari/537.36 edg/112.0.1722.48"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        asn_info = response.json()
        asns = asn_info.get('data', {}).get('asns', [])
        return [asn['asn'] for asn in asns], asns
    else:
        st.error(f"Failed to retrieve information for {organization_name}")
        return [], []

# Function to get ASN prefixes from RIPE NCC API
def get_asn_prefixes(asn):
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/112.0.0.0 safari/537.36 edg/112.0.1722.48"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        asn_prefix_info = response.json()
        if asn_prefix_info['status'] == 'ok':
            prefixes = asn_prefix_info.get('data', {}).get('prefixes', [])
            return [prefix['prefix'] for prefix in prefixes]
        else:
            st.error(f"Error retrieving prefixes for ASN {asn}")
            return []
    else:
        st.error(f"Failed to get response from {url}")
        return []

# Function to write analytics to a text file and display results
def write_asn_analytics(asn_prefixes):
    unique_prefixes = sorted(set(asn_prefixes))
    unique_prefix_count = len(unique_prefixes)

    with open("asn_ip_ranges.txt", "w") as f:
        for prefix in unique_prefixes:
            f.write(f"{prefix}\n")

    return unique_prefix_count, unique_prefixes

# Function to create a DataFrame from ASN analytics
def create_analytics_dataframe(asn_data):
    df = pd.DataFrame(asn_data)
    df['ASN'] = df['asn']
    df['Country Code'] = df['country_code']
    df['Description'] = df['description'].str.replace(',', '')
    df['Name'] = df['name'].str.replace(',', '')
    return df[['ASN', 'Country Code', 'Description', 'Name']]

# Function to calculate additional analytics
def calculate_additional_analytics(df, unique_prefix_count):
    unique_country_codes_count = df['Country Code'].nunique()
    unique_asn_count = df['ASN'].nunique()
    unique_names_count = df['Name'].nunique()
    unique_descriptions_count = df['Description'].nunique()

    return {
        "Unique Country Codes": unique_country_codes_count,
        "Unique ASN Numbers": unique_asn_count,
        "Unique Names": unique_names_count,
        "Unique Descriptions": unique_descriptions_count,
        "Unique Prefixes": unique_prefix_count,
    }

# Main content area
st.title("ASN-2-IP: IP Range Finder")
st.text("aalex954   https://github.com/aalex954/ASN-2-IP")


if st.sidebar.button("Find ASN IP Ranges"):
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # Step 1: Start fetching ASN information
    progress_text.text("Starting to fetch ASN information...")
    time.sleep(0.5)  # Simulate time delay

    # Step 2: API Call to fetch ASN information
    progress_text.text(f"Fetching ASN information from BGPView... https://api.bgpview.io/search?query_term=")
    progress_bar.progress(20)
    time.sleep(0.5)  # Simulating a delay for the progress bar
    as_numbers, asn_data = get_asn_info(organization_name)

    if as_numbers:
        st.write(f"Found **{len(as_numbers)}** ASNs for **{organization_name}**")

        # Step 3: API Call to fetch ASN prefixes
        progress_text.text(f"Fetching ASN prefixes from RIPE NCC... https://stat.ripe.net/data/announced-prefixes/data.json?resource=")
        progress_bar.progress(40)
        time.sleep(0.5)  # Simulating a delay for the progress bar

        all_prefixes = []
        for asn in as_numbers:
            prefixes = get_asn_prefixes(asn)
            all_prefixes.extend(prefixes)

        if all_prefixes:
            # Step 4: Process and display analytics
            progress_text.text("Processing and displaying analytics...")
            progress_bar.progress(70)
            time.sleep(0.5)  # Simulating a delay for the progress bar
            unique_prefix_count, unique_prefixes = write_asn_analytics(all_prefixes)

            df = create_analytics_dataframe(asn_data)
            analytics = calculate_additional_analytics(df, unique_prefix_count)

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Country Codes", analytics['Unique Country Codes'])
            col2.metric("ASN Numbers", analytics['Unique ASN Numbers'])
            col3.metric("Prefixes", analytics['Unique Prefixes'])
            col4.metric("Names", analytics['Unique Names'])
            col5.metric("Descriptions", analytics['Unique Descriptions'])

            # Step 5: Display Data Table
            progress_text.text("Displaying ASN analytics data table...")
            st.write("### ASN Analytics Data Table")
            st.dataframe(df, width=1000, height=400)

            # Step 6: Provide Download Option
            progress_bar.progress(90)
            progress_text.text("Finalizing download options...")
            if st.download_button('Download ASN IP Ranges', data='\n'.join(unique_prefixes), file_name='asn_ip_ranges.txt', mime='text/plain'):
                st.success('File downloaded successfully!')

            # Step 7: Display ASN Numbers for Manual Copy
            st.write("### Copy ASN Numbers")
            sorted_as_numbers = sorted(map(int, as_numbers))
            st.text_area("ASN Numbers (CSV format)", value=','.join(map(str, sorted_as_numbers)), height=100)

            progress_bar.progress(100)
            progress_text.text("Done!")

        else:
            st.warning("No prefixes found for the ASNs")
            progress_bar.progress(100)
            progress_text.text("Done with warnings.")
    else:
        st.warning("No ASNs found for the organization")
        progress_bar.progress(100)
        progress_text.text("Done with warnings.")
