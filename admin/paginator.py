
from django.core.paginator import Paginator, Page

class Paginator(Paginator):
    """
    Paginator which is designed to work with appengine limit and offset
    instead of list slices.
    """

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        return Page(self.object_list.fetch(limit=self.per_page, offset=bottom), number, self)
