"""
A useful set of tools for your gae application.

Just add a file 'fabfile.py' to your application root, install
fabric of course::

    from gae_django.fabric_commands import *
    
Available commands::

    deploy        Deploy an application::
    local_shell   Open a local shell for this application
    remote_shell  Open a remote shell for this application

"""


import sys
import os

from fabric.api import env, task, local

def setup_paths():
    """Setup sys.path with everything we need to run."""
    import google
    
    DIR_PATH = os.path.abspath(os.path.dirname(os.path.dirname(google.__file__)))
    
    EXTRA_PATHS = [
      os.getcwd(),
      DIR_PATH,
      os.path.join(DIR_PATH, 'lib', 'antlr3'),
      os.path.join(DIR_PATH, 'lib', 'django_1_3'),
      os.path.join(DIR_PATH, 'lib', 'fancy_urllib'),
      os.path.join(DIR_PATH, 'lib', 'ipaddr'),
      os.path.join(DIR_PATH, 'lib', 'jinja2'),
      os.path.join(DIR_PATH, 'lib', 'protorpc'),
      os.path.join(DIR_PATH, 'lib', 'markupsafe'),
      os.path.join(DIR_PATH, 'lib', 'webob_0_9'),
      os.path.join(DIR_PATH, 'lib', 'webapp2'),
      os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
      os.path.join(DIR_PATH, 'lib', 'simplejson'),
      os.path.join(DIR_PATH, 'lib', 'google.appengine._internal.graphy'),
    ]
    
    sys.path = EXTRA_PATHS + sys.path

def read_app_config():
    """Load the app.yaml file and add some things to env."""
    setup_paths()
    from google.appengine.tools.dev_appserver import ReadAppConfig
    appinfo = ReadAppConfig('app.yaml')
    return appinfo

@task
def deploy(version='', appid='.'):
    """
    Deploy an application::
    
        Standard Deploy
        $ fab deploy
        
        Deploy a different version than in the app.yaml
        $ fab deploy:version=fabulous
        
        Deploy to a different appid
        $ fab deploy:appid=someotherapp
    """
    yaml_file = os.path.join(appid, 'app.yaml')
    assert os.path.isfile(yaml_file), "Could not find app.yaml file"
    version_str = '-V %s' % version if version else ''
    cmd = 'appcfg.py update %s %s' % (version_str, appid)
    local(cmd)

def prep_shell(prefix, appid=None, server=None):
    """Setup the remote shell for either remote or local.
    
    * prefix: either 's~' or 'dev~' 
    * appid: Use a different application id
    * server: Point to a different server
    """

    appinfo = read_app_config()
    # TODO: assert 'remote_api' in appinfo.builtins
    
    if hasattr(appinfo, 'env_variables'):
        os.environ.update(appinfo.env_variables)
    
    if appid is not None:
        appinfo.application = appid
    
    if server is None:
        server = '%s.appspot.com' % appinfo.application
        
    application = '%s%s' % (prefix, appinfo.application)
    
    return application, server

@task
def remote_shell(appid=None, server=None):
    """
    Open a remote shell for this application
    
    The builtin 'remote_api' must be set to 'on' in your app.yaml file.
    
        $ fab remote_shell
        
        Use a different application id:
        $ fab remote_shell:different-id
        
        Point to a different server
        $ fab remote_shell:server=other-app.appspot.com
    """
    
    application, server = prep_shell('s~', appid, server)
    
    from google.appengine.tools import remote_api_shell
    from google.appengine.tools import appengine_rpc
    
    remote_api_shell.remote_api_shell(server, application, 
        remote_api_shell.DEFAULT_PATH, True, appengine_rpc.HttpRpcServer)

@task
def local_shell(appid=None, server=None):
    """
    Open a local shell for this application
    
    The builtin 'remote_api' must be set to 'on' in your app.yaml file.
    The default will use the remote api against your local dev server,
    which is at 'localhost:8080'
    
        $ fab local_shell
        
        Use a different application id:
        $ fab local_shell:different-id
        
        Point to a different server
        $ fab local_shell:server=localhost:8081
    """
    server = server or 'localhost:8080'
    
    application, server = prep_shell('dev~', appid, server)
    
    from google.appengine.tools import remote_api_shell
    from google.appengine.tools import appengine_rpc
    
    remote_api_shell.remote_api_shell(server, application, 
        remote_api_shell.DEFAULT_PATH, False, appengine_rpc.HttpRpcServer)