import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
import time

# Function to scrape job listings from Indeed
def scrape_indeed_jobs(query, location, num_pages=1):
    base_url = 'https://www.indeed.com/jobs'
    jobs = []
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Use a session to maintain cookies and headers
    with requests.Session() as session:
        session.headers.update(headers)
        
        for page in range(num_pages):
            params = {
                'q': query,
                'l': location,
                'start': page * 10  # Indeed shows 10 jobs per page
            }
            
            try:
                response = session.get(base_url, params=params, timeout=10)  # Add timeout
                response.raise_for_status()  # Raise an error for bad status codes
            except requests.RequestException as e:
                st.error(f"Error fetching data: {e}")
                return jobs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_listings = soup.find_all('div', class_='job_seen_beacon')
            
            for job in job_listings:
                try:
                    title = job.find('h2', class_='jobTitle').text.strip()
                    company = job.find('span', class_='companyName').text.strip()
                    location = job.find('div', class_='companyLocation').text.strip()
                    summary = job.find('div', class_='job-snippet').text.strip()
                    link = 'https://www.indeed.com' + job.find('a')['href']
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'summary': summary,
                        'link': link
                    })
                except AttributeError as e:
                    st.warning(f"Skipping a job listing due to missing data: {e}")
                    continue
            
            # Add a delay between requests to avoid detection
            time.sleep(2)  # Wait 2 seconds before the next request
    
    return jobs

# Function to save job listings to a CSV file
def save_to_csv(jobs, filename='job_listings.csv'):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(['Title', 'Company', 'Location', 'Summary', 'Link'])
            
            # Write each job listing to the CSV file
            for job in jobs:
                writer.writerow([job['title'], job['company'], job['location'], job['summary'], job['link']])
        st.success(f"Job listings saved to '{filename}'.")
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")

# Streamlit app
def main():
    st.title("Indeed Job Scraper")
    
    # Input fields for job query and location
    query = st.text_input("Enter job title or keywords:", "Software Engineer")
    location = st.text_input("Enter location:", "New York, NY")
    num_pages = st.slider("Number of pages to scrape:", 1, 10, 1)
    
    if st.button("Search Jobs"):
        st.write(f"Searching for '{query}' jobs in '{location}'...")
        
        # Scrape jobs
        jobs = scrape_indeed_jobs(query, location, num_pages)
        
        if jobs:
            st.write(f"Found {len(jobs)} jobs:")
            for i, job in enumerate(jobs, 1):
                st.subheader(f"Job {i}: {job['title']}")
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Summary:** {job['summary']}")
                st.write(f"**Link:** [Apply Here]({job['link']})")
                st.write("---")
            
            # Save jobs to CSV
            save_to_csv(jobs)
            
            # Provide a download button for the CSV file
            try:
                with open('job_listings.csv', 'rb') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f,
                        file_name='job_listings.csv',
                        mime='text/csv',
                    )
            except Exception as e:
                st.error(f"Error creating download button: {e}")
        else:
            st.write("No jobs found.")

if __name__ == "__main__":
    main()
