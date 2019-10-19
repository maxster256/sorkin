from links import LinksFetcher
from reviews import ReviewsFetcher

lf = LinksFetcher()
rf = ReviewsFetcher()
# reviews = lf.get_review_links_from_pages(lf.get_review_links_from_page, 1, 5)

review = rf.get_review('http://blogfilmowy24.blogspot.com/2019/10/recenzja-nieznajomi.html')
print(review)