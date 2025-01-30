import streamlit as st
from playwright.sync_api import sync_playwright
import csv
import time
import random

# Function to scrape job listings from Indeed using Playwright
def scrape_indeed_jobs(query, location, num_pages=1):
    jobs = []
    
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for page_num in range(num_pages):
            url = f"https://www.indeed.com/jobs?q={query}&l={location}&start={page_num * 10}"
            page.goto(url)
            time.sleep(3)  # Wait for the page to load
            
            # Scroll to load all job listings
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find job listings
            job_listings = page.query_selector_all('div.job_seen_beacon')
            
            for job in job_listings:
                try:
                    title = job.query_selector('h2.jobTitle').inner_text().strip()
                    company = job.query_selector('span.companyName').inner_text().strip()
                    location = job.query_selector('div.companyLocation').inner_text().strip()
                    summary = job.query_selector('div.job-snippet').inner_text().strip()
                    link = job.query_selector('a').get_attribute('href')
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'summary': summary,
                        'link': f"https://www.indeed.com{link}"
                    })
                except Exception as e:
                    st.warning(f"Skipping a job listing due to missing data: {e}")
                    continue
            
            # Add a delay between pages to avoid detection
            time.sleep(random.uniform(2, 5))
        
        browser.close()
    
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
