from django.core.urlresolvers import reverse
from queryhandler.settings import SITE_DOMAIN

def s_reverse_admin_home():
    return SITE_DOMAIN + reverse('adminpage.views.home')


def s_reverse_activity_list():
    return SITE_DOMAIN + reverse('adminpage.views.activity_list')


def s_reverse_activity_checkin(actid):
    return SITE_DOMAIN + reverse('adminpage.views.activity_checkin', kwargs={'actid': actid})


def s_reverse_activity_checkin_post(actid):
    return SITE_DOMAIN + reverse('adminpage.views.activity_checkin_post', kwargs={'actid': actid})


def s_reverse_admin_login_post():
    return SITE_DOMAIN + reverse('adminpage.views.login')


def s_reverse_admin_logout():
    return SITE_DOMAIN + reverse('adminpage.views.logout')


def s_reverse_activity_delete():
    return SITE_DOMAIN + reverse('adminpage.views.activity_delete')


def s_reverse_activity_add():
    return SITE_DOMAIN + reverse('adminpage.views.activity_add')


def s_reverse_activity_detail(actid):
    return SITE_DOMAIN + reverse('adminpage.views.activity_detail', kwargs={'actid': actid})


def s_reverse_activity_post():
    return SITE_DOMAIN + reverse('adminpage.views.activity_post')


def s_reverse_order_index():
    return SITE_DOMAIN + reverse('adminpage.views.order_index')


def s_reverse_order_login():
    return SITE_DOMAIN + reverse('adminpage.views.order_login')


def s_reverse_order_logout():
    return SITE_DOMAIN + reverse('adminpage.views.order_logout')


def s_reverse_order_list():
    return SITE_DOMAIN + reverse('adminpage.views.order_list')


def s_reverse_print_ticket(unique_id):
    return SITE_DOMAIN + reverse('adminpage.views.print_ticket', kwargs={'unique_id': unique_id})


def s_reverse_adjust_menu():
    return SITE_DOMAIN + reverse('adminpage.views.adjust_menu_view')


def s_reverse_get_menu():
    return SITE_DOMAIN + reverse('adminpage.views.custom_menu_get')


def s_reverse_modify_menu():
    return SITE_DOMAIN + reverse('adminpage.views.custom_menu_modify_post')


def s_reverse_vote_list():
    return SITE_DOMAIN + reverse('adminpage.views.vote_list')

