import scrapy
from scrapy.http import HtmlResponse

class BiomedCentralSpider(scrapy.Spider):
    name = 'biomed_central'
    start_urls = ['https://www.biomedcentral.com/search?query=animal+disease&searchType=publisherSearch']

    def parse(self, response):
        # Extract the initial set of article links
        links = response.css('a[data-test="title-link"]::attr(href)').extract()
        for link in links:
            # Check if the URL has a scheme
            if not link.startswith(('http://', 'https://')):
                link = 'http://' + link  # You can use 'https://' if the site uses HTTPS

            yield scrapy.Request(url=link, callback=self.parse_article)

        # Check for next page and follow the link
        next_page = response.css('span:contains("Next page")::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_article(self, response):
        # Extract information from the article page
        title = response.css('h1.u-text-lg::text').get()
        sections = response.css('section[data-title]')

        # Extract content from each section
        content = {}
        for section in sections:
            section_title = section.css('h2.c-article-section__title::text').get()
            section_content = section.css('div.c-article-section__content').extract_first()
            content[section_title] = section_content

        # Print or save the extracted data as needed
        print(f'Title: {title}')
        print('Sections:')
        for section_title, section_content in content.items():
            print(f'{section_title}: {section_content}')
        print('-' * 50)

        # You can save the data to a file or database instead of printing it

# Run the spider using the command: scrapy runspider your_spider_file.py -o output.json
