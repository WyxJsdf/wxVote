from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'userpage.views.home'),
    url(r'^validate/try/$', 'userpage.views.validate_post'),
    url(r'^validate/(?P<openid>\S+)/$', 'userpage.views.validate_view'),
    url(r'^activity/(?P<activityid>\d+)/$','userpage.views.details_view'),
    url(r'^ticket/(?P<uid>\S+)/$','userpage.views.ticket_view'),
    url(r'^help/$','userpage.views.help_view'),
    url(r'^helpact/$','userpage.views.helpact_view'),
    url(r'^helpclub/$','userpage.views.helpclub_view'),
    url(r'^helplecture/$','userpage.views.helplecture_view'),
    url(r'^activity/(?P<actid>\d+)/menu/$', 'userpage.views.activity_menu_view'),

    url(r'^vote_main/(?P<voteid>\d+)/(?P<openid>[^/]+)/(?P<typeid>\d+)/$', 'userpage.views.vote_main_redirect_old'),
    url(r'^vote_main/(?P<voteid>\d+)/(?P<typeid>\d+)$', 'userpage.views.vote_main_view'),
    url(r'^vote_post/(?P<voteid>\d+)$', 'userpage.views.vote_post'),
    url(r'^vote_item_detail/(?P<itemid>\d+)/$', 'userpage.views.vote_item_detail'),
    url(r'^set_openid/(?P<openid>\S+)/redirect=(?P<url>.+)$', 'userpage.views.set_session'),
    url(r'^clean_session/redirect=(?P<url>.+)$', 'userpage.views.clean_session'),
    )