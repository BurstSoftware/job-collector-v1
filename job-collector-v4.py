import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Streamlit App Title
st.title("Job Scraper")

# Input for the job board URL
url = st.text_input("Enter the job board URL:", "https://example-job-board.com/jobs")

# Button to trigger scraping
if st.button("Scrape Jobs"):
    if url:
        try:
            # Send an HTTP GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all job listings (adjust the selector based on the website's structure)
            job_listings = soup.find_all('div', class_='job-listing')

            # Check if any job listings were found
            if job_listings:
                st.success(f"Found {len(job_listings)} job listings!")
                st.write("---")

                # Initialize a list to store job data
                jobs_data = []

                # Loop through each job listing and extract relevant information
                for job in job_listings:
                    try:
                        title = job.find('h2', class_='job-title').text.strip()
                    except AttributeError:
                        title = "N/A"
                    try:
                        company = job.find('div', class_='company-name').text.strip()
                    except AttributeError:
                        company = "N/A"
                    try:
                        location = job.find('div', class_='job-location').text.strip()
                    except AttributeError:
                        location = "N/A"
                    try:
                        link = job.find('a')['href']
                    except (AttributeError, TypeError):
                        link = "N/A"

                    # Add job data to the list
                    jobs_data.append({
                        "Title": title,
                        "Company": company,
                        "Location": location,
                        "Link": link
                    })

                    # Display the extracted information in Streamlit
                    st.subheader(title)
                    st.write(f"**Company:** {company}")
                    st.write(f"**Location:** {location}")
                    st.write(f"**Link:** [Apply Here]({link})")
                    st.write("---")

                # Convert the jobs data to a DataFrame
                jobs_df = pd.DataFrame(jobs_data)

                # Display the DataFrame in Streamlit
                st.write("### All Job Listings")
                st.dataframe(jobs_df)

                # Add a button to export the data to a CSV file
                if st.button("Export to CSV"):
                    csv = jobs_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="job_listings.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("No job listings found on this page.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred while fetching the webpage: {e}")
    else:
        st.warning("Please enter a valid URL.")
