import scrapy
import json
import logging

from math import ceil


class PetitionSpider(scrapy.Spider):
    name = "petitions"

    def __init__(self, search=None, *args, **kwargs):
        super(PetitionSpider, self).__init__(*args, **kwargs)
        self.base_url = f"https://www.change.org/search?q={search}"

    def start_requests(self):
        """
        Called when the spider is started, gets the first page of search
        results.
        """
        yield scrapy.Request(url=self.base_url, callback=self.parse_first_results)

    def get_page_count(self, results_text):
        """
        Calculates how many pages of search results there sould be, based on
        the text saying how many results there are.
        """
        results = int(results_text.split()[0].replace(",", ""))
        return int(ceil(results / 10.0))

    def parse_first_results(self, response):
        """
        Special case for first page of search results.
        Creates a request for each page of search of results.
        """
        yield from self.parse_search_results(response)

        pages = self.get_page_count(response.css(".mhxs::text").get())
        logging.info(f"{pages} pages to scrape")

        for offset in range(10, pages * 10, 10):
            url = self.base_url + f"&offset={offset}"
            yield scrapy.Request(url=url, callback=self.parse_search_results)

    def parse_search_results(self, response):
        """
        Follow links to all search results.
        """
        petition_links = response.css("a.js-click-search-result")
        yield from response.follow_all(petition_links, self.parse_petition)

    def parse_petition(self, response):
        """
        Extract data to be saved from each petition page.
        """
        # Lots of useful data is available in a Javascript block that can be
        # parsed as JSON.
        petition_data = json.loads(
            response.css("head script::text")[0].get().strip()[29:-1]
        )["petition"]

        # Petition descriptions can appear in one of two different elements
        # this gets the description form whichever one works.
        description_parts = response.css(".rte *").getall() or response.css("div.description div *").getall()

        yield {
            "url": response.url,
            "title": response.css("h1.petition-title::text").get().strip(),
            "created": petition_data["createdAt"],
            "user_id": petition_data["user"]["id"],
            "user_display_name": petition_data["user"]["displayName"],
            "signature_total": petition_data["signatureCount"]["total"],
            "signature_target": petition_data["signatureCount"]["goal"],
            "description": "\n".join(description_parts),
        }
