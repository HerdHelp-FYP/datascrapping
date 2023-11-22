import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError
from scrapy.utils.project import get_project_settings
from fake_useragent import UserAgent

class WileySpider(scrapy.Spider):
    name = 'wiley_spider'
    start_urls = ['https://onlinelibrary.wiley.com/action/doSearch?AllField=veterinary+disease&SeriesKey=19391676']
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy_rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'scrapy_rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        'ROTATING_PROXY_LIST': get_project_settings().get('PROXY_LIST'),
        'ROTATING_PROXY_BACKOFF_BASE': 300,
        'ROTATING_PROXY_BACKOFF_CAP': 1200,
        'ROTATING_PROXY_CLOSE_SPIDER': False,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, errback=self.errback_http, dont_filter=True)

    def parse(self, response):
        # Extract links to individual articles
        article_links = response.css('span.hlFld-Title a.visitable::attr(href)').getall()

        # Follow each article link and extract content from article body
        for link in article_links:
            yield response.follow(link, self.parse_article, cb_kwargs={'retry': 3})

    def parse_article(self, response, retry):
        # Check if the request was successful, otherwise retry
        if response.status == 200:
            # Extract title and content from the article
            article_title = response.css('h1.citation__title::text').get().strip()
            article_content = response.css('div.article__body::text').getall()
            cleaned_content = ' '.join(map(str.strip, article_content)).strip()

            # Return the extracted data
            yield {
                'title': article_title,
                'content': cleaned_content
            }
        elif retry > 0:
            # Retry the request
            yield response.request.replace(dont_filter=True, cb_kwargs={'retry': retry - 1})
        else:
            self.logger.error(f"Failed to fetch {response.url} after multiple retries")

    def errback_http(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)
        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)
        elif failure.check(TimeoutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
