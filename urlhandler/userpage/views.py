# -*- coding:utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from urlhandler.models import User, Activity, Ticket
from urlhandler.settings import STATIC_URL
import urllib, urllib2
import datetime
from django.utils import timezone
from userpage.safe_reverse import *


def home(request):
    return render_to_response('mobile_base.html')


# Get timestamp and return it to front end
# Recently Modified by: Liu Junlin
# Date: 2014-11-17 16:32
def get_timestamp():
    req_url = 'http://auth.igeek.asia/v1/time'
    req = urllib2.Request(url=req_url)
    res_data = urllib2.urlopen(req)
    return res_data.read()


# Get two-dimensional barcodes from weixin server
def get_2D_barcodes(key):
    img_url = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=' + str(key)
    return img_url


###################### Validate ######################
# request.GET['openid'] must be provided.
def validate_view(request, openid):
    timestamp = get_timestamp()

    if User.objects.filter(weixin_id=openid, status=1).exists():
        isValidated = 1
    else:
        isValidated = 0
    studentid = ''
    if request.GET:
        studentid = request.GET.get('studentid', '')
    return render_to_response('validation_student.html', {
        'openid': openid,
        'studentid': studentid,
        'isValidated': isValidated,
        'now': datetime.datetime.now() + datetime.timedelta(seconds=-5),
        'timestamp': timestamp
    }, context_instance=RequestContext(request))


# Validate Format:
# METHOD 1: learn.tsinghua
# url: https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp
# form: { userid:2011013236, userpass:***, submit1: 登录 }
# success: check substring 'loginteacher_action.jsp'
# validate: userid is number
def validate_through_learn(userid, userpass):
    req_data = urllib.urlencode({'userid': userid, 'userpass': userpass, 'submit1': u'登录'.encode('gb2312')})
    request_url = 'https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp'
    req = urllib2.Request(url=request_url, data=req_data)
    res_data = urllib2.urlopen(req)
    try:
        res = res_data.read()
    except:
        return 'Error'
    if 'loginteacher_action.jsp' in res:
        return 'Accepted'
    else:
        return 'Rejected'


# METHOD 2 is not valid, because student.tsinghua has not linked to Internet
# METHOD 2: student.tsinghua
# url: http://student.tsinghua.edu.cn/checkUser.do?redirectURL=%2Fqingxiaotuan.do
# form: { username:2011013236, password:encryptedString(***) }
# success: response response is null / check response status code == 302
# validate: username is number
def validate_through_student(userid, userpass):
    return 'Error'


# Function: To validate student number through AuthTHU provided by Chen Huarong
# Recently Modified by: Liu Junlin
# Date: 2014-11-17 16:32
def validate_through_auth(userpass):
    req_url = 'http://auth.igeek.asia/v1'
    req_data = urllib.urlencode({'secret': userpass})
    req = urllib2.Request(url=req_url, data=req_data)
    res_data = urllib2.urlopen(req).read()
    res_dict = eval(res_data)
    if res_dict['code'] == 0:
        return 'Accepted'
    else:
        return 'Rejected'


# Recently Modified by: Liu Junlin
# Date: 2014-11-17 16:32
def validate_post(request):
    if (not request.POST) or (not 'openid' in request.POST) or \
            (not 'username' in request.POST) or (not 'password' in request.POST):
        raise Http404
    userid = request.POST['username']
    if not userid.isdigit():
        raise Http404
    # userpass = request.POST['password'].encode('gb2312')
    # validate_result = validate_through_learn(userid, userpass)
    userpass = request.POST['password']
    validate_result = validate_through_auth(userpass)
    if validate_result == 'Accepted':
        openid = request.POST['openid']
        try:
            User.objects.filter(stu_id=userid).update(status=0)
            User.objects.filter(weixin_id=openid).update(status=0)
        except:
            return HttpResponse('Error')
        try:
            currentUser = User.objects.get(stu_id=userid)
            currentUser.weixin_id = openid
            currentUser.status = 1
            try:
                currentUser.save()
            except:
                return HttpResponse('Error')
        except:
            try:
                newuser = User.objects.create(weixin_id=openid, stu_id=userid, status=1)
                newuser.save()
            except:
                return HttpResponse('Error')
    return HttpResponse(validate_result)


###################### Activity Detail ######################

def details_view(request, activityid):
    activity = Activity.objects.filter(id=activityid)
    if not activity.exists():
        raise Http404  #current activity is invalid
    act_name = activity[0].name
    act_key = activity[0].key
    act_place = activity[0].place
    act_bookstart = activity[0].book_start
    act_bookend = activity[0].book_end
    act_begintime = activity[0].start_time
    act_endtime = activity[0].end_time
    act_totaltickets = activity[0].total_tickets
    act_text = activity[0].description
    act_ticket_remian = activity[0].remain_tickets
    act_abstract = act_text
    MAX_LEN = 256
    act_text_status = 0
    if len(act_text) > MAX_LEN:
        act_text_status = 1
        act_abstract = act_text[0:MAX_LEN] + u'...'
    act_photo = activity[0].pic_url
    cur_time = timezone.now()  # use the setting UTC
    act_seconds = 0
    if act_bookstart <= cur_time <= act_bookend:
        act_delta = act_bookend - cur_time
        act_seconds = act_delta.total_seconds()
        act_status = 0  # during book time
    elif cur_time < act_bookstart:
        act_delta = act_bookstart - cur_time
        act_seconds = act_delta.total_seconds()
        act_status = 1  # before book time
    else:
        act_status = 2  # after book time
    variables = RequestContext(request, {'act_name': act_name, 'act_text': act_text, 'act_photo': act_photo,
                                         'act_bookstart': act_bookstart, 'act_bookend': act_bookend,
                                         'act_begintime': act_begintime,
                                         'act_endtime': act_endtime, 'act_totaltickets': act_totaltickets,
                                         'act_key': act_key,
                                         'act_place': act_place, 'act_status': act_status, 'act_seconds': act_seconds,
                                         'cur_time': cur_time,
                                         'act_abstract': act_abstract, 'act_text_status': act_text_status,
                                         'act_ticket_remian': act_ticket_remian})
    return render_to_response('activitydetails.html', variables)


def ticket_view(request, uid):
    ticket = Ticket.objects.filter(unique_id=uid)
    if not ticket.exists():
        raise Http404  #current activity is invalid
    activity = Activity.objects.filter(id=ticket[0].activity_id)
    act_id = activity[0].id
    act_uid = uid
    act_name = activity[0].name
    act_key = activity[0].key
    act_begintime = activity[0].start_time
    act_endtime = activity[0].end_time
    act_place = activity[0].place
    ticket_status = ticket[0].status
    now = datetime.datetime.now()
    if act_endtime < now:  #表示活动已经结束
        ticket_status = 3
    ticket_seat = ticket[0].seat
    # act_photo = "http://qr.ssast.org/fit/"+uid
    # act_photo = get_2D_barcodes(ticket[0].barcode_key)
    print '******** %s' % uid
    act_photo = "http://qr.ssast.org/fit/" + uid
    #act_photo = get_2D_barcodes(ticket[0].barcode_key)
    #mainmenu = s_safe_reverse_seat_mainmenu(uid)
    variables = RequestContext(request, {'uid': uid,
                                         'act_id': act_id,
                                         'act_name': act_name,
                                         'act_place': act_place,
                                         'act_begintime': act_begintime,
                                         'act_endtime': act_endtime,
                                         'act_photo': act_photo,
                                         'ticket_status': ticket_status,
                                         'ticket_seat': ticket_seat,
                                         'act_key': act_key})
    return render_to_response('activityticket.html', variables)


# context = {'abd':2, 'mainmenu':mainmenu,'act_uid':act_uid,'act_id':act_id, 'act_name':act_name,'act_place':act_place, 'act_begintime':act_begintime,'act_endtime':act_endtime,'act_photo':act_photo, 'ticket_status':ticket_status,'ticket_seat':ticket_seat,'act_key':act_key}
# print '#######'
# return render_to_response('activityticket.html', context, context_instance=RequestContext(request))

def help_views(request):
    variables = RequestContext(request, {'name': u'“紫荆之声”'})
    return render_to_response('help.html', variables)


def activity_menu_view(request, actid):
    activity = Activity.objects.get(id=actid)
    return render_to_response('activitymenu.html', {'activity': activity})


def helpact_view(request):
    variables = RequestContext(request, {})
    return render_to_response('help_activity.html', variables)


def helpclub_view(request):
    variables = RequestContext(request, {})
    return render_to_response('help_club.html', variables)


def helplecture_view(request):
    variables = RequestContext(request, {})
    return render_to_response('help_lecture.html', variables)


#一下为选座view部分，尚未添加处理--刘博格,刘峻琳

def seat_mainmenu_view(request):
    print 'aaaaaaaaaaaaaaaaaaaaaa'
    # variables=RequestContext(request,{'uid':uid})
    variables = RequestContext(request, {})
    return render_to_response('seat_mainmenu.html', variables)


def seat_submenu(request, uid, block_id):
    # variables = RequestContext(request, {'uid': uid, 'block_id': block_id})
    return render_to_response('seat_submenu.html', {
        'uid':uid,
        'block_id':block_id
    })