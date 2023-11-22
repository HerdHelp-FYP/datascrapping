import scrapy
from scrapy_selenium import SeleniumRequest

class USDAAnimalDiseaseSpider(scrapy.Spider):
    name = 'usda_animal_disease'
    start_urls = ['https://www.aphis.usda.gov/aphis/ourfocus/animalhealth/animal-disease-information']

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse, wait_time=10)

    def clean_text(self, text):
        # Function to clean the text by removing special characters, HTML tags, etc.
        cleaned_text = " ".join(text.split())  # Remove extra spaces and newlines
        cleaned_text = cleaned_text.replace("&nbsp;", " ")  # Replace non-breaking space
        cleaned_text = scrapy.Selector(text=cleaned_text).xpath('//text()').get()  # Remove HTML tags
        cleaned_text = cleaned_text.strip() if cleaned_text else None
        return cleaned_text

    def parse(self, response):
        # Extract links from the table and follow them
        for disease_link in response.css('.table a'):
            disease_url = response.urljoin(disease_link.attrib['href'])
            yield SeleniumRequest(url=disease_url, callback=self.parse_disease_page, wait_time=10)

    def parse_disease_page(self, response):
        main_content = response.css('.col-md-8.span8')
        if main_content:
            title = self.clean_text(main_content.css('.contentTitle::text').get())

            # Extract all paragraphs inside <div class="col-md-8 span8">
            paragraphs = main_content.css('div.col-md-8.span8 p::text').getall()
            cleaned_paragraphs = [self.clean_text(p) for p in paragraphs if self.clean_text(p)]

            # Format the data
            formatted_data = f"{title}, {' '.join(cleaned_paragraphs)}"

            # Write the data to a text file
            with open('output.txt', 'a', encoding='utf-8') as file:
                file.write(formatted_data + '\n')

            yield {
                'title': title,
                'content_paragraphs': cleaned_paragraphs
            }
