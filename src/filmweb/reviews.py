import requests
import bs4
from bs4 import BeautifulSoup

class ReviewsFetcher:
    def __init__(self):
        self.domain = "https://filmweb.pl"

    def getReview(self, link):
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
            

# rf = ReviewsFetcher()
# print(rf.getReview("/review/Sex%2C+drugs+i+zwyczajne+%C5%BCycie-182"))