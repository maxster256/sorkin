import requests
import bs4
from bs4 import BeautifulSoup


class ReviewsFetcher:
    def __init__(self):
        pass

    def split_reviews(self, reviews):
        """
        Returns lists of rated and not rated reviews from a list of parsed reviews from Film.org.pl.
        :param reviews: list of parsed reviews from Film.org.pl
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
        Returns a list of reviews from a given list of links to Film.org.pl review pages.
        :param links: List of relative links to reviews on Film.org.pl
        :return: List of dictionaries with 'title' of review, 'author' of review, 'movie' that's been reviewed,
        'rating' given by the reviewer, 'date' of review, 'helpful' rate given by readers and actual 'review'
        """
        reviews, count = [], 0

        print(links)

        for link in links:

            print("Downloading review from {}...".format(link))
            review = self.get_review(link)
            if review:
                reviews.append(review)

        return reviews

    def get_review(self, link):
        """
        Returns a dictionary of review details parsed from a given link to a Film.org.pl review page.
        :param link: Relative link to a review on Film.org.pl
        :return: Dictionary with 'title' of review, 'author' of review, 'movie' that's been reviewed,
        'rating' given by the reviewer, 'date' of review, 'helpful' rate given by readers and actual 'review'
        """
        try:
            r = requests.get(link + '?m=1', headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1"})
            soup = BeautifulSoup(r.text, 'html.parser')
            children = []

            print(soup.find(class_="article-content entry-content"))

            # review_title = soup.find(class_='single-header-content').find('h1').text
            # author_name = soup.find(class_='author pull-left').find('span').text
            # content = soup.find('article').findAll('p')
            #
            # for child in content:
            #     if not child.find('h3') and child.text:
            #         children.append(child.text.replace('\xa0', ' '))
            #
            # grade = soup.find(class_='review-score').findAll(class_='positive-state state')
            # return {'title': review_title, 'author': author_name, 'content': '\n'.join(children), 'rating': len(grade)}

        except Exception as error:
            print("Error when fetching review {}: '{}'".format(link, error))
            return None
