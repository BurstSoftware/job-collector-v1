import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Function to scrape job listings from Indeed using Selenium
def scrape_indeed_jobs(query, location, num_pages=1):
    jobs = []
    
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # Disable sandboxing
    options.add_argument('--disable-dev-shm-usage')  # Disable shared memory usage
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  # Set user agent
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        for page in range(num_pages):
            url = f"https://www.indeed.com/jobs?q={query}&l={location}&start={page * 10}"
            driver.get(url)
            time.sleep(3)  # Wait for the page to load
            
            # Scroll to load all job listings
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Find job listings
            job_listings = driver.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')
            
            for job in job_listings:
                try:
                    title = job.find_element(By.CSS_SELECTOR, 'h2.jobTitle').text.strip()
                    company = job.find_element(By.CSS_SELECTOR, 'span.companyName').text.strip()
                    location = job.find_element(By.CSS_SELECTOR, 'div.companyLocation').text.strip()
                    summary = job.find_element(By.CSS_SELECTOR, 'div.job-snippet').text.strip()
                    link = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'summary': summary,
                        'link': link
                    })
                except Exception as e:
                    st.warning(f"Skipping a job listing due to missing data: {e}")
                    continue
            
            # Add a delay between pages to avoid detection
            time.sleep(random.uniform(2, 5))
    
    finally:
        driver.quit()  # Close the browser
    
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
