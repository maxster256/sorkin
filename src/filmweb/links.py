import requests
from bs4 import BeautifulSoup

class LinksFetcher:
    def __init__(self):
        self.domain = "https://www.filmweb.pl"
        self.reviewsPath = "https://filmweb.pl/reviews?page="
        # self.searchPath = "https://www.filmweb.pl/films/search?orderBy=popularity&descending=true&page="
        self.searchPath = "https://www.filmweb.pl/films/search?endRate=3&orderBy=popularity&descending=true&startRate=2&page="
        self.seriesSearchPath = "https://www.filmweb.pl/serials/search?orderBy=popularity&descending=true&page="
        self.ajaxPath = "https://www.filmweb.pl/ajax/film/user/reviews/"

    def get_review_links_from_pages(self, func, fromPage, toPage):
        """
        Returns links to Filmweb's staff movie reviews from multiple staff reviews pages.
        :param fromPage: index from which staff reviews pages are parsed
        :param toPage: index to which staff reviews pages are parsed
        :return: set of links to Filmweb's staff movie reviews
        """
        links = set()

        for page in range(fromPage, toPage):
            print("Downloading links from page {}/{}...".format(page, toPage))
            links.update(func(page))

        return links

    def getUserReviewLinksFromAjaxPages(self, fromPage, toPage):
        """
        Returns links to user reviews from Filmweb's AJAX carousel on '/reviews' page.
        :param fromPage: index of the page to start parsing
        :param toPage: index of the page to end parsing
        :return: list of links to reviews written by Filmweb's users
        """
        links = set()

        for page in range(fromPage, toPage):
            print("Downloading links from AJAX page {}/{}...".format(page, toPage))
            links.update(self.getUserReviewLinksFromAjaxPage(page))
        
        return links

    def getUserReviewLinksFromAjaxPage(self, pageNumber):
        """
        Returns links to user reviews from  Filmweb's AJAX carousel page found on '/reviews' page.
        :param pageNumber: index of AJAX carousel page to parse
        :return: list of links from given AJAX carousel page
        """
        r = requests.get(self.ajaxPath + str(pageNumber))
        parser = BeautifulSoup(r.text, 'html.parser')

        results = set()
        try:
            links = parser.find_all(class_="review__title")
            
            for link_wrapper in links:
                link = link_wrapper.find("a")
                if link:
                    results.add(link.attrs['href'])

            return results
        except Exception as error:
            print(error)
            pass
        
    def get_staff_review_links_from_page(self, pageNumber):
        """
        Returns links to Filmweb's staff movie reviews from a single staff reviews page.
        :param pageNumber: index of staff reviews page to parse
        :return: set of links to Filmweb's staff movie reviews
        """
        r = requests.get(self.reviewsPath + str(pageNumber))
        parser = BeautifulSoup(r.text, 'html.parser')
        results, links = [], set()

        try:
            featured_film_reviews = parser.find(class_="section filmTopReviews page__section")
            film_reviews = parser.find(class_="section filmReviews page__section")

            if film_reviews:
                results.extend(film_reviews.find_all("h3", class_="review__title"))

            if featured_film_reviews:
                results.extend(featured_film_reviews.find_all("h3", class_="review__title"))

            for result in results:
                link = result.find("a")
                if link:
                    links.add(link.attrs["href"])

            return links
        
        except AssertionError as error:
            print("Error when fetching links from page {}: '{}'".format(pageNumber, error))

    def get_links_to_user_movie_reviews_from_search_pages(self, fromPage, toPage):
        """
        Returns set of links to movies from Filmweb search results.
        :param fromPage: index from which search results are parsed
        :param toPage: index to which search results are parsed
        :param searchPath: relative path to search page (with search parameters)
        :return: set of links to movie pages on Filmweb
        """
        links = set()
        
        for page in range(fromPage, toPage):
            print("Downloading links to movies from page {}/{}...".format(page, toPage))
            links.update(self.get_links_to_user_movie_reviews_from_search_page(page, self.searchPath))
        
        return links

    def get_links_to_user_movie_reviews_from_search_page(self, pageNumber, searchPath):
        """
        Returns list of links to movie reviews from a given Filmweb search page.
        :param pageNumber: search results page pagination index
        :param searchPath: relative path to search page (with search parameters)
        :return: list of links to user movie reviews on Filmweb
        """
        r = requests.get(searchPath + str(pageNumber), headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"})
        parser = BeautifulSoup(r.text, 'html.parser')
        movie_links = [], review_links = []

        try:
            relative_movie_links = parser.find_all(class_="filmPreview__link")
       
            for link in relative_movie_links:
                movie_links.append(link.attrs['href'])

            for link in movie_links:
                review_links.extend(self.get_links_to_user_reviews_from_movie_page(movie_links))

            return review_links

        except AssertionError as error:
            print("Error when fetching links from page {}: '{}'".format(pageNumber, error))

    def get_links_to_user_reviews_from_movie_page(self, moviePage):
        """
        Returns a list of links to Filmweb users' reviews from a given movie page link.
        :param moviePage: link to a Filmweb movie page
        :return: list of user review links from Filmweb
        """
        r = requests.get(self.domain + moviePage + "/reviews", headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"})
        parser = BeautifulSoup(r.text, 'html.parser')
        links = []

        print("Getting links to reviews from '{}'...".format(moviePage))

        try:
            review_containers = parser.find_all(class_="pageBox")

            for container in review_containers:
                if container.previous_sibling and container.previous_sibling.find(class_="inline") and container.previous_sibling.find(class_="inline").text == "recenzje Użytkowników":
                    
                    user_review_links = container.find_all(class_=["l", "normal"])

                    for link in user_review_links:
                        links.append(link.attrs['href'])

            return links
        except AssertionError as error:
            print("Error when fetching links from page '{}': '{}'".format(moviePage, error))