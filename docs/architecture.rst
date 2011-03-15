Akhet Architecture
%%%%%%%%%%%%%%%%%%%%%%%

Introduction
============

Here we'll go through the code in an Akhet application, explaining what each
part is and how it differs from Pylons. Some features come from Pyramid and are
common to Pyramid's built-in application templates, while others features are
added by Akhet. We'll try to specify which features come from where.

The sample application here is named "Zzz", and the top-level Python package
within it is "zzz". So wherever it says Zzz or zzz below, it means your actual
application name or package name.

Paster
======

As in Pylons, the "paster" command creates and runs applications.

paster create
-------------

**paster create** works the same in both Pylons and Pyramid:

.. code-block:: sh

    $ paster create -t akhet Zzz

This is how you create a new application. Our sample application is named
"Zzz". It will ask whether to preconfigure SQLAlchemy in the application; the
default is true. Answer 'n' to skip SQLAlchemy. You can also pass the answer on
the command line:

.. code-block:: sh

    $ paster create -t akhet Zzz sqlalchemy=n

(The SQLAlchemy question is specific to the 'akhet' template. Other
application templates may have other questions or no questions.)

The **application name** must be a valid Python identifier. I.e., it must start
with a letter or underscore; and may contain only letters, numbers, and
underscore. "paster create" will automatically generate the Python **package
name** by lowercasing the application name. 

You can't use an application name that's identical to a module in the Python
standard library.  Paster will create it but Python won't be able to run it. So
don't name your application "Test".

paster serve
------------

**paster serve** also works the same:

.. code-block:: sh

    $ paster serve development.ini
    $ paster serve --reload development.ini

This runs the application under PasteHTTPServer or another server specified in
the INI file. Running it under Apache or another Python webserver works the
same way as in Pylons; see the Pyramid manual for details.

paster proutes
--------------

**paster proutes** prints the current route definitions. You have to specify
both the INI file and the application section in the file, which for Akhet is
"zzz" regardless of the actual application name:

.. code-block:: sh

    $ paster proutes development.ini zzz

This replaces "paster routes" in Pylons.

Other paster commands
---------------------

**paster pshell** is covered in the "Shell" section below. It replaces "paster
shell" in Pylons.

"paster make-config" is not supported in Pyramid. Instead, all Pyramid
application templates include a production.ini. You can copy it to make other
INI files.

"paster setup-app" is not supported in Pyramid. Instead, Akhet includes a
*create_db* script. After you have defined your models, run it to create the
database tables. You can customize the script if you want to prepopulate the
dataabse with certain initial records:

.. code-block:: sh

    $ python -m zzz.scripts.create_db development.ini

You can also put other utility scripts in the "scripts" package and run them
the same way.

"paster controller" and "paster restcontroller" do not exist in Pyramid. You'll
have to create your handler modules by hand or copy an existing module.

INI files
=========

development.ini
---------------

*development.ini* is generally similar to Pylons but has some different sections
and options:

.. code-block:: ini

    [app:myapp]
    use = egg:Zzz
    reload_templates = true
    debug_authorization = false
    debug_notfound = false
    debug_routematch = false
    debug_templates = true
    default_locale_name = en
    mako.directories = zzz:templates
    sqlalchemy.url = sqlite:///%(here)s/db.sqlite
    session.type = file
    session.data_dir = %(here)s/data/sessions/data
    session.lock_dir = %(here)s/data/sessions/lock
    session.key = Zzz
    session.secret = 4b391beb818275e9aef4a58207782e5366e9c662

.. code-block:: ini

    [server:main]
    use = egg:Paste#http
    host = 127.0.0.1
    port = 5000

.. code-block:: ini

    [pipeline:main]
    pipeline =
        egg:WebError#evalerror
        myapp

..
    The sections are in different code blocks due to a limitation in Pygments'
    syntax highlighting. If a value spans multiple lines as the "pipeline"
    value does, Pygments will not colorize any of the block.

The first thing to notice is that the main section is "[pipeline:main]", not
"[app:main]". In Pylons middleware is configured in middleware.py, but in
Pyramid it's configured in the INI file. Pyramid does not require any
middleware at all; we're only using it here for error handling.  

The default development pipeline has two components:

1. WebError's EvalError, which produces the interactive traceback if
   there's an uncaught exception.

2. "zzz" is the application, defined in the "[app:myapp]" section.

The "[app:myapp]" section has a "use = egg:Zzz" setting, which tells Paste to
load the Pyramid application by its entry point. An entry point is a shortcut
alias to a callable. The other variables in this section are arguments to that
callable, passed using ``\*\*kwargs`` so that the names can contain ".". The
actual callable is the ``main()`` function in the next section. Entry points
are defined in the application's *setup.py*.  More information on entry points
is in the Setup or Distribute documentation.

The "myapp" in the section name is always "myapp". All other "Zzz"'s in this
article are the actual name of your application, and "myapp"'s are the
corresponding package name. (Akhet hardcodes the section name to "myapp" so that
command-line utilities can guess which section contains the application
settings without having to ask the user.  "paster pshell" asks the user anyway,
but we're working on that.) 

The "debug\_\*" settings turn on various debugging features which output to the
console. "reload_templates" causes Mako to check the modify time of each
template before rendering it, to notice any changes. (It also works with
Chameleon and some other template engines.)

"sqlalchemy.url" is your database URL, the same as in Pylons. The "session.\*"
variables are the same as in Pylons. "session.secret" is automatically set to a
random number when the application is created.

The "[server:main]" section is the same as in Pylons. It tells which WSGI
server to run. By default this is PasteHTTPServer, a multhtreaded HTTP server
written in Pylons. 

production.ini
--------------

*production.ini* has a different pipeline:

.. code-block:: ini

    [pipeline:main]
    pipeline =
        weberror
        myapp

Here the WebError middleware replaces EvalException. This is exactly what
Pylons does; it's just configured a different way. Pylons has a global 'debug'
setting that indirectly choses WebError when false, while Pyramid just lets you
configure the middleware directly.
WebError dumps exception tracebacks to the console or emails them the
admistrator. It's is configured in the "[filter:weberror]" section:

.. code-block:: ini

    [filter:weberror]
    use = egg:WebError#error_catcher
    debug = false
    ;error_log = 
    ;show_exceptions_in_wsgi_errors = true
    ;smtp_server = localhost
    ;error_email = janitor@example.com
    ;smtp_username = janitor
    ;smtp_password = "janitor's password"
    ;from_address = paste@localhost
    ;error_subject_prefix = "Pyramid Error"
    ;smtp_use_tls =
    ;error_message =

Again, these are the same settings as Pylons' production.ini, just in a
different format.  

.. important::

   **To avoid security risks when running in production, ensure that
   EvalException is NOT used, and that WebError's debug setting is false.**
   The default production.ini does this, but you should double-check it anyway. 

   EvalException is useful during development, but if the application is
   exposed to the Internet and a malicious user gets the interactive traceback,
   either by accidentally getting an exception or by forcing an exception, s/he
   would have a Python prompt directly into your application's process, and
   could modify files or variables.

   WebError's debug mode is less dangerous but it does show an exception's
   traceback to the user, which may reveal details of your application
   structure and server environment that could be leveraged in an attack.

The "error_message" variable allows you to customize the error message shown to
the user if an exception occurs. The default message is rather unsatisfactory::

    Server Error

    An error occurred. See the error logs for more information. (Turn debug on
    to display exception reports here) 

This is more of a message to you than a meaningful message to the user, so you
may want to change it. Whatever text you put in the 'error_message' variable
will replace the second paragraph of the message. If you have a multi-line
message, indent the subsequent lines so that ConfigParser knows they're
continuation lines.

In the application section of *production.ini*, all the "debug\_\*" variables
and "reload_templates" are false. This saves some CPU cycles as it's processing
requests. 

Logging
-------

The bottom half of both INI files contain several sections to configure
Python's logging system.  This is the same as in Pylons. 

We can't explain the entire logging syntax here, but these are the sections
most often customized by users:

.. code-block:: ini

    [logger_root]
    level = WARN
    handlers = console

    [logger_zzz]
    level = DEBUG
    handlers =
    qualname = zzz

    [logger_sqlalchemy]
    level = INFO
    handlers =
    qualname = sqlalchemy.engine
    # "level = INFO" logs SQL queries.
    # "level = DEBUG" logs SQL queries and results.
    # "level = WARN" logs neither.  (Recommended for production systems.)

These define a logger "root", "zzz" (the application's package name), and
"sqlalchemy.engine" (specified in the qualname). Each has a 'level' variable
which can be DEBUG, INFO, WARN, ERROR, or CRITICAL. Each level also logs the
levels on its right, so WARN logs warnings and errors. Logger names are in a
dotted hierarchy, so that "sqlalchemy.engine" affects all loggers below it
("sqlalchemy.engine.ENGINE1", etc).  "root" affects all loggers that aren't
otherwise specified.

Generally, DEBUG is debugging information, INFO is chatty success messages,
WARN means something might be wrong, ERROR means something is
definitely wrong, and CRITICAL means you'd better fix it now or else. 
But each library can choose log at which level. So SQLAlchemy logs SQL queries
at the INFO level on "sqlalchemy.engine.ENGINE_NAME", even though some people
would consider this debugging information. 

Logger names do NOT automatically correspond to Python module names, although
it's customary to do so if there's no better name for the logger. That lets the
user quickly find the code that produced a log message.  In Akhet applications,
several loggers are predefined with the same name as the containing module.
E.g., ``zzz.helpers.main`` has the following code::

    import logging
    log = logging.getLogger(__name__)

This creates a variable ``log`` which is the "zzz.helpers.main" logger.
(``__name__`` is a special Python variable which is the name of the current
moduole.)

By default, *development.ini* sets the root logger to WARN, the application
logger to DEBUG, and the SQLAlchemy engine logger to INFO. This displays all
application logging and SQL queries, but suppresses all other messages unless
they're warnings or errors. *production.ini* sets all of these to WARN, to
avoid filling up your log files with trivial success messages. You can adjust
the log levels as you wish. You can also set other loggers to different levels
by creating a section for them and listing them in the "[loggers]" section.
they're warnings or errors. 

"paster serve" activates logging when it starts up. If you're not using "paster
serve", you can activate logging yourself this way::

    import logging.config
    logging.config.fileConfig(INI_FILENAME)

Init module
===========

A Pyramid application revolves around a top-level ``main()`` function in the
application package. "paster serve" does the equivalent of this::

    # Instantiate your WSGI application
    import zzz
    app = zzz.main(**settings)

The Pylons equivalent to ``main()`` is ``make_app()`` in middleware.py. The
``main()`` function replaces Pylons' middleware.py, config.py, *and* routing.py
but is much shorter:

.. code-block:: python
   :linenos:

    from pyramid.config import Configurator
    import akhet
    import pyramid_beaker
    import sqlahelper
    import sqlalchemy

    def main(global_config, XXsettings):
        """ This function returns a Pyramid WSGI application.
        """

        # Here you can insert any code to modify the ``settings`` dict.
        # You can:
        # * Add additional keys to serve as constants or "global variables" in the
        #   application.
        # * Set default values for settings that may have been omitted.
        # * Override settings that you don't want the user to change.
        # * Raise an exception if a setting is missing or invalid.
        # * Convert values from strings to their intended type.

        # Create the Pyramid Configurator.
        config = Configurator(settings=settings)
        config.include("pyramid_handlers")
        config.include("akhet")

        # Initialize database
        engine = sqlalchemy.engine_from_config(settings, prefix="sqlalchemy.")
        sqlahelper.add_engine(engine)
        config.include("pyramid_tm")

        # Configure Beaker sessions
        session_factory = pyramid_beaker.session_factory_from_settings(settings)
        config.set_session_factory(session_factory)

        # Configure renderers and event subscribers
        config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
        config.add_subscriber("zzz.subscribers.create_url_generator",
            "pyramid.events.ContextFound")
        config.add_subscriber("zzz.subscribers.add_renderer_globals",
                              "pyramid.events.BeforeRender")

        # Set up view handlers
        config.include("zzz.handlers")

        # Set up other routes and views
        # ** If you have non-handler views, create create a ``zzz.views``
        # ** module for them and uncomment the next line.
        #
        #config.scan("zzz.views")

        # Mount a static view overlay onto "/". This will serve, e.g.:
        # ** "/robots.txt" from "zzz/static/robots.txt" and
        # ** "/images/logo.png" from "zzz/static/images/logo.png".
        #
        config.add_static_route("zzz", "static", cache_max_age=3600)

        # Mount a static subdirectory onto a URL path segment.
        # ** This not necessary when using add_static_route above, but it's the
        # ** standard Pyramid way to serve static files under a URL prefix (but
        # ** not top-level URLs such as "/robots.txt"). It can also serve files from
        # ** third-party packages, or point to an external HTTP server (a static
        # ** media server).
        # ** The first commented example serves URLs under "/static" from the
        # ** "zzz/static" directory. The second serves URLs under 
        # ** "/deform" from the third-party ``deform`` distribution.
        #
        #config.add_static_view("static", "zzz:static")
        #config.add_static_view("deform", "deform:static")

        return config.make_wsgi_app()

(Note: ``**settings`` in line 7 is displayed as ``XXsettings`` due to a
limitation in our documentation generator: "``*``" in code blocks
outside comments make Vim's syntax highlighting go bezerk.)

Lines 11-18 are a long comment explaining how you can modify the ``settings``
dict. If you have any code to set "global variables" for the application, or to
validate the settings or convert the values from strings to other types, 
put the code here. (We're considering a default routine to validate the
settings but haven't decided whether to use homegrown code, Colander,
FormEncode, or another validation library.)

Line 21 instantiates a ``Configurator`` which will create the application.
(It's not the application itself.) Lines 22-23 add plug-in functionality to
the configurator. The argument is the name of a module that contains an
``includeme()`` function. Line 22 ultimately creates the
``config.add_handler()`` method; line 23 creates the
``config.add_static_route()`` method. 

Line 26 creates a SQLAlchemy engine based on the "sqlalchemy.url" setting in
*development.ini*. The default setting is
"sqlite:///%(here)s/db.sqlite", which creates or opens a database "db.sqlite"
in the same directory as the INI file. You can also pass other engine arguments
to SQLAlchemy, either by putting them in the INI file with the "sqlalchemy."
prefix, or by passing them as keyword args. Line 27 adds the engine to the
``sqlahelper`` library so that the model can use it; it also updates the
library's contextual session.  Line 28 initializes the "pyramid_tm" transaction
manager. SQLAHelper is further explained in the Models section below; the
transaction manager is explained in the "Transaction Manager" chapter.

(Note: if you answered 'n' to the SQLAlchemy question when creating the
application, lines 4-5 and 25-28 will not be present in your module.)

Lines 31-32 configure the session factory. 

Line 35 tells Pyramid to render *\*.html* templates using Mako. Pyramid out of
the box renders Mako templates with the *\*.mako* or *\*.mak* extensions, and
Chameleon templates with the *\*.pt* extension, but you have to tell it if you
want to use a different extension or another template engine. Third-party
packages are available for using Jinja2 (``pyramid_jinja2``), and
a Genshi emulator using Chameleon (``pyramid_genshi_chameleon``),

Lines 36-39 registers event subscribers, which are callback functions called at
specific points during request processing. Lines 36-37 register a callback that
instantiates a URL generator (see "URL Generator" section). Lines 38-39
register a callback which adds several Pylons-like variables to the template
namespace whenever a template is rendered. The callbacks are defined in the
``zzz.subscribers`` module, which you can modify.

Lines 42 configures routing. Actually it calls an include function in the
handlers package. We'll explore routing more fullyh later.

Lines 44-48 and 56-67 are commented code; they show how to enable certain
advanced features.

Line 54 is equivalent to the *public* directory in Pylons applications. It's
not a standard part of Pyramid, which handles static files a different way, but
this method is closer to the Pylons tradition. Any URLs which did not match a
dynamic route will be compared to the contents of the *zzz/static* directory,
and if a file exists for the URL, it is served. Unlike Pylons, this happens
after the dynamic routes are tried rather than before. This means that any
dynamic route that might accidentally match a static resource must explicitly
exclude that URL. 

This is just one of several ways to serve static files in Pyramid, each with
its own advantages and disadvantages. These are all discussed below in the
Static Files section.

Line 69 creates and returns a Pyramid WSGI application based on the
configuration.

This short main function -- compared to Pylons' three functions in three
modules -- allows an entire small application to be defined in a single module.
Half the lines are comments so they can be deleted.  A short main function is
useful for small demos, but the principle also leads to a different developer
culture. Pylons' application template is complex enough that most people don't
stray from it, and Pylons' documentation emphasizes using "paster serve" rather
than other invocation methods. Pyramid's docs encourage users to structure
everything outside ``main()`` as they wish, and they describe "paster serve" as
just one way to invoke the application. The INI files and "paster serve" are
just for your convenience; you don't have to use them.

A bit more about Paster
-----------------------

"paster serve" does several other things besides calling the main function.
It interpolates "%(here)s" placeholders in the INI file, as well as
variables in the "[DEFAULT]" section (which we aren't using here). It
configures logging, and finds the application by looking up the entry point
specified in the 'use' variable. All this can be done by the following code
in both Pyramid and Pylons::

    import logging.config
    import os
    import paste.deploy.loadwsgi as loadwsgi
    ini_path = "/path/to/development.ini"
    logging.config.fileConfig(ini_path)
    app_dir, ini_file = os.path.split(ini_path)
    app = loadwsgi.loadapp("config:" + ini_file, relative_to=app_dir)

Models
======

The default *zzz/models/__init__.py* looks like this::

    import logging
    import sqlahelper
    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    import transaction

    log = logging.getLogger(__name__)

    Base = sqlahelper.get_base()
    Session = sqlahelper.get_session()


    #class MyModel(Base):
    #    __tablename__ = "models"
    #
    #    id = sa.Column(sa.Integer, primary_key=True)
    #    name = sa.Column(sa.Unicode(255), nullable=False)

Pylons applications have a "zzz.model.meta" model to hold SQLAlchemy's
housekeeping objects, but Akhet uses the SQLAHelper library which holds them
instead. This gives you more freedom to structure your models as you wish,
while still avoiding circular imports (which would happen if you defined
Session in the main module and then import the other modules into it; the
other modules would import the main module to get the Session, and voilà
circular imports).

A real application would replace the commented ``MyModel`` class with
one or more ORM classes. The example uses SQLAlchemy's "declarative" syntax,
although of course you don't have to. 

SQLAHelper
----------

The SQLAHelper library is a holding place for the application's contextual
session (normally assigned to a ``Session`` variable with a capital S, to
distinguish it from a regular SQLAlchemy session), all engines used by the
application, and an optional declarative base. We initialized it via the
``sqlahelper.add_engine`` line in the main function. Because we did not specify
an engine name, the library set the engine name to "default", and also bound the
contextual session and the base's metadata to it. 

There's not much else to know about SQLAHelper. You can call ``get_session()``
at any time to get the contextual session. You can call ``get_engine()`` or
``get_engine(name)`` to retrieve an engine that was previously added. You can
call ``get_base()`` to get the declarative base.  

If you need to modify the session-creation parameters, you can call
``get_session().config(...)``. But if you modify the session extensions, see
the "Transaction Manager" chapter to avoid losing the extension that powers the
transaction manager.

View handlers
=============

The default *handlers.py* looks like this::

    import logging

    from pyramid_handlers import action

    #from zzz.models import MyModel

    log = logging.getLogger(__name__)

    class MainHandler(object):
        def __init__(self, request):
            self.request = request

        @action(renderer='index.html')
        def index(self):
            log.debug("testing logging; entered MainHandler.index()")
            return {'project':'zzz'}

This is clearly different from Pylons, and the ``@action`` decorator looks a
bit like TurboGears. The Pyramid developers decided to go with the
return-a-dict approach because it helps in two use cases: (1) unit testing,
where you want to test the data calculated rather than parsing the HTML output,
and (2) cases where the same data is rendered by different templates or
sometimes as a JSON web service. The testing use is configured by default: the
view decorators decorators do not modify the return value or arguments, but
merely set method attributes or interact with the configurator. The
multi-template scenarios are handled by multiple ``@action`` decorators on the
same method: each decorator can specify a different action name, which
determines which URL goes to it, while using the same view callable.

Pyramid does not have a base handler, although you can create your own to save
``self.request`` and define any shared methods. 

If you have any handler-wide variables you want to pass to template, one trick
is to assign them as attributes to ``self.request.tmpl_context``. That's the
same as as pylons.tmpl_context except it's not a global; it's just an empty
object used to pass request-local data to the template or between handler
methods. Note that non-template renderers such as "json" generally ignore it,
so it's really only useful for HTML-only data like which stylesheet to use.

``index`` is a view method. Its ``@action`` decorator has a ``renderer`` arg
naming a template (defined in *zzz/templates/index.html*). The method itself
does a trivial example of logging and then returns a dict of template variables.

Let's go back to the route that points to this view. ::

    config.add_handler('home', '/', 'zzz.handlers:MainHandler',
                       action='index')

This route is triggered whenever the URL is "/". It  instantiates
``MainHandler``, and calls its ``index`` method. The ``@action`` decorator sets
up a renderer for the view. The renderer takes the view's return value (a
dict), invokes the specified template (index.html) using the dict's variables,
and creates a Response to return to the router. This is the most common pattern
in a Pylons-like Pyramid application. The view also has the option of creating
and returning a Response itself; in this case the renderer will be bypassed. 

Redirecting and HTTP errors
---------------------------

To issue a redirect inside a view, return an HTTPFound::

    from pyramid.httpexceptions import HTTPFound

    def myview(self):
        return HTTPFound(location=request.route_url("foo"))
        # Or to redirect to an external site
        return HTTPFound(location="http://example.com/")

You can return other HTTP errors the same way: ``HTTPNotFound``, ``HTTPGone``,
``HTTPForbidden``, ``HTTPUnauthorized``, ``HTTPInternalServerError``, etc.
These are all subclasses of both ``Response`` and ``Exception``.  Although you
can raise them, Pyramid prefers that you return them instead.

If you intend to raise them, you have to do two extra things. One, define an
exception view for each one that returns the exception object itself
(``request.exception``). Two, if you want to be compatible with Python 2.4 and
2.3, do ``raise HTTPNotFound().exception()`` rather than raising the instance
directly. HTTP exceptions are new-style classes which can't be raised in Python
2.4 or 2.3.  See the Views chapter in the Pyramid manual for details on
exception views and raising HTTP exceptions.

Pyramid catches two non-HTTP exceptions by default,
``pyramid.exceptions.NotFound`` and ``pyramid.exceptions.Forbidden``, which
it sends to the Not Found View and the Forbidden View respectively. You can
override these views to display custom HTML pages.

app_globals and cache
---------------------

Pyramid does not currently have an equivalent to Pylons "app_globals" and
"cache" variables. For "app_globals" you can use the Pyramid registry or
abuse "settings" (the config variables from the INI file, available as
``request.registry.settings``). You can also use ordinary module globals or
class attributes, provided  you don't run multiple instances of Pyramid
applications in the same process. (Pyramid does not encourage multiple
applications per process anyway. Instead Pyramid recommends its extensibility
features such as its Zope Component Architecture, which allow you to write
pieces of code to interfaces and plug them into a single application.)

For caching, you can configure Beaker caching the same way Pylons does, but
this has not been currently documented. `One user's recommendation`_. Perhaps
make a cache object in the registry or settings?

.. _One user's recommendation: http://groups.google.com/group/pylons-devel/browse_thread/thread/b628bc639711889c

More on routing and traversal
=============================

Routing methods and view decorators
-----------------------------------

Pyramid has several routing methods and view decorators. The ones we've seen,
from the ``pyramid_handlers`` package, are:

.. function:: @action(\*\*kw)

   I make a method in a class into a *view* method, which
   ``config.add_handler`` can connect to a URL pattern. By definition, any class
   that contains view methods is a view handler. My most interesting args are 
   'name' and 'renderer'. If 'name' is NOT specified, the action name is the
   same as the method name. If 'name' IS specified, the action name can be
   different. If 'renderer' is specified, it indicates a renderer or template
   (and the template's extension indicates a renderer). If multiple ``@action``
   decorators are put on a single method, each must have a different name, and
   they presumably will have different renderers too.

.. method:: config.add_handler(name, pattern, handler, action=None, \*\*kw)

   I create a route connecting the URL pattern to the handler class. If
   'action' is specified, I connect the route to that specific action (a method
   decorated with the ``@action`` decorator). If 'action' is not specified, the
   pattern must contain a "{action}" placeholder. In that case I scan the
   handler class for all possible actions. It is an error to specify both "{action}"
   and an ``action`` arg. I pass extra keyword args to ``config.add_route``,
   and keyword args in the ``@action`` decorator to ``config.add_view``.

``config.add_handler`` calls two lower-level methods which you can also call
directly:

.. method:: config.add_route(name, pattern, \*\*kw)

   Create a route connecting a URL pattern directly to a view callable outside
   a handler.  The view is specified with a 'view' arg. If the view is a
   function, it must take a Request argument and return a Response (or any
   object with the three required attributes). If it's a class, the constructor
   takes the Request argument and the specified method (``.__call__`` by
   default) is called with no arguments.

.. method:: config.add_view(\*\*kw)

   I register a view (specified with a 'view' arg). In URL dispatch, you
   normally don't call this directly but let ``config.add_handler`` or
   ``config.add_route`` call it for you. In traversal, you call this to
   register a view. The 'name' argument is the view name, which is used by
   traversal to choose which view to invoke.

Two others you should know about:

.. function:: config.scan(package=None)

   I scan the specified package (which may be an asset spec) and import all its
   modules recursively, looking for functions decorated with ``@view_config``.
   For each such function, I call ``add_view`` passing the decorator's args to
   it. I can also scan a package, in which case all submodules in the package
   are recursively scanned. If no package is specified, I scan the caller's
   package (i.e., the entire application). 
   
   I can also be called for my side effect of importing all of a package's
   modules even if none of them contain ``@view_config``.

.. function:: @view_config(\*\*kw)

   I decorate a function so that ``config.scan`` will recognize it as a view
   callable, and I also hold ``add_view`` arguments that ``config.scan`` will
   pick up and apply.  I can also decorate a class or a method in a class.


Route arguments and predicates
------------------------------

``config.add_handler`` accepts a large number of keyword
arguments. We'll list the ones most commonly used with Pylons-like applications
here. For full documentation see the `add_route
<http://docs.pylonsproject.org/projects/pyramid/1.0/api/config.html#pyramid.config.Configurator.add_route>`_
API. Most of these arguments can also be used with ``config.add_route``.

The arguments are divided into *predicate arguments* and *non-predicate
arguments*.  Predicate arguments determine whether the route matches the
current request: all predicates must pass in order for the route to be chosen.

name

    [Non-predicate] The first positional arg; required. This must be a unique name
    for the route, and is used in views and templates to generate the URL.

pattern

    [Predicate] The second positional arg; required. This is the URL path with
    optional "{variable}" placeholders; e.g., "/articles/{id}" or
    "/abc/{filename}.html". The leading slash is optional. By default the
    placeholder matches all characters up to a slash, but you can specify a
    regex to make it match less (e.g., "{variable:\d+}" for a numeric variable)
    or more ("{variable:.*}" to match the entire rest of the URL including
    slashes). The substrings matched by the placeholders will be available as
    *request.matchdict* in the view.

    A wildcard syntax "\*varname" matches the rest of the URL and puts it into
    the matchdict as a tuple of segments instead of a single string.  So a
    pattern "/foo/{action}/\*fizzle" would match a URL "/foo/edit/a/1" and
    produce a matchdict ``{'action': u'edit', 'fizzle': (u'a', u'1')}``.

    Two special wildcards exist, "\*traverse" and "\*subpath". These are used
    in advanced cases to do traversal on the right side of the URL, and should
    be avoided otherwise.

factory

    [Non-predicate] A callable (or asset spec). In URL dispatch, this returns a
    *root resource* which is also used as the *context*. If you don't specify
    this, a default root will be used. In traversal, the root contains one
    or more resources, and one of them will be chosen as the context.

xhr

    [Predicate] True if the request must have an "X-Reqested-With" header. Some
    Javascript libraries (JQuery, Prototype, etc) set this header in AJAX
    requests.

request_method

    [Predicate] An HTTP method: "GET", "POST", "HEAD", "DELETE", "PUT". Only
    requests of this type will match the route.

path_info

    [Predicate] A regex compared to the URL path (the part of the URL after the
    application prefix but before the query string). The URL must match this
    regex in order for the route to match the request.

request_param

    [Predicate] If the value doesn't contain "=" (e.g., "q"), the request must
    have the specified parameter (a GET or POST variable). If it does contain
    "=" (e.g., "name=value"), the parameter must have the specified value.

header

    [Predicate] If the value doesn't contain ":"; it  specifies an HTTP header
    which must be present in the request (e.g., "If-Modified-Since"). If it
    does contain ":", the right side is a regex which the header value must
    match; e.g., "User-Agent:Mozilla/.\*". The header name is case insensitive.

accept

    [Predicate] A MIME type such as "text/plain", or a wildcard MIME type with
    a star on the right side ("text/\*") or two stars ("\*/\*"). The request
    must have an "Accept:" header containing a matching MIME type.

custom_predicates

    [Predicate] A sequence of callables which will be called in order to
    determine whether the route matches the request. The callables should
    return ``True`` or ``False``. If any callable returns ``False``, the route
    will not match the request. The callables are called with two arguments,
    ``info`` and ``request``. ``request`` is the current request. ``info`` is a
    dict which contains the following::
    
        info["match"]  =>  the match dict for the current route
        info["route"].name  =>  the name of the current route
        info["route"].pattern  =>  the URL pattern of the current route

    Use custom predicates argument when none of the other predicate args fit
    your situation.  See
    <http://docs.pylonsproject.org/projects/pyramid/1.0/narr/urldispatch.html#custom-route-predicates>`
    in the Pyramid manual for examples.

    You can modify the match dict to affect how the view will see it. For
    instance, you can look up a model object based on its ID and put the object
    in the match dict under another key. If the record is not found in the
    model, you can return False to prevent the route from matching the request;
    this will ultimately case HTTPNotFound if no other route or traversal
    matches the URL.  The difference between doing this and returning
    HTTPNotFound in the view is that in the latter case the following routes
    and traversal will never be consulted. That may or may not be an advantage
    depending on your application.

View arguments
--------------

These can be specified in ``@action``, ``@view_config``, and
``config.add_view``.  ``config.add_route`` has counterparts to some of these,
such as 'view_permission'. 

view

    A view callable (or asset spec). Useful only in ``config.add_view`` because
    the decorators already know the view.

name

    The view name. With view handlers it's the same as the route's 'action',
    and by default is the same name as the view callable. In traversal it's used
    to look up a view by name.

renderer

    The name of a renderer or template (whose extension indicates the
    renderer). A renderer converts a view's return value into a Response.
    Template renderers expect the view to return a dict. Non-template renderers
    include "json" which serializes the result to JSON, and "string" which
    calls ``str()`` on the result unless it's already a Unicode object.  If you
    don't specify a renderer, the view must return a Response object itself (or
    any object having three particular attributes). The View can also return a
    Response object to bypass the renderer.  HTTP errors such as HTTPNotFound
    also bypass the renderer.
   
permission

    A string permission name. This is discussed in the Authorization section
    below.
    
wrapper

    The name of another view which will be called after this view returns. This
    makes it possible to chain views together. (XXX Is this compatible with
    view handlers?)

The request object
==================

The Request object contains all information about the current request state and
application state. It's available as ``self.request`` in handler views, the
``request`` arg in view functions, and the ``request`` variable in templates.
(In other places you can get it via
``pyramid.threadlocal.get_current_request()``, but you really shouldn't except in
unit tests or pshell. If something you call from the view requires it, pass it
as an argument.)

Pyramid's Request_ object is a subclass of WebOb.Request_ just like
pylons.request is, so it contains all the same attributes in methods like
``params``, ``GET``, ``POST``, ``headers``, ``method``, ``charset``, ``date``,
``environ``, ``body``, ``body_file``. 
so it contains all 
attributes and methods.  The following are specific to Pyramid.

Special Pyramid attributes and methods
--------------------------------------

.. attribute:: context

   The request context, used mainly in authorization and traversal.

.. attribute:: matchdict

   The routing match dict, whose keys are the placeholders in the route
   pattern, and whose values are the substrings matched by those placeholders.
   ``None`` if no route matched the URL (which would occur only with
   traversal).

.. attribute:: matched_route

   The route object that matched the URL. It has ``.name`` and ``.pattern``
   attributes.

.. attribute:: registry

   The Pyramid registry, which is global to the application.

.. attribute:: registry.settings

   The settings parsed from the INI file.
    
.. attribute:: session

   The session.

.. attribute:: tmpl_context

   An empty object used to pass data to the template or between methods in the
   view handler. Equivalent to "pylons.tmpl_context". This is mainly used in
   the handler's constructor to pass handler-wide data to the template without
   having to make the view method put it in its return dict. This object is
   available as the ``c`` variable in templates, and in views you can assign it
   to a local variable ``c`` for convenience.

.. attribute:: root, subpath, traversed, view_name

   Attributes useful with traversal.

.. attribute:: virtual_root, virtual_root_path

   Attributes useful in virtual hosting.

.. attribute:: exception

   Defined only in the exception view or in certain callbacks. It indicates the
   exception that was raised, or ``None`` if no exception.

.. attribute:: get_response(app, catch_exc_info=False)

   Call another WSGI application and return a Response. This can be used in a
   view to delegate to an external WSGI application.

URL generation methods
----------------------

.. method:: route_path(route_name, \*elements, \*\*kw)

   Generate a URL by route name. Equivalent to "pylons.url(route_name,
   \*\*kw)".  XXX What are 'elements'?

.. method:: route_url(route_name, \*elements, \*\*kw)

   Same as ``route_path`` but include the scheme and domain. Equivalent to
   "pylons.url(route_name, qualified=True, \*\*kw)".

.. method:: resource_url(resource, \*elements, \*\*kw)

   Generate a URL to a resource. This is mainly used with traversal, and is not
   useful in a pure Pylons-like application.

.. method:: static_url(path, \*\*kw)

   Generate a URL to a static resource defined with
   ``config.add_static_view()``. This is not useful with the default
   ``pyramid_sqla`` application template, which uses
   ``config.add_static_route()`` instead of ``config.add_static_view()``. 

Path attributes
---------------

These correspond to parts of the request URL.

.. attribute:: path

    The full URL path including SCRIPT_NAME and PATH_INFO, but not including
    the scheme, host, or query string. 

.. attribute:: application_url

    A partial URL including the scheme, host, and SCRIPT_NAME. 

.. attribute:: script_name

    The first part of the URL path corresponding to the application itself.
    It's either empty or starts with a slash, but does not end with a slash.
    E.g., "" or "/my-application".

.. attribute:: path_info

    The part of the URL path after the SCRIPT_NAME. This is the part the
    application is responsible for parsing. It always starts with a slash and
    does not include the query string.  In certain situations, segments are
    moved from path_info to script_name. 

.. attribute:: path_qs

    The full URL path with query string, but without the scheme or host.

.. attribute:: path_url

    The absolute URL including the scheme, host, script_name, and path_info,
    but not the query string.

.. attribute:: scheme, script_name, path_info, query_string

     Individual parts of the URL.

.. attribute:: url

     The complete URL including scheme, host, script_name, path_info, and query
     string.

Attributes affecting the response
---------------------------------

The following attributes tell the renderer what kind of Response to create.

.. attribute:: response_status

   The response status in WSGI format (e.g., "200 OK").

.. attribute:: response_content_type

   The MIME type of the response; e.g., "text/xml".

.. attribute:: response_charset

   The charcter set of the response (e.g., "utf-8").

.. attribute:: response_headerlist

   A list of tuples representing HTTP headers to be set in the response.
   E.g., ``[('Set-Cookie', 'abc=123'), ('X-My-Header', 'foo')]``.

.. attribute:: response_cache_for

   A value in seconds which will influence the "Cache-Control" and "Expires"
   headers in the response.

Callbacks
---------

.. method:: add_response_callback(callback)

    Push a callback function to be called after the response is created. The
    function will be called as ``callback(request, response)``. You may modify
    the response. Callbacks will be called in the order pushed. Callbacks will
    not be called if an exception occurs.

.. method:: add_finished_callback(callback)

    Push a callback function to be called at the end of request processing,
    even if an exception occurs. The function will be called as
    ``callback(request)``. You can't use this to modify the effective
    response.

.. _Request: http://docs.pylonsproject.org/projects/pyramid/1.0/api/request.html
.. _WebOb.Request: http://pythonpaste.org/webob/reference.html#id1

Templates
=========

Pyramid has built-in support for Mako and Chameleon templates. Chameleon runs
only on CPython and Google App Engine, not on Jython or other platforms. Jinja2
support is available via the ``pyramid_jinja2`` package on PyPI, and a Genshi
emulator using Chameleon is in the ``pyramid_chameleon_genshi`` package.

Whenever a renderer invokes a template, the template namespace includes all the
variables in the view's return dict, plus the following:

.. attribute:: request

   The current request.

.. attribute:: context

   The context (same as ``request.context``).

.. attribute:: renderer_name

   The fully-qualified renderer name; e.g., "zzz:templates/foo.mako".

.. attribute:: renderer_info

   An object with attributes ``name``, ``package``, and ``type``.

The subscriber in your application adds the following additional variables:

.. attribute:: c, tmpl_context

   ``request.tmpl_context``

.. attribute:: h

   The helpers module, defined as "zzz.helpers". This is set by a subscriber
   callback in your application; it is not built into Pyramid. 

.. attribute:: session

   ``request.session``.

.. attribute:: url

   ``request.route_url``.

If you need to fill a template within view code or elsewhere, do this::

    from pyramid.renderers import render
    variables = {"foo": "bar"}
    html = render("mytemplate.mako", variables, request=request)

There's also a ``render_to_response`` function which invokes the template and
returns a Response, but usually it's easier to let ``@action`` or
``@view_config`` do this.

For further information on templating see the Templates section in the Pyramid
manual, the Mako manual, and the Chameleon manual.  You can customize Mako's
TemplateLookup by setting "mako.*" variables in the INI file.

Most applications using Mako will define a site template something like this:

.. code-block:: mako

   <!DOCTYPE html>
   <html>
     <head>
       <title>${self.title()}</title>
       <link rel="stylesheet" href="${application_url}/default.css"
           type="text/css" />
     </head>
     <body>

   <!-- *** BEGIN page content *** -->
   ${self.body()}
   <!-- *** END page content *** -->
     </body>
   </html>
   <%def name="title()" />

Then the page templates can inherit it like so:

.. code-block:: mako

   <%inherit file="/site.html" />
   <%def name="title()">My Title</def>
   ... rest of page content goes here ...

Static files
============

Pyramid has five ways to serve static files. Each algorithm has different
advantages and limitations, and requires a different way to generate static
URLs.

``config.add_static_route``

    This is the default algorithm in the ``pyramid_sqla`` application template,
    and is closest to Pylons. It serves the static directory as an overlay on
    "/", so that URL "/robots.txt" serves "zzz/static/robots.txt", and URL
    "/images/logo.png" serves "zzz/static/images/logo.png". If the file does
    not exist, the route will not match the URL and Pyramid will try the next
    route or traversal. You cannot use any of the URL generation methods with
    this; instead you can put a literal URL like
    "${application_url}/images/logo.png" in your template. 

    Usage::

        config.include('pyramid_sqla')
        config.add_static_route('zzz', 'static', cache_max_age=3600)
        # Arg 1 is the Python package containing the static files.
        # Arg 2 is the subdirectory in the package containing the files.

``config.add_static_view``

    This is Pyramid's default algorithm. It mounts a static directory under a
    URL prefix such as "/static". It is not an overlay; it takes over the URL
    prefix completely. So URL "/static/images/logo.png" serves file
    "zzz/static/images/logo.png". You cannot serve top-level static files like
    "/robots.txt" and "/favicon.ico" using this method; you'll have to serve
    them another way. 

    Usage::

        config.add_static_view("static", "zzz:static")
        # Arg 1 is the view name which is also the URL prefix.
        # It can also be the URL of an external static webserver.
        # Arg 2 is an asset spec referring to the static directory/

    To generate "/static/images/logo.png" in a Mako template, which will serve
    "zzz/static/images/logo.png":

    .. code-block:: mako

       href="${request.static_url('zzz:static/images/logo.png')}

    One advantage of add_static_view is that you can copy the static directory
    to an external static webserver in production, and static_url will
    automatically generate the external URL:

    .. code-block:: ini

        # In INI file
        static_assets = "static"
        # -OR-
        static_assets = "http://staticserver.com/"

    ..  code-block:: python

        config.add_static_view(settings["static_assets"], "zzz:static")

    .. code-block:: mako

        href="${request.static_url('zzz:static/images/logo.png')}"
        ## Generates URL "http://staticserver.com/static/images/logo.png"

Other ways

    There are three other ways to serve static files. One is to write a custom
    view callable to serve the file; an example is in the Static Assets section
    of the Pyramid manual. Another is to use ``paste.fileapp.FileApp`` or
    ``paste.fileapp.DirectoryApp`` in a view. These three ways can be used with
    ``request.route_url()`` because the route is an ordinary route. The
    advantage of these three ways is that they can serve a static file or
    directory from a normal view callable, and the view can be protected
    separately using the usual authorization mechanism.

Session, flash messages, and secure forms
=========================================

Pyramid's session object is ``request.session``. It has its own interface but
uses Beaker on the back end, and is configured in the INI file the same way as
Pylons' session. Like Pylons' session, it's a dict-like object and can store
any pickleable values. Unlike Pylons session, you don't have to call
``session.save()`` after adding or replacing a key because Pyramid does it for
you, but you do have to call
``session.changed()`` when you modify a mutable value in place.  You can call
``session.invalidate()`` to discard the session data at the end of the request.
``session.created`` is an integer timestamp in Unix ticks telling when the
session was created, and ``session.new`` is true if it was created during this
request (as opposed to being loaded from persistent storage).

Pyramid sessions have two extra features: flash messages and a secure form
token. These replace ``webhelpers.pylonslib.flash`` and
``webhelpers.pylonslib.secure_form``, which are incompatible with Pyramid.

Flash messages are a session-based queue. You can push a message to be
displayed on the next request, such as before redirecting. This is often used 
after form submissions, to push a success or failure message before redirecting
to the record's main screen. (This is different from form validation, which
normally redisplays the form with error messages if the data is rejected.)

To push a message, call ``request.session.flash("My message.")`` The message is
normally text but it can be any object. Your site template will then have to
call ``request.session.pop_flash()`` to retrieve the list of messages, and
display then as it wishes, perhaps in <div>'s or a <ul>. The queue is
automatically cleared when the messages are popped, to ensure they are
displayed only once.

The full signature for the flash method is::

    session.flash(message, queue='', allow_duplicate=True)

You can have as many message queues as you wish, each with a different string
name. You can use this to display warnings differently from errors, or to show
different kinds of messages at different places on the page. If
``allow_duplicate`` is false, the message will not be inserted if an identical
message already exists in that queue. The ``session.pop_flash`` method also takes a
queue argument to specify a queue. You can also use ``session.peek_flash`` to
look at the messages without deleting them from the queue.

The secure form token prevents cross-site request forgery (CSRF)
attacts. Call ``session.get_csrf_token()`` to get the session's token, which is
a random string. (The first time it's called, it will create a new random token and
store it in the session. Thereafter it will return the same token.) Put the
token in a hidden form field. When the form submission comes back in the next
request, call ``session.get_csrf_token()`` again and compare it to the hidden
field's value; they should be the same. If the form data is missing the field
or the value is different, reject the request, perhaps by returning a forbidden
status. ``session.new_csrf_token()`` always returns a new token, overwriting
the previous one if it exists.

WebHelpers and forms
====================

Most of WebHelpers works with Pyramid, including the popular
``webhelpers.html`` subpackage, ``webhelpers.text``, and ``webhelpers.number``.
Pyramid does not depend on WebHelpers so you'll have to add the dependency to
your application if you want to use it.  The only part that doesn't work with
Pyramid is the ``webhelpers.pylonslib`` subpackage, which depends on Pylons'
special globals.

``webhelpers.paginate`` is mostly compatible, except that if you want to use the
``Page.pager()`` method, you have to create your own URL generator callback and
pass it to the constructor. Pyramid does not have ``pylons.url`` or
``route.url_for`` globals, so Paginate can't calculate the other page's URLs
otherwise.  Here's one way to create a URL generator::

    from webhelpers.paginate import Page
    from webhelpers.util import update_params

    # Inside a view method -- ``self`` comes from the surrounding scope.
    def url_generator(page):
        return update_params(self.request.path_qs, page=page) 
    records = Page(collection, page=1, items_per_page=20, url=url_generator)

The WebHelpers' developers have discussed adding another constructor arg for
the current URL, but WebHelpers has already had so many URL generation schemes
added to it that there's some reluctance to add more. Also, if WebHelpers
changed the 'page' parameter, it wouldn't work with URLs that use a different
parameter name or put the page number in the URL path.


Authentication and Authorization
================================

XXX

Shell
=====

.. code-block:: sh

    $ paster pshell development.ini Zzz
    Python 2.6.6 (r266:84292, Sep 15 2010, 15:52:39) 
    [GCC 4.4.5] on linux2
    Type "help" for more information. "root" is the Pyramid app root object, "registry" is the Pyramid registry object.
    >>> registry.settings["sqlalchemy.url"]
    'sqlite:////home/sluggo/exp/pyramid-docs/main/workspace/Zzz/db.sqlite'
    >>> import pyramid.threadlocal
    >>> req = pyramid.threadlocal.get_current_request()
    >>> 

Shell
=====

**paster pshell** is similar to Pylons' "paster shell". It gives you an
interactive shell in the application's namespace with a dummy request. Unlike
Pylons, you have to specify the application section on the command line because
it's not "main". Akhet, for convenience, names the section "myapp" regardless
of the actual application name. To get the request, but you also need to
specify the name of the app section because it's not "main".  Akhet, for
convenience,  names the section "myapp" regardless of the actual application
name.

.. code-block:: sh

    $ paster pshell development.ini myapp



Testing
=======

XXX

Deployment
==========

Deployment is the same for Pyramid as for Pylons. Use "paster serve" with
mod_proxy, or mod_wsgi, or whatever else you prefer. 

Internationalization
====================

XXX Support exists. I've never done this so I can't explain it.

Other Pyramid features
======================

XXX Events, hooks, extending (ZCA), ZCML.

XXX URL Generator

XXX Transaction manager

XLines 27-28 are one such route: "/{action}" would match
"/favicon.ico", "/robots.txt", and "/w3c" (the `machine-readable privacy policy
<http://www.w3.org/P3P/>`_ standard), so it has a ``path_info`` argument to
exclude these.