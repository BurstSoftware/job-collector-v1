def main():
    st.title("Indeed Job Scraper")
    
    query = st.text_input("Enter job title or keywords:", "Software Engineer")
    location = st.text_input("Enter location:", "New York, NY")
    num_pages = st.slider("Number of pages to scrape:", 1, 10, 1)
    
    if st.button("Search Jobs"):
        st.write(f"Searching for '{query}' jobs in '{location}'...")
        
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
        else:
            st.write("No jobs found.")
