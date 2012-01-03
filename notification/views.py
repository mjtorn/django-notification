from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render_to_response
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import feed
from django.contrib import messages
from django.template import RequestContext

from notification.models import *
from notification.decorators import basic_auth_required, simple_basic_auth_callback
from notification.feeds import NoticeUserFeed


@basic_auth_required(realm='Notices Feed', callback_func=simple_basic_auth_callback)
def feed_for_user(request):
    """
    An atom feed for all unarchived :model:`notification.Notice`s for a user.
    """
    url = "feed/%s" % request.user.username
    return feed(request, url, {
        "feed": NoticeUserFeed,
    })


@login_required
def notices(request,
            template_name='notification/notices.html'):
    """
    The main notices index view.

    Template: :template:`notification/notices.html`

    Context:

        notices
            A list of :model:`notification.Notice` objects that are not archived
            and to be displayed on the site.
    """
    notices = Notice.objects.notices_for(request.user, on_site=True)

    return render_to_response(template_name, {
        "notices": notices,
    })

@login_required
def notice_settings(request,
                    template_name='notification/notice_settings.html',
                    template_name_ajax='notification/notice_settings_ajax.html'):
    """
    The notice settings view.

    Template: :template:`notification/notice_settings.html`

    Context:

        notice_types
            A list of all :model:`notification.NoticeType` objects.

        notice_settings
            A dictionary containing ``column_headers`` for each ``NOTICE_MEDIA``
            and ``rows`` containing a list of dictionaries: ``notice_type``, a
            :model:`notification.NoticeType` object and ``cells``, a list of
            tuples whose first value is suitable for use in forms and the second
            value is ``True`` or ``False`` depending on a ``request.POST``
            variable called ``form_label``, whose valid value is ``on``.
    """
    if request.is_ajax():
        template_name = template_name_ajax

    notice_types = NoticeType.objects.all()
    settings_table = []
    for notice_type in notice_types:
        settings_row = []
        for medium_id, medium_display in NOTICE_MEDIA:
            form_label = "%s_%s" % (notice_type.label, medium_id)
            setting = get_notification_setting(request.user, notice_type, medium_id)
            if request.method == "POST":
                if request.POST.get(form_label) == "on":
                    if not setting.send:
                        setting.send = True
                        setting.save()
                else:
                    if setting.send:
                        setting.send = False
                        setting.save()
            settings_row.append((form_label, setting.send))
        settings_table.append({"notice_type": notice_type, "cells": settings_row})

    if(request.method == "POST" and
       request.REQUEST.has_key('next')):
        messages.add_message(request, messages.INFO, "Your notification settings have been saved.")
        return HttpResponseRedirect(request.REQUEST['next'])

    notice_settings = {
        "column_headers": [medium_display for medium_id, medium_display in NOTICE_MEDIA],
        "rows": settings_table,
    }

    context = {
        "notice_types": notice_types,
        "notice_settings": notice_settings,
    }
    req_ctx = RequestContext(request, context)

    return render_to_response(template_name, req_ctx)


@login_required
def single(request, id, mark_seen=True, template_name='notification/notice_settings.html'):
    """
    Detail view for a single :model:`notification.Notice`.

    Template: :template:`notification/single.html`

    Context:

        notice
            The :model:`notification.Notice` being viewed

    Optional arguments:

        mark_seen
            If ``True``, mark the notice as seen if it isn't
            already.  Do nothing if ``False``.  Default: ``True``.
    """
    notice = get_object_or_404(Notice, id=id)
    if request.user == notice.recipient:
        if mark_seen and notice.unseen:
            notice.unseen = False
            notice.save()
        return render(request, template_name, {
            "notice": notice,
        })
    raise Http404


@login_required
def archive(request, noticeid=None, next_page=None):
    """
    Archive a :model:`notices.Notice` if the requesting user is the
    recipient or if the user is a superuser.  Returns a
    ``redirect`` when complete.

    Optional arguments:

        noticeid
            The ID of the :model:`notices.Notice` to be archived.

        next_page
            The page to redirect to when done.
    """
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.recipient or request.user.is_superuser:
                notice.archive()
            else:   # you can archive other users' notices
                    # only if you are superuser.
                return redirect(next_page)
        except Notice.DoesNotExist:
            return redirect(next_page)
    return redirect(next_page)



@login_required
def delete(request, noticeid=None, next_page=None):
    """
    Delete a :model:`notices.Notice` if the requesting user is the recipient
    or if the user is a superuser.  Returns a ``redirect`` when
    complete.

    Optional arguments:

        noticeid
            The ID of the :model:`notices.Notice` to be archived.

        next_page
            The page to redirect to when done.
    """
    if noticeid:
        try:
            notice = Notice.objects.get(id=noticeid)
            if request.user == notice.recipient or request.user.is_superuser:
                notice.delete()
            else:   # you can delete other users' notices
                    # only if you are superuser.
                return redirect(next_page)
        except Notice.DoesNotExist:
            return redirect(next_page)
    return redirect(next_page)



@login_required
def mark_all_seen(request, success_url=None):
    """
    Mark all unseen notices for the requesting user as seen.  Returns a
    ``redirect`` when complete. 
    """

    if success_url is None:
        success_url = reverse("notification_notices")
    if request.GET.has_key("next"):
        success_url = request.GET['next']

    for notice in Notice.objects.notices_for(request.user, unseen=True):
        notice.unseen = False
        notice.save()

    return HttpResponseRedirect(success_url)

