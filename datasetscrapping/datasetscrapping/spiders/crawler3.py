import scrapy

class AVMASpider(scrapy.Spider):
    name = 'avma_spider'
    start_urls = ['https://www.avma.org/search?search=Animal+Disease']

    def parse(self, response):
        # Extract links to individual articles
        article_links = response.css('div.view-content a.avma-search-result__link::attr(href)').getall()

        # Follow each article link and extract content from the specified elements
        for link in article_links:
            yield response.follow(link, self.parse_article)

    def parse_article(self, response):
        # Extract title and content from the specified elements
        article_title = response.css('div.block-layout-builder h1.field--name-title::text').get(default='').strip()
        article_content = response.css('div.avma__wysiwyg--content div.field--name-body p::text').getall()
        cleaned_content = ' '.join(map(str.strip, article_content)).strip()

        # Check if the title is found, else log an error
        if article_title:
            # Clean HTML tags from the content
            cleaned_content = self.clean_html_tags(cleaned_content)

            # Save the data to a .txt file
            with open('output1.txt', 'a', encoding='utf-8') as file:
                file.write(f"{article_title}, {cleaned_content}\n")
        else:
            self.logger.error(f"Title not found in {response.url}")

    def clean_html_tags(self, text):
        # Remove HTML tags from the text
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
