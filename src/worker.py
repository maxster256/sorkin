import config

from filmweb.links import LinksFetcher
from filmweb.reviews import ReviewsFetcher
from pymongo import MongoClient

class MongoWorker:
    def __init__(self):
        self.client = MongoClient(config.mongo_string)
        self.linksFetcher = LinksFetcher()
        self.reviewsFetcher = ReviewsFetcher()

        self.filmweb_db = self.client.filmweb
        self.users_db = self.client.users
        self.users_series_db = self.client.series

    def store_reviews_by_users_from_ajax(self, start, limit):
        """
        Stores reviews fetched from Filmweb's AJAX carousel on '/reviews' page in MongoDB database.
        :param start: index of the AJAX carousel page to start parsing from
        :param limit: index of the AJAX carousel page to end parsing at
        :return:
        """
        links = self.get_new_links_from_list(self.linksFetcher.get_review_links_from_pages(
            self.linksFetcher.getUserReviewLinksFromAjaxPage, start, limit), self.users_db.links)

        self.store_reviews(links, self.users_db.rated, self.users_db.not_rated, self.users_db.links)

    def store_reviews_by_users(self, start, limit):
        """
        Stores user reviews fetched from Filmweb's movie pages in MongoDB database.
        :param start: index of the search page to start parsing from
        :param limit: index of the search page to end parsing at
        :return:
        """
        links = self.get_new_links_from_list(self.linksFetcher.get_links_to_user_movie_reviews_from_search_pages(start, limit), self.users_db.links)

        self.store_reviews(links, self.users_db.rated, self.users_db.not_rated, self.users_db.links)

    def store_reviews_by_filmweb(self, start, limit):
        """
        Stores Filmweb staff's reviews fetched from '/reviews' page in MongoDB database.
        :param start: index of the reviews page to start parsing from
        :param limit: index of the reviews page to end parsing at
        :return:
        """
        links = self.get_new_links_from_list(self.linksFetcher.get_review_links_from_pages(
            self.linksFetcher.get_staff_review_links_from_page, start, limit), self.filmweb_db.links)

        self.store_reviews(links, self.filmweb_db.rated, self.filmweb_db.not_rated, self.filmweb_db.links)

    def store_reviews(self, links, target_rated, target_not_rated, target_valid_links):
        """
        Downloads reviews from given list of links to Filmweb review pages, splits them into 'rated' and 'not_rated',
        creates lists of MongoDB document insertion operations and performs these operations for given target
        collections.
        :param links: list of links to Filmweb review pages
        :param target_rated: target MongoDB collection storing rated reviews from Filmweb
        :param targetNotRated: target MongoDB collection storing not rated reviews from Filmweb
        :param targetValidLinks: target MongoDb collection storing links for which the reviews were downloaded
        :return:
        """
        reviews = self.reviewsFetcher.get_reviews(links)
        rated, not_rated = self.reviewsFetcher.split_reviews(reviews)
        link_docs = [{'link': l} for l in links]

        print("Uploading {} rated reviews, {} not rated reviews, {} links...".format(len(rated),
                                                                                     len(not_rated), len(link_docs)))
        try:
            if rated:
                target_rated.insert_many(rated)
            if not_rated:
                target_not_rated.insert_many(not_rated)
            if link_docs:
                target_valid_links.insert_many(link_docs)
        except Exception as e:
            print(e)

    def get_new_links_from_list(self, links, collection):
        """
        Returns a set of links to reviews that have not been already uploaded to the MongoDB database.
        :param links: list of fetched links to reviews on Filmweb
        :param collection: MongoDB collection storing links to check for duplicates
        :return: set of unique, new links to reviews on Filmweb
        """
        downloaded_links = collection.find()

        for downloaded_link in downloaded_links:
            if downloaded_link['link'] in links:
                links.remove(downloaded_link['link'])

        return links

    def get_rated_reviews(self):
        """
        Returns a list of all rated reviews stored in database.
        :return: list of reviews
        """
        return list(self.filmweb_db.rated.find()).extend(list(self.users_db.rated.find()))

    def get_not_rated_reviews(self):
        """
        Returns a list of all rated reviews stored in database.
        :return: list of reviews
        """
        return list(self.filmweb_db.not_rated.find()).extend(list(self.users_db.not_rated.find()))


