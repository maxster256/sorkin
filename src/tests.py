from links import LinksFetcher
from reviews import ReviewsFetcher

lf = LinksFetcher()
links = lf.get_review_links_from_pages(1, 2)

rf = ReviewsFetcher()

grades, no_grades = rf.getCategorizedReviews(links)

print(grades)
print(no_grades)

review = rf.getReview("/review/Widz+w+rozpaczy-624")
print(review)

