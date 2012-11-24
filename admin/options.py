
from gettext import gettext as _

from google.appengine.ext import db, ndb
from google.appengine.ext.deferred.deferred import defer

import djangoforms
from .changelist import GAEChangeList, NDBChangeList
from .utils import decorate_model, decorate_ndb_model

from django.contrib.admin import ModelAdmin as DjangoModelAdmin
from django.utils.safestring import mark_safe
from django import template
from django.shortcuts import render_to_response
from django.http import Http404
import logging
from google.appengine.api import datastore


class ModelAdmin(DjangoModelAdmin):
    """Default class for instances of google.appengine.ext.db.Model"""
    
    form = None
    change_form_template = 'admin/gae_change_form.html'
    
    def __init__(self, model, admin_site):
        # add meta class and various attributes/methods for django
        model = decorate_model(model)
        super(ModelAdmin, self).__init__(model, admin_site)
    
    def queryset(self, request):
        return self.model.all()
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return GAEChangeList
    
    def get_object(self, request, object_id):
        """
        Returns an instance matching the primary key provided. ``None``  is
        returned if no match is found (or the object_id failed validation
        against the primary key field).
        """
        return db.get(object_id)
    
    def save_model(self, request, obj, form, change):
        from django.db.transaction import set_dirty
        obj.put()
        set_dirty()
    
    def delete_model(self, request, obj):
        from django.db.transaction import set_dirty
        obj.delete()
        set_dirty()
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.form:
            return self.form
        
        if self.declared_fieldsets:
            from django.contrib.admin.util import flatten_fieldsets
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(kwargs.get("exclude", []))
        exclude.extend(self.get_readonly_fields(request, obj))
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        defaults = {
            "fields": fields,
            "exclude": exclude or None,
            "model": self.model,
        }
        defaults.update(kwargs)
        
        def ignore(*args, **kwargs):
            """Make this function a no-op."""
            pass
        
        meta = type('Meta', (), defaults)
        name = '%sForm' % self.model.__name__
        bases = (djangoforms.ModelForm,)
        attrs = { "Meta": meta, 'save_m2m': ignore }
        return type(name, bases, attrs)
    
    def get_formset(self, request, obj=None, **kwargs):
        # TODO: add formset support for child objects?
        return []

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # Need to override this because of content types lookup and absolute_url crap
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        absurl = None
        if obj and hasattr(self.model, 'get_absolute_url'):
            absurl = obj.get_absolute_url()
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': absurl,
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            # STUPID CONTENT TYPES!!!
            'content_type_id': opts.object_name.lower(),
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': getattr(self.admin_site, 'root_path', '/'),
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, context_instance=context_instance)
    
    def history_view(self, request, object_id, extra_context=None):
        "The 'history' admin view for this model."
        from .models import LogEntry
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        parent = datastore.Key(object_id)
        action_list = LogEntry.all().ancestor(parent).order('-action_time').fetch(100)
        # If no history was found, see whether this object even exists.
        obj = self.get_object(request, object_id)
        if obj is None:
            raise Http404
        
        context = {
            'title': _('Change history: %s') % obj,
            'action_list': action_list,
            'module_name': opts.verbose_name_plural,
            'object': obj,
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.object_name.lower()),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context, context_instance=context_instance)
    
    def log_addition(self, request, obj):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from .tasks import create_log
        from django.contrib.admin.models import ADDITION
        defer(create_log, 
              user_id = request.user.id,
              user_name = unicode(request.user),
              content_type = obj._meta.verbose_name,
              app_label = obj._meta.app_label,
              object_id = obj.pk,
              object_repr = unicode(obj),
              action_flag = ADDITION
        )
        

    def log_change(self, request, obj, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from .tasks import create_log
        from django.contrib.admin.models import CHANGE
        defer(create_log, 
              user_id = request.user.id,
              user_name = unicode(request.user),
              content_type = obj._meta.verbose_name,
              app_label = obj._meta.app_label,
              object_id = obj.pk,
              object_repr = unicode(obj),
              action_flag = CHANGE,
              change_message = message
        )

    def log_deletion(self, request, obj, object_repr):
        """
        Log that an object will be deleted. Note that this method is called
        before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from .tasks import create_deletion_log
        defer(create_deletion_log, 
              user_id = request.user.id,
              user_name = unicode(request.user),
              content_type = obj._meta.verbose_name,
              object_id = obj.pk,
              object_repr = object_repr
        )

class NDBModelAdmin(ModelAdmin):
    
    def __init__(self, model, admin_site):
        # add meta class and various attributes/methods for django
        model = decorate_ndb_model(model)
        super(ModelAdmin, self).__init__(model, admin_site)
    
    def queryset(self, request):
        return self.model.query()
    
    def get_object(self, request, object_id):
        """
        Returns an instance matching the primary key provided. ``None``  is
        returned if no match is found (or the object_id failed validation
        against the primary key field).
        """
        key = ndb.Key(urlsafe=object_id)
        return key.get()
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return NDBChangeList