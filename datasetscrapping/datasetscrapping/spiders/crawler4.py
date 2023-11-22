import os
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

class WoahSpider(scrapy.Spider):
    name = 'woah_spider'
    start_urls = ['https://www.woah.org/en/what-we-do/standards/codes-and-manuals/terrestrial-code-online-access/']

    def __init__(self):
        options = Options()
        options.headless = True  # Run Chrome in headless mode (no GUI)

        # Set ChromeDriver executable path through PATH environment variable
        chrome_driver_path = 'C:/Users/admin/Desktop/dataset_scrapper/chromedriver.exe'
        os.environ['PATH'] += ';' + chrome_driver_path

        self.driver = webdriver.Chrome(options=options)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(2)  # Wait for JavaScript to load the content (adjust the wait time if needed)

        # Get the fully rendered HTML content
        fully_rendered_html = self.driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(fully_rendered_html, 'html.parser')

        # Extract data using BeautifulSoup selectors
        chapter_links = soup.select('div.oe_bloc2 table tbody tr td p.sommaire-libelle-chapitre a[href]')
        for link in chapter_links:
            chapter_url = link['href']
            chapter_url = self.start_urls[0] + chapter_url 
            yield scrapy.Request(url=chapter_url, callback=self.parse_content)

        # Close the driver when done
        self.driver.quit()

    def parse_content(self, response):
        # Parse individual chapter pages if needed
        chapter_title = response.css('div.codes-and-manuals div.oe_bloc2 div.code-terrestre p.document-chapitre-intitule::text').get(default='').strip()
        chapter_content = response.css('div.codes-and-manuals div.oe_bloc2 div.code-terrestre p.style-standard-ouvrage::text').getall()
        cleaned_content = ' '.join(map(str.strip, chapter_content)).strip()
        

        #if chapter_title and cleaned_content:
        with open('woah_output.txt', 'a', encoding='utf-8') as file:
            file.write(f"{chapter_title}, {cleaned_content}\n")
        #else:
        #    self.logger.error(f"Title or content not found in {response.url}")
