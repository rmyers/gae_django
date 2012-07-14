"""
Admin Utils
"""
import re

from django.db.models.options import Options

class PK:
    attname = 'id'

class DefaultMeta:
    db_table = 'google_datastore'
    ordering = 'DO_NOT_USE'


def decorate_model(model):
    """
    Add attributes and methods to a google db Model instance
    to allow functions in the django admin to work as expected.
    """
    
    # Grab the app_label from the models module path
    # myproject.myapp.models.MyModel => 'myapp'
    app_label = re.sub('\.models$', '', model.__module__).split('.')[-1]
    
    if not hasattr(model, 'Meta'):
        setattr(model, 'Meta', DefaultMeta)
        
    opts = Options(model.Meta, app_label)
    opts.pk = PK
    opts.contribute_to_class(model, 'NAME_DOES_NOT_APPEAR_TO_BE_USED')
    # Add some methods that Django uses
    model.serializable_value = lambda m, attr: getattr(m, attr)
    model._deferred = False
    model._get_pk_val = lambda m: str(m.key())
    model._get_id = lambda m: m.key().id()
    model.id = property(model._get_id)
    model.pk = property(model._get_pk_val)
    return model

def decorate_ndb_model(model):
    """
    Add attributes and methods to a google db Model instance
    to allow functions in the django admin to work as expected.
    """
    
    # Grab the app_label from the models module path
    # myproject.myapp.models.MyModel => 'myapp'
    app_label = re.sub('\.models$', '', model.__module__).split('.')[-1]
    
    if not hasattr(model, 'Meta'):
        setattr(model, 'Meta', DefaultMeta)
        
    opts = Options(model.Meta, app_label)
    opts.pk = PK
    opts.contribute_to_class(model, 'NAME_DOES_NOT_APPEAR_TO_BE_USED')
    # Add some methods that Django uses
    model.serializable_value = lambda m, attr: getattr(m, attr)
    model._deferred = False
    model._get_pk_val = lambda m: str(m.key)
    model._get_id = lambda m: m.key.id()
    model.id = property(model._get_id)
    model.pk = property(model._get_pk_val)
    return model