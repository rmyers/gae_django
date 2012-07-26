from django.contrib.admin.views.main import ChangeList, ALL_VAR, ORDER_VAR,\
    ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, TO_FIELD_VAR

from filterspecs import FilterSpec
from paginator import Paginator
import logging
from google.appengine.ext import ndb

class GAEChangeList(ChangeList):
    
    def get_results(self, request):
        paginator = Paginator(self.query_set, self.list_per_page)
        # Get the number of objects, with admin filters applied.
        result_count = paginator.count

        # Get the total number of objects, with no admin filters applied.
        # Perform a slight optimization: Check to see whether any filters were
        # given. If not, use paginator.hits to calculate the number of objects,
        # because we've already done paginator.hits and the value is cached.
        if not self.query_set._filtered:
            full_result_count = result_count
        else:
            full_result_count = self.root_query_set.count()

        can_show_all = result_count <= 1000
        multi_page = result_count > self.list_per_page

        # Get the list of objects to display on this page.
        if (self.show_all and can_show_all) or not multi_page:
            result_list = self.query_set.fetch(1000)
        else:
            try:
                result_list = paginator.page(self.page_num+1).object_list
            except:
                raise

        self.result_count = result_count
        self.full_result_count = full_result_count
        self.result_list = result_list
        self.can_show_all = can_show_all
        self.multi_page = multi_page
        self.paginator = paginator

    
    def get_query_set(self):
        qs = self.root_query_set
        qs._filtered = False
        # Switch django filter strings into appengine ones 
        gaefilters = {
            'exact': '=',
            'iexact': '=',
            'isnull': '!=',
            'bool': '=',
            # TODO: more
        }
        lookup_params = self.params.copy() # a dictionary of the query string
        for i in (ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, TO_FIELD_VAR):
            if i in lookup_params:
                del lookup_params[i]
        for key, value in lookup_params.items():
            if not isinstance(key, str):
                # 'key' will be used as a keyword argument later, so Python
                # requires it to be a string.
                del lookup_params[key]
                lookup_params[str(key)] = value
            
            field, lookup = key.split('__')
            new_filter = '%s %s' % (field, gaefilters.get(lookup, '='))
            if lookup == 'bool':
                value = bool(int(value))
            qs.filter(new_filter, value)
            qs._filtered = True
        
        if self.search_fields and self.query:
            logging.error(self.query)
        
        if self.order_field:
            qs.order('%s%s' % ((self.order_type == 'desc' and '-' or ''), self.order_field))
        
        return qs
    
    def url_for_result(self, result):
        return "%s/" % result.key()

    def get_filters(self, request):
        filter_specs = []
        if self.list_filter:
            for filter_name in self.list_filter:
                field = self.model.fields().get(filter_name)
                spec = FilterSpec.create(field, request, self.params,
                                         self.model, self.model_admin,
                                         field_path=filter_name)
                if spec and spec.has_output():
                    filter_specs.append(spec)
        return filter_specs, bool(filter_specs)

class NDBChangeList(GAEChangeList):
    
    def get_filters(self, request):
        filter_specs = []
        if self.list_filter:
            for filter_name in self.list_filter:
                field = self.model._properties.get(filter_name)
                spec = FilterSpec.create(field, request, self.params,
                                         self.model, self.model_admin,
                                         field_path=filter_name)
                if spec and spec.has_output():
                    filter_specs.append(spec)
        return filter_specs, bool(filter_specs)
    
    def url_for_result(self, result):
        return "%s/" % result.key.urlsafe()
    
    def get_query_set(self):
        qs = self.root_query_set
        qs._filtered = False
        lookup_params = self.params.copy() # a dictionary of the query string
        for i in (ALL_VAR, ORDER_VAR, ORDER_TYPE_VAR, SEARCH_VAR, IS_POPUP_VAR, TO_FIELD_VAR):
            if i in lookup_params:
                del lookup_params[i]
        for key, value in lookup_params.items():
            if not isinstance(key, str):
                # 'key' will be used as a keyword argument later, so Python
                # requires it to be a string.
                del lookup_params[key]
                lookup_params[str(key)] = value
            
            _field, lookup = key.split('__')
            field = getattr(self.model, _field)
            if lookup == 'bool':
                qs = qs.filter(field == bool(int(value)))
            elif lookup in ['iexact', 'exact']:
                qs = qs.filter(field == value)
            # TODO: more
            qs._filtered = True
        
        
        if self.search_fields and self.query:
            if len(self.search_fields) == 1:
                # simple case just do a filter
                field = getattr(self.model, self.search_fields[0])
                qs = qs.filter(field == self.query)
                qs._filtered = True
            else:
                fields = [getattr(self.model, f) for f in self.search_fields]
                queries = [ndb.AND(field == self.query) for field in fields]
                qs = qs.filter(ndb.OR(*queries))
                qs._filtered = True
                    
        if self.order_field:
            filtered = qs._filtered
            field = getattr(self.model, self.order_field)
            if self.order_type == 'desc':
                qs = qs.order(-field)
            else:
                qs = qs.order(field)
            qs._filtered = filtered
        
        return qs