from django.contrib.admin import AdminSite

from options import ModelAdmin
from django.shortcuts import redirect
from django.conf import settings

class GAEAdminSite(AdminSite):
    
    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Registers the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelAdmin (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.

        If a model is abstract, this will raise ImproperlyConfigured.
        """
        if not admin_class:
            admin_class = ModelAdmin

        if not isinstance(model_or_iterable, (list, tuple)):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:

            if model in self._registry:
                raise AttributeError('The model %s is already registered' % model.__name__)

            # If we got **options then dynamically construct a subclass of
            # admin_class with those **options.
            if options:
                # For reasons I don't quite understand, without a __module__
                # the created class appears to "live" in the wrong place,
                # which causes issues later on.
                options['__module__'] = __name__
                admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

            # Instantiate the admin class to save in the registry
            self._registry[model] = admin_class(model, self)

    def unregister(self, model_or_iterable):
        """
        Unregisters the given model(s).

        If a model isn't already registered, this will raise NotRegistered.
        """
        if not isinstance(model_or_iterable, (list, tuple)):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise AttributeError('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def login(self, request):
        return redirect(settings.LOGIN_URL)

site = GAEAdminSite()