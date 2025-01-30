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
