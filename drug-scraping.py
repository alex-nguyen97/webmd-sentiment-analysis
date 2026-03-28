# from WebMDScraper.items import WebmdscraperItem
from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request
from scrapy.selector import Selector
from pathlib import Path


OUTPUT_CSV = Path(__file__).with_name('webmd_drug_reviews.csv')
NUMBER_OF_CHARACTERS = 1
NUMBER_OF_SUB_CHARACTERS = 1
NUMBER_OF_DRUGS = 1
SPIDER_SETTINGS = {
    'DOWNLOAD_DELAY': 2,
    'RANDOMIZE_DOWNLOAD_DELAY': True,
    'CONCURRENT_REQUESTS': 4,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 2,
    'AUTOTHROTTLE_MAX_DELAY': 15,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
}


class WebmdSpider(Spider):
    name = 'webmd_spider'
    allowed_domains = ['http://www.webmd.com/']
    start_urls = ['https://www.webmd.com/drugs/2/index']
    drug_dict = {}
    custom_settings = SPIDER_SETTINGS | {
        'FEEDS': {
            str(OUTPUT_CSV): {
                'format': 'csv',
                'overwrite': True,
            },
        },

    }

    def parse(self, response):
        print("Processing:" + response.url)
        drugs_a_to_z = response.xpath(
            '//ul[@class="browse-letters squares alpha-letters"]/li/a/@href'
        ).getall()
        for i in range(NUMBER_OF_CHARACTERS):
            print(response.urljoin(drugs_a_to_z[i]))
            yield Request(response.urljoin(drugs_a_to_z[i]),
                          callback=self.parse_sub,
                          dont_filter=True)

    def parse_sub(self, response):
        print("Processing sub drug category:" + response.url)
        sub = response.xpath(
            '//ul[contains(@class,"browse-letters squares sub-alpha sub-alpha-letters")]//a/@href'
        ).getall()
        for i in range(NUMBER_OF_SUB_CHARACTERS):
            yield Request(response.urljoin(sub[i]),
                          callback=self.parse_drug,
                          dont_filter=True)

    def parse_drug(self, response):
        print("Processing drug:" + response.url)
        drug_list = response.xpath(
            '//div[@class="drugs-search-list-conditions"]//li/a')
        for i in range(NUMBER_OF_DRUGS):
            yield Request(response.urljoin(drug_list[i].xpath("@href")[0].extract()),
                          callback=self.parse_details,
                          meta={'Drug': drug_list[i].xpath(
                              "text()")[0].extract().lower()},
                          dont_filter=True)

    def parse_details(self, response):
        print("Processing drug details:" + response.url)
        review_url = response.xpath(
            '//li[contains(@class,"tab-7")]//a/@href').get(default='').strip()

        if review_url:
            yield Request(response.urljoin(review_url.replace(" ", '')),
                          callback=self.parse_reviews,
                          meta={'Drug': response.meta['Drug'],
                                'Review_URL': review_url,
                                }, dont_filter=True)

    def parse_reviews(self, response):
        # Extract overall ratings
        overall_rating = response.xpath(
            '//span[@class="rat-num"]/text()').get()
        effectiveness = response.xpath(
            '//div[contains(@class,"effect-rating")]//div[contains(@class,"webmd-rate")]/@aria-valuenow').get()
        ease_of_use = response.xpath(
            '//div[contains(@class,"ease-rating")]//div[contains(@class,"webmd-rate")]/@aria-valuenow').get()
        satisfaction = response.xpath(
            '//div[contains(@class,"satis-rating")]//div[contains(@class,"webmd-rate")]/@aria-valuenow').get()

        # print as json object
        print({
            'Drug': response.meta['Drug'],
            'OverallPageRating': overall_rating,
            'EffectivenessPageRating': effectiveness,
            'EaseOfUsePageRating': ease_of_use,
            'SatisfactionPageRating': satisfaction,
        })

        # Parse individual reviews
        reviews_list = response.xpath('//div[@class="review-details-holder"]')
        print(f"Found {len(reviews_list)} reviews")

        for review in reviews_list:
            # Extract user details
            details_text = ' '.join(review.xpath(
                './/div[@class="details"]//text()').getall()).strip()

            # Extract date
            date = review.xpath('.//div[@class="date"]/text()').get()

            # Extract condition
            condition = review.xpath(
                './/strong[@class="condition"]/text()').get()
            if condition:
                condition = condition.replace('Condition:', '').strip()

            # Extract ratings for this review
            review_overall = review.xpath(
                './/div[@class="overall-rating"]//div[@class="webmd-rate on-mobile"]/@aria-valuenow').get()
            review_effectiveness = review.xpath(
                './/div[@class="categories"]//section[1]//div[@class="webmd-rate on-mobile"]/@aria-valuenow').get()
            review_ease = review.xpath(
                './/div[@class="categories"]//section[2]//div[@class="webmd-rate on-mobile"]/@aria-valuenow').get()
            review_satisfaction = review.xpath(
                './/div[@class="categories"]//section[3]//div[@class="webmd-rate on-mobile"]/@aria-valuenow').get()

            # Extract description
            description = ' '.join(review.xpath(
                './/p[@class="description-text"]//text()').getall()).strip()

            # Extract likes/dislikes
            likes = review.xpath(
                './/div[@class="helpful"]//span[@class="likes"]/text()').get()
            dislikes = review.xpath(
                './/div[@class="not-helpful"]//span[@class="dislikes"]/text()').get()

            # Yield review item
            yield {
                'Drug': response.meta['Drug'],
                'OverallPageRating': overall_rating,
                'EffectivenessPageRating': effectiveness,
                'EaseOfUsePageRating': ease_of_use,
                'SatisfactionPageRating': satisfaction,
                'ReviewDetails': details_text,
                'Date': date,
                'Condition': condition,
                'ReviewOverallRating': review_overall,
                'ReviewEffectiveness': review_effectiveness,
                'ReviewEaseOfUse': review_ease,
                'ReviewSatisfaction': review_satisfaction,
                'ReviewText': description,
                'Likes': likes or 0,
                'Dislikes': dislikes or 0,
            }


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(WebmdSpider)
    process.start()
