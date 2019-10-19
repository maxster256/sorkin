from links import LinksFetcher
from reviews import ReviewsFetcher

lf = LinksFetcher()
rf = ReviewsFetcher()
# reviews = lf.get_review_links_from_pages(lf.get_review_links_from_page, 1, 5)

review = rf.get_review('https://paradoks.net.pl/read/38856-joker-recenzja-trzecia')
print(review)