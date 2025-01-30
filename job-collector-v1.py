import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to scrape job listings from Indeed
def scrape_indeed_jobs(query, location):
    base_url = 'https://www.indeed.com/jobs'
    params = {
        'q': query,
        'l': location
    }
    
    response = requests.get(base_url, params=params)
    jobs = []
    
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

# Streamlit app
def main():
    st.title("Indeed Job Scraper")
    
    # Input fields for job query and location
    query = st.text_input("Enter job title or keywords:", "Software Engineer")
    location = st.text_input("Enter location:", "New York, NY")
    
    if st.button("Search Jobs"):
        st.write(f"Searching for '{query}' jobs in '{location}'...")
        
        # Scrape jobs
        jobs = scrape_indeed_jobs(query, location)
        
        if jobs:
            st.write(f"Found {len(jobs)} jobs:")
            for i, job in enumerate(jobs, 1):
                st.subheader(f"Job {i}: {job['title']}")
                st.write(f"**Company:** {job['company']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Summary:** {job['summary']}")
                st.write(f"**Link:** [Apply Here]({job['link']})")
                st.write("---")
        else:
            st.write("No jobs found.")

if __name__ == "__main__":
    main()
