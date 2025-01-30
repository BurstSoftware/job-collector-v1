import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape job listings from Indeed
def scrape_indeed_jobs(query, location, num_pages=1):
    base_url = 'https://www.indeed.com/jobs'
    jobs = []
    
    for page in range(num_pages):
        params = {
            'q': query,
            'l': location,
            'start': page * 10  # Indeed shows 10 jobs per page
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_listings = soup.find_all('div', class_='job_seen_beacon')
            
            for job in job_listings:
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
    
    return jobs

# Function to save job listings to a CSV file
def save_to_csv(jobs, filename='job_listings.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Title', 'Company', 'Location', 'Summary', 'Link'])
        
        # Write each job listing to the CSV file
        for job in jobs:
            writer.writerow([job['title'], job['company'], job['location'], job['summary'], job['link']])

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
            st.success("Job listings saved to 'job_listings.csv'.")
        else:
            st.write("No jobs found.")

if __name__ == "__main__":
    main()
