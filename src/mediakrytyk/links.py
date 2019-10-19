import requests
from bs4 import BeautifulSoup


class LinksFetcher:
    def __init__(self):
        self.reviews_path = "https://film.org.pl/r/page/"

    def get_review_links_from_pages(self, func, fromPage, toPage):
        """
        Returns links to Film.org.pl's movie reviews from multiple reviews pages.
        :param fromPage: index from which reviews pages are parsed
        :param toPage: index to which reviews pages are parsed
        :return: set of links to Film.org.pl's movie reviews
        """
        links = set()

        for page in range(fromPage, toPage):
            print("Downloading links from page {}/{}...".format(page, toPage))
            links.update(func(page))

        return links

    def get_review_links_from_page(self, pageNumber):
        """
        Returns list of links to movie reviews from a given Film.org.pl reviews page.
        :param pageNumber: search results page pagination index
        :param searchPath: relative path to search page (with search parameters)
        :return: list of links to user movie reviews on Film.org.pl
        """
        try:
            r = requests.get(self.reviews_path + str(pageNumber), headers={
                "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"})
            parser = BeautifulSoup(r.text, 'html.parser')

            reviews = parser.find_all(class_="title")
            links = []

            for review in reviews:
                h4 = review.find('h4')

                if h4:
                    a = h4.find('a')
                    if a and 'href' in a.attrs:
                        links.append(a.attrs['href'])

            return links

        except Exception as error:
            print("Error when fetching links from page {}: '{}'".format(pageNumber, error))
            return []
