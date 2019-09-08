import requests
from bs4 import BeautifulSoup

class LinksFetcher:
    def __init__(self):
        self.domain = "https://www.filmweb.pl"
        self.reviewsPath = "https://filmweb.pl/reviews?page="
        # self.searchPath = "https://www.filmweb.pl/films/search?orderBy=popularity&descending=true&page="
        self.searchPath = "https://www.filmweb.pl/films/search?orderBy=popularity&descending=false&startCount=70000&page="

    def getReviewLinksFromPages(self, fromPage, toPage):
        links = set()
        
        for page in range(fromPage, toPage):
            print("Downloading links from page {}/{}...".format(page, toPage))
            links.update(self.getReviewLinksFromPage(page))
        
        return links
        
    def getReviewLinksFromPage(self, pageNumber):
        r = requests.get(self.reviewsPath + str(pageNumber))
        parser = BeautifulSoup(r.text, 'html.parser')

        try:
            featured_film_reviews = parser.find(class_="section filmTopReviews page__section")
            film_reviews = parser.find(class_="section filmReviews page__section")

            results, links = [], set()

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

    def getLinksToMoviesFromSearchPages(self, fromPage, toPage):
        links = set()
        
        for page in range(fromPage, toPage):
            print("Downloading links to movies from page {}/{}...".format(page, toPage))
            links.update(self.getLinksToMoviesFromSearchPage(page))
        
        return links

    def getLinksToMoviesFromSearchPage(self, pageNumber):
        r = requests.get(self.searchPath + str(pageNumber), headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"})
        parser = BeautifulSoup(r.text, 'html.parser')

        movie_links = []

        try:
            relative_movie_links = parser.find_all(class_="filmPreview__link")
       
            for link in relative_movie_links:
                movie_links.append(link.attrs['href'])

            return movie_links

        except AssertionError as error:
            print("Error when fetching links from page {}: '{}'".format(pageNumber, error))

    def getLinksToReviewsFromMoviePage(self, moviePage):
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

# lf = LinksFetcher()
# print(lf.getLinksToMoviesFromSearchPages(1, 2))
# print(lf.getLinksToReviewsFromMoviePage("/film/Witaj+w+klubie-2013-657859"))
