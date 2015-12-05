from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r'^$', 'adminpage.views.home'),
    url(r'^list/$', 'adminpage.views.activity_list'),
    url(r'^detail/(?P<actid>\d+)/$', 'adminpage.views.activity_detail'),
    url(r'^checkin/(?P<actid>\d+)/$', 'adminpage.views.activity_checkin'),
    url(r'^checkin/(?P<actid>\d+)/check/', 'adminpage.views.activity_checkin_post'),
    url(r'^export/(?P<actid>\d+)/$', 'adminpage.views.activity_export_stunum'),
    url(r'^add/$', 'adminpage.views.activity_add'),
    url(r'^delete/$', 'adminpage.views.activity_delete'),
    url(r'^modify/$', 'adminpage.views.activity_post'),
    url(r'^login/$', 'adminpage.views.login'),
    url(r'^logout/$', 'adminpage.views.logout'),
    url(r'^order/$', 'adminpage.views.order_index'),
    url(r'^order_login/$', 'adminpage.views.order_login'),
    url(r'^order_logout/$', 'adminpage.views.order_logout'),
    url(r'^order_list/$', 'adminpage.views.order_list'),
    url(r'^print/(?P<unique_id>\S+)/$', 'adminpage.views.print_ticket'),
    url(r'^menu/adjust/$', 'adminpage.views.adjust_menu_view'),
    url(r'^menu/get/$', 'adminpage.views.custom_menu_get'),
    url(r'^menu/submit/$', 'adminpage.views.custom_menu_modify_post'),

    url(r'^vote_list/$', 'adminpage.views.vote_list'),
    url(r'^vote_detail/(?P<voteid>\d+)/$', 'adminpage.views.vote_detail'),
    url(r'^vote_add/$', 'adminpage.views.vote_add'),
    url(r'^vote_modify/$', 'adminpage.views.vote_post'),
    url(r'^vote_delete/$', 'adminpage.views.vote_delete'),
    url(r'^vote_modify_display/(?P<voteid>\d+)/$', 'adminpage.views.vote_modify_display'),
    url(r'^vote_export/(?P<voteid>\d+)/$', 'adminpage.views.vote_export'),
    url(r'^vote_statistics/(?P<voteid>\d+)/$', 'adminpage.views.vote_statistics'),
    url(r'^upload_pic/$', 'adminpage.views.upload_pic'),
)