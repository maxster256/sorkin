import requests, bs4, multiprocessing
from joblib import Parallel, delayed

from bs4 import BeautifulSoup
from selenium import webdriver

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
        reviews = Parallel(n_jobs=multiprocessing.cpu_count())(delayed(self.get_review(link) for link in links))
        return reviews

    def get_review(self, link):
        """
        Returns a dictionary of review details parsed from a given link to a Film.org.pl review page.
        :param link: Relative link to a review on Film.org.pl
        :return: Dictionary with 'title' of review, 'author' of review, 'movie' that's been reviewed,
        'rating' given by the reviewer, 'date' of review, 'helpful' rate given by readers and actual 'review'
        """
        try:
            print("Downloading review from {}...".format(link))
            driver = webdriver.Chrome('/users/pawel/chromedriver')
            driver.implicitly_wait(10)
            driver.get(link)

            title_source = driver.find_element_by_class_name('title')
            content_source = driver.find_element_by_class_name('article-content')

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            title = soup.find(class_='title entry-title').find('a').text.replace('\n', '')

            content_grade = soup.find(class_='article-content entry-content').text.replace('\xa0', '\n').split(
                '\n\nocena ')

            content = content_grade[0]

            if content_grade[1]:
                grade = content_grade[1].split('/')[0]

            return {'title': title, 'author': 'Marcin Stasiowski', 'content': content, 'rating': grade}

        except Exception as error:
            print("Error when fetching review {}: '{}'".format(link, error))
            return None
