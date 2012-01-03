django-notification
===================

Many sites need to notify users when certain events have occurred and to allow
configurable options as to how those notifications are to be received.

The project aims to provide a Django app for this sort of functionality. This
includes:

 * submission of notification messages by other apps
 * notification messages on signing in
 * notification messages via email (configurable by user)
 * notification messages via feed

Dependencies
------------

If you want migrations, please install ``south``, but not required.

The use of ``django-mailer`` is recommended, but not required.

Installation
------------

Add ``notification`` to your INSTALLED_APPS and migrate/syncdb.

Create some ``NoticeType`` instances in your database.

Templates
---------

Make sure you have ``django.contrib.humanize`` in INSTALLED_APPS
if you use the default templates, as they load the filter.

Same goes for ``django-pagination`` and ``django-timezones``
which depends on ``pytz``.

Do note they extend a template called ``site_base.html``
so have that available as well.

Creating your own templates is recommended, all the views
take ``template_name`` as a parameter.

