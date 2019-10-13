from worker import MongoWorker

def main():
    worker = MongoWorker()
    worker.store_reviews_by_filmweb(1, 6)


if __name__ == '__main__':
    main()