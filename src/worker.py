import config

from filmweb.links import LinksFetcher
from filmweb.reviews import ReviewsFetcher
from pymongo import MongoClient
from pymongo import InsertOne
from pymongo.errors import BulkWriteError

class MongoWorker:
    def __init__(self):
        self.client = MongoClient(config.mongo_string)
        self.filmweb_db = self.client.filmweb
        self.users_db = self.client.users
        self.users_series_db = self.client.series
        self.linksFetcher = LinksFetcher()
        self.reviewsFetcher = ReviewsFetcher()

    def storeLinksAndReviewsByUsersFromAjax(self, start, limit):
        """Convenience method"""
        links = self.getNewLinks(self.linksFetcher.getUserReviewLinksFromAjaxPages(start, limit), self.users_db.links)

        self.storeLinksAndReviews(links, self.users_db.rated, self.users_db.not_rated, self.users_db.links, self.users_db.invalid_links)

    def getNewLinks(self, links, collection):
        """Returns a list of not downloaded links from a given links list and a collection"""
        # links = self.linksFetcher.getReviewLinksFromPages(fromPage, toPage)

        downloaded_links = collection.find()

        for downloaded_link in downloaded_links:
            if downloaded_link['link'] in links:
                links.remove(downloaded_link['link'])

        return links

    def storeLinksAndReviewOfShowsByUsers(self, start, limit):
        """Convenience method"""
        show_pages = self.linksFetcher.getLinksToMoviesFromSearchPages(start, limit, "https://www.filmweb.pl/serials/search?orderBy=popularity&descending=true&page=")

        review_links = []
        for page in show_pages:
            review_links.extend(self.linksFetcher.getLinksToReviewsFromMoviePage(page))

        links = self.getNewLinks(review_links, self.users_series_db.links)

        self.storeLinksAndReviews(links, self.users_series_db.rated, self.users_series_db.not_rated, self.users_series_db.links, self.users_series_db.invalid_links)

    def storeLinksAndReviewsByUsers(self, start, limit):
        """Convenience method"""
        movie_pages = self.linksFetcher.getLinksToMoviesFromSearchPages(start, limit, "https://www.filmweb.pl/films/search?orderBy=popularity&descending=true&page=")
        review_links = []

        for page in movie_pages:
            review_links.extend(self.linksFetcher.getLinksToReviewsFromMoviePage(page))

        links = self.getNewLinks(review_links, self.users_db.links)

        self.storeLinksAndReviews(links, self.users_db.rated, self.users_db.not_rated, self.users_db.links, self.users_db.invalid_links)

    def storeLinksAndReviewsByFilmweb(self, start, limit):
        """Convenience method"""
        links = self.getNewLinks(self.linksFetcher.getReviewLinksFromPages(start, limit), self.filmweb_db.links)

        self.storeLinksAndReviews(links, self.filmweb_db.rated, self.filmweb_db.not_rated, self.filmweb_db.links, self.filmweb_db.invalid_links)

    def storeLinksAndReviews(self, links, targetRated, targetNotRated, targetValidLinks, targetInvalidLinks):
        """Downloads reviews from given links and stores them in database. Also stores valid and invalid links in appropriate collections."""
        count, invalid, total = 1, 1, len(links)
        rated, not_rated, valid_links, invalid_links = [], [], [], []

        # Download reviews
        for link in links:   
            review = self.reviewsFetcher.getReview(link)
            
            if review:
                valid_links.append(link)
                print("Downloaded review from '{}' ({}/{})...".format(link, count, total))         

                if review['rating']:
                    rated.append(review)
                else:
                    del review['rating']
                    not_rated.append(review)
            else:
                invalid_links.append(link)
                print("Couldn't download review from '{}', invalid links {}/{} total".format(link, invalid, total))
                invalid += 1

            count += 1

        # Prepare upload
        bulk_rated, bulk_not_rated, bulk_downloaded, bulk_not_downloaded = self.createDocumentsFromReviews(rated), self.createDocumentsFromReviews(not_rated), self.createDocumentsFromLinks(valid_links), self.createDocumentsFromLinks(invalid_links)

        print("Uploading {} rated reviews, {} not rated reviews, {} valid links, {} invalid links...".format(len(bulk_rated), len(bulk_not_rated), len(bulk_downloaded), len(bulk_not_downloaded)))

        try:
            if bulk_rated:
                targetRated.bulk_write(bulk_rated)
            if bulk_not_rated:
                targetNotRated.bulk_write(bulk_not_rated)
            if bulk_not_downloaded:
                targetInvalidLinks.bulk_write(bulk_not_downloaded)
            if bulk_downloaded:
                targetValidLinks.bulk_write(bulk_downloaded)

        except BulkWriteError as bwe:
            print(bwe.details)
            print(bwe)
        except Exception as e:
            print(e)

    def storeLinksAndUserReviews(self):
        """Downloads reviews from given links and stores them in database. Also stores valid and invalid links in appropriate collections."""

    def getRatedReviews(self):
        """Downloads all the rated reviews from database"""
        reviews = list(self.filmweb_db.rated.find())
        reviews.extend(list(self.users_db.rated.find()))
        return reviews

    def getUnratedReviews(self):
        """Downloads all the unrated reviews from the database"""
        reviews = list(self.filmweb_db.not_rated.find())
        reviews.extend(list(self.users_db.not_rated.find()))
        return reviews

    def createDocumentsFromReviews(self, reviews):
        bulk_documents = []
        for review in reviews:
            doc = InsertOne(review)
            bulk_documents.append(doc)
        
        return bulk_documents

    def createDocumentsFromLinks(self, links):
        bulk_documents = []
        for link in links:
            doc = InsertOne({"link": link})
            bulk_documents.append(doc)
        
        return bulk_documents

# worker = MongoWorker()
# worker.storeLinksAndReviewsByUsers(1, 1001)
# worker.storeLinksAndReviewOfShowsByUsers(1, 1001)
# worker.storeLinksAndReviewsByFilmweb(1, 10)

# worker.storeLinksAndReviewsByUsersFromAjax(1, 708)