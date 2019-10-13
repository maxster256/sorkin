import requests
import bs4
from bs4 import BeautifulSoup

class ReviewsFetcher:
    def __init__(self):
        self.domain = "https://filmweb.pl"

    def split_reviews(self, reviews):
        """
        Returns lists of rated and not rated reviews from a list of parsed reviews from Filmweb.
        :param reviews: list of parsed reviews from Filmweb
        :return: 'rated' and 'not_rated' reviews lists
        """
        rated, not_rated = [], []
        for review in reviews:
            if review['rating']:
                rated.append(review)
            else:
                del review['rating']
                not_rated.append(review)

        return rated, not_rated

    def get_reviews(self, links):
        """
        Returns a list of reviews from a given list of links to Filmweb review pages.
        :param links: List of relative links to reviews on Filmweb
        :return: List of dictionaries with 'title' of review, 'author' of review, 'movie' that's been reviewed,
        'rating' given by the reviewer, 'date' of review, 'helpful' rate given by readers and actual 'review'
        """
        reviews, count = [], 0

        for link in links:
            review = self.get_review(link)
            if review:
                reviews.append(review)

        return reviews

    def get_review(self, link):
        """
        Returns a dictionary of review details parsed from a given link to a Filmweb review page.
        :param link: Relative link to a review on Filmweb
        :return: Dictionary with 'title' of review, 'author' of review, 'movie' that's been reviewed,
        'rating' given by the reviewer, 'date' of review, 'helpful' rate given by readers and actual 'review'
        """
        r = requests.get(self.domain + link, headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"})
        soup = BeautifulSoup(r.text, 'html.parser')

        try:
            movie_title = soup.find("h1", class_="s-16 bottom-15").find("a").string
            review_title = soup.find("h2", class_="inline", attrs={"itemprop": "name"}).string
            author_name = soup.find("div", class_="boxContainer va-top small-margin").find("div", class_="top-5", attrs={"itemprop": "author"}).string

            review_date = soup.find("div", class_="forceCap").find("span")
            if review_date:
                review_date = review_date.attrs["title"]

            review_content = soup.find("div", class_="pageBox reviewPage").find(attrs={"itemprop": "reviewBody"})
            internal_divs = review_content.find_all("div")
            
            for div in internal_divs:
                div.decompose()

            review = review_content.text.replace("  ", "\n")
            author_rating_details = soup.find("div", class_="pageBox", attrs={"itemprop": "reviewRating"})
            author_rating = None

            if author_rating_details:
                author_rating = author_rating_details.find(attrs={"itemprop": "ratingValue"}).string

            helpful_rate_container = soup.find(class_="reviewRatingPercent")
            helpful_rate = None

            if helpful_rate_container:
                helpful_rate = helpful_rate_container.text

            return {"title": review_title, "author": author_name, "movie": movie_title, "rating": author_rating, "date": review_date, "helpful": helpful_rate, "review": review}
        
        except AssertionError as error:
            print("Error when fetching review {}: '{}'".format(link, error))
        except Exception as e:
            print(e)