from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import json

class FacebookScraper:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None
        
    def initialize_driver(self):
        """Initialize the Edge webdriver with custom options"""
        options = webdriver.EdgeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        self.driver = webdriver.Edge(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def simulate_human_typing(self, element, text):
        """Simulate human-like typing patterns"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.7))
                
    def login(self):
        """Login to Facebook"""
        self.driver.get("https://www.facebook.com/login")
        
        # Enter email
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        self.simulate_human_typing(email_input, self.email)
        
        # Enter password
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "pass"))
        )
        self.simulate_human_typing(password_input, self.password)
        
        # Click login button
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        ActionChains(self.driver)\
            .move_to_element(login_button)\
            .pause(random.uniform(0.2, 0.4))\
            .click()\
            .perform()
            
        time.sleep(15)
        
    def navigate_to_profile(self, profile_url):
        """Navigate to a specific Facebook profile"""
        self.driver.get(profile_url)
        time.sleep(4)
        
    def slow_scroll(self, step=500):
        """Scroll the page slowly"""
        self.driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(2)
        
    def extract_posts_with_bs(self):
        """Extract posts data using BeautifulSoup"""
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        posts_data = []
        
        posts = soup.find_all("div", {"class": "x1n2onr6 x1ja2u2z"})
        
        for post in posts:
            try:
                message_elements = post.find_all("div", {"data-ad-preview": "message"})
                post_text = " ".join([msg.get_text(strip=True) for msg in message_elements])
                
                likes_element = post.select_one("span.xt0b8zv.x1jx94hy.xrbpyxo.xl423tq > span > span")
                likes = likes_element.get_text(strip=True) if likes_element else None
                
                comments_element = post.select("div > div > span > div > div > div > span > span.html-span ")
                comments = comments_element[0].text if comments_element else None
                
                
                shares_element =post.select("div > div > span > div > div > div > span > span.html-span ")
                shares = shares_element[1].text if shares_element else None

                timeelement=post.select_one("div.xu06os2.x1ok221b > span > div > span > span > a > span")
                post_time= timeelement.get_text(strip=True) if timeelement else None

                
                posts_data.append({
                    "post_text": post_text,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "post_time": post_time
                })
            except Exception as e:
                print("Error extracting post data:", e)
                
        return posts_data
        
    def remove_duplicates(self, data_list):
        """Remove duplicate posts"""
        seen = set()
        unique_data = []
        for data in data_list:
            data_tuple = tuple(data.items())
            if data_tuple not in seen:
                seen.add(data_tuple)
                unique_data.append(data)
        return unique_data
        
    def scrape_posts(self, max_posts):
        """Scrape a specified number of posts"""
        all_posts = []
        
        while len(all_posts) < max_posts:
            posts = self.extract_posts_with_bs()
            all_posts.extend(posts)
            all_posts = self.remove_duplicates(all_posts)
            print(f"Extracted {len(all_posts)} unique posts so far.")
            # print(all_posts)
            self.slow_scroll()
            
            if len(all_posts) >= max_posts:
                break
                
        return all_posts[:max_posts]



    def print_posts(self, posts_data):
        """Print the scraped posts data"""
        for idx, post in enumerate(posts_data, start=1):
            print(f"Post {idx}:")
            print(f"Text: {post['post_text']}")
            print(f"Likes: {post['likes']}")
            print(f"Comments: {post['comments']}")
            print(f"Shares: {post['shares']}")
            print(f"Time Posted: {post['post_time']}")
            print("-" * 50)
            
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    # Initialize the scraper
    scraper = FacebookScraper("yourEmail", "yourPassword")
    
    try:
        # Setup and login
        scraper.initialize_driver()
        scraper.login()
        
        # Navigate to Cristiano Ronaldo's profile
        scraper.navigate_to_profile("https://www.facebook.com/cnn")
        
        # Scrape 10 posts
        posts_data = scraper.scrape_posts(max_posts=10)
        
        # Print the results
        scraper.print_posts(posts_data)
        
    finally:
        # Clean up
        scraper.close()

