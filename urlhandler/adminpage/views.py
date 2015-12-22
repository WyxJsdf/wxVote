#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.forms.models import model_to_dict
from datetime import datetime
import json
import time
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import F
import urllib
import urllib2
from urlhandler.models import Activity, Ticket
from urlhandler.models import User as Booker
from weixinlib.custom_menu import get_custom_menu, modify_custom_menu, add_new_custom_menu, auto_clear_old_menus
from weixinlib.settings import get_custom_menu_with_book_acts, WEIXIN_BOOK_HEADER
from adminpage.safe_reverse import *

import xlwt
import re
from django.utils.http import urlquote
from django.utils.encoding import smart_str

from urlhandler.models import Vote, VoteItem, SingleVote
from datetime import timedelta
from PIL import Image
from queryhandler.settings import SITE_DOMAIN



@csrf_protect
def home(request):
    if not request.user.is_authenticated():
        return render_to_response('login.html', context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(s_reverse_vote_list())


def activity_list(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    actmodels = Activity.objects.filter(status__gte=0).order_by('-id').all()
    activities = []
    for act in actmodels:
        activities += [wrap_activity_dict(act)]
    permission_num = 1 if request.user.is_superuser else 0
    return render_to_response('activity_list.html', {
        'activities': activities,
        'permission': permission_num,
    })


def activity_checkin(request, actid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())
    try:
        activity = Activity.objects.get(id=actid)
        if datetime.now() > activity.end_time:
            raise 'Time out!'
    except:
        return HttpResponseRedirect(s_reverse_activity_list())

    return render_to_response('activity_checkin.html', {
        'activity': activity,
    }, context_instance=RequestContext(request))


def activity_checkin_post(request, actid):
    if (not request.POST) or (not ('uid' in request.POST)):
        raise Http404
    try:
        activity = Activity.objects.get(id=actid)
    except:
        return HttpResponse(json.dumps({'result': 'error', 'stuid': 'Unknown', 'msg': 'noact'}),
                            content_type='application/json')

    rtnJSON = {'result': 'error', 'stuid': 'Unknown', 'msg': 'rejected'}
    flag = False
    uid = request.POST['uid']
    if len(uid) == 10:
        if not uid.isdigit():
            rtnJSON['result'] = 'error'
            rtnJSON['stuid'] = 'Unknown'
            rtnJSON['msg'] = 'rejected'
            flag = True
        if not flag:
            rtnJSON['stuid'] = uid
            try:
                student = Booker.objects.get(stu_id=uid, status=1)
            except Exception as e:
                rtnJSON['msg'] = 'nouser'
                flag = True
            if not flag:
                try:
                    ticket = Ticket.objects.get(stu_id=student.stu_id, activity=activity)
                    if ticket.status == 0:
                        raise 'noticket'
                    elif ticket.status == 2:
                        rtnJSON['result'] = 'warning'
                        rtnJSON['msg'] = 'used'
                        flag = True
                    elif ticket.status == 1:
                        ticket.status = 2
                        ticket.save()
                        rtnJSON['msg'] = 'accepted'
                        rtnJSON['result'] = 'success'
                        flag = True
                except:
                    rtnJSON['msg'] = 'noticket'
                    flag = True
    elif len(uid) == 32:
        try:
            ticket = Ticket.objects.get(unique_id=uid, activity=activity)
            if ticket.status == 0:
                raise 'rejected'
            elif ticket.status == 2:
                rtnJSON['msg'] = 'used'
                rtnJSON['stuid'] = ticket.stu_id
                rtnJSON['result'] = 'warning'
                flag = True
            else:
                ticket.status = 2
                ticket.save()
                rtnJSON['result'] = 'success'
                rtnJSON['stuid'] = ticket.stu_id
                rtnJSON['msg'] = 'accepted'
                flag = True
        except:
            rtnJSON['result'] = 'error'
            rtnJSON['stuid'] = 'Unknown'
            rtnJSON['msg'] = 'rejected'
            flag = True

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def login(request):
    if not request.POST:
        raise Http404

    rtnJSON = {}

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        rtnJSON['message'] = 'success'
        rtnJSON['next'] = s_reverse_vote_list()
    else:
        time.sleep(2)
        rtnJSON['message'] = 'failed'
        if User.objects.filter(username=username, is_active=True):
            rtnJSON['error'] = 'wrong'
        else:
            rtnJSON['error'] = 'none'

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(s_reverse_admin_home())


def str_to_datetime(strg):
    return datetime.strptime(strg, '%Y-%m-%d %H:%M:%S')


def activity_create(activity):
    preDict = dict()
    for k in ['name', 'key', 'description', 'place', 'pic_url', 'seat_status', 'total_tickets']:
        preDict[k] = activity[k]
    for k in ['start_time', 'end_time', 'book_start', 'book_end']:
        preDict[k] = str_to_datetime(activity[k])
    preDict['status'] = 1 if ('publish' in activity) else 0
    preDict['remain_tickets'] = preDict['total_tickets']
    newact = Activity.objects.create(**preDict)
    return newact


def activity_modify(activity):
    nowact = Activity.objects.get(id=activity['id'])
    now = datetime.now()
    if nowact.status == 0:
        keylist = ['name', 'key', 'description', 'place', 'pic_url', 'seat_status', 'total_tickets']
        timelist = ['start_time', 'end_time', 'book_start', 'book_end']
    elif nowact.status == 1:
        if now >= nowact.start_time:
            keylist = ['description', 'pic_url']
            timelist = ['start_time', 'end_time']
        elif now >= nowact.book_start:
            keylist = ['description', 'place', 'pic_url']
            timelist = ['start_time', 'end_time', 'book_end']
        else:
            keylist = ['description', 'place', 'pic_url', 'seat_status', 'total_tickets']
            timelist = ['start_time', 'end_time', 'book_end']
    else:
        keylist = []
        timelist = []
    for key in keylist:
        if key == 'total_tickets':
            setattr(nowact, 'remain_tickets', activity[key])
        setattr(nowact, key, activity[key])
    for key in timelist:
        setattr(nowact, key, str_to_datetime(activity[key]))
    if (nowact.status == 0) and ('publish' in activity):
        nowact.status = 1
    nowact.save()
    return nowact


@csrf_exempt
def activity_delete(request):
    requestdata = request.POST
    if not requestdata:
        raise Http404
    curact = Activity.objects.get(id=requestdata.get('activityId', ''))
    curact.status = -1
    curact.save()
    #删除后刷新界面
    return HttpResponse('OK')


def get_checked_tickets(activity):
    return Ticket.objects.filter(activity=activity, status=2).count()


def wrap_activity_dict(activity):
    dt = model_to_dict(activity)
    if (dt['status'] >= 1) and (datetime.now() >= dt['book_start']):
        dt['tickets_ready'] = 1
        dt['ordered_tickets'] = int(activity.total_tickets) - int(activity.remain_tickets)
        dt['checked_tickets'] = get_checked_tickets(activity)
    return dt


def activity_add(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    return render_to_response('activity_detail.html', {
        'activity': {
            'name': u'新建活动',
        }
    }, context_instance=RequestContext(request))


def activity_detail(request, actid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    try:
        activity = Activity.objects.get(id=actid)

        unpublished = (activity.status == 0)
    except:
        raise Http404
    return render_to_response('activity_detail.html', {
        'activity': wrap_activity_dict(activity),
        'unpublished': unpublished
    }, context_instance=RequestContext(request))


class DatetimeJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def activity_post(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    if not request.POST:
        raise Http404
    post = request.POST
    rtnJSON = dict()
    try:
        if 'id' in post:
            activity = activity_modify(post)
        else:
            iskey = Activity.objects.filter(key=post['key'])
            if iskey:
                now = datetime.now()
                for keyact in iskey:
                    if now < keyact.end_time:
                        rtnJSON['error'] = u"当前有活动正在使用该活动代称"
                        return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder),
                                            content_type='application/json')
            activity = activity_create(post)
            rtnJSON['updateUrl'] = s_reverse_activity_detail(activity.id)
        rtnJSON['activity'] = wrap_activity_dict(activity)
        ### deleted by xiaohe ###
        #if 'publish' in post:
        #    updateErr = json.loads(add_new_custom_menu(name=activity.key, key=WEIXIN_BOOK_HEADER + str(activity.id))).get('errcode', 'err')
        #    if updateErr != 0:
        #        rtnJSON['error'] = u'活动创建成功，但更新微信菜单失败，请手动更新:(  \r\n错误代码：%s' % updateErr
       ### end by xiaohe ####
    except Exception as e:
        rtnJSON['error'] = str(e)
    return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder), content_type='application/json')


def order_index(request):
    return render_to_response('print_login.html', context_instance=RequestContext(request))


def order_login(request):
    if not request.POST:
        raise Http404

    rtnJSON = {}

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    try:
        Booker.objects.get(stu_id=username)
    except:
        rtnJSON['message'] = 'none'
        return HttpResponse(json.dumps(rtnJSON), content_type='application/json')

    req_data = urllib.urlencode({'userid': username, 'userpass': password, 'submit1': u'登录'.encode('gb2312')})
    request_url = 'https://learn.tsinghua.edu.cn/MultiLanguage/lesson/teacher/loginteacher.jsp'
    req = urllib2.Request(url=request_url, data=req_data)
    res_data = urllib2.urlopen(req)

    try:
        res = res_data.read()
    except:
        raise Http404

    if 'loginteacher_action.jsp' in res:
        request.session['stuid'] = username
        request.session.set_expiry(0)
        rtnJSON['message'] = 'success'
        rtnJSON['next'] = s_reverse_order_list()
    else:
        rtnJSON['message'] = 'failed'

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def order_logout(request):
    return HttpResponseRedirect(s_reverse_order_index())


def order_list(request):

    if not 'stuid' in request.session:
        return HttpResponseRedirect(s_reverse_order_index())

    stuid = request.session['stuid']

    orders = []
    qset = Ticket.objects.filter(stu_id = stuid)

    for x in qset:
        item = {}

        activity = Activity.objects.get(id = x.activity_id)

        item['name'] = activity.name

        item['start_time'] = activity.start_time

        item['end_time'] = activity.end_time
        item['place'] = activity.place
        item['seat'] = x.seat
        item['valid'] = x.status
        item['unique_id'] = x.unique_id
        orders.append(item)

    return render_to_response('order_list.html', {
        'orders': orders,
        'stuid':stuid
    }, context_instance=RequestContext(request))


def print_ticket(request, unique_id):

    if not 'stuid' in request.session:
        return HttpResponseRedirect(s_reverse_order_index())

    try:
        ticket = Ticket.objects.get(unique_id = unique_id)
        activity = Activity.objects.get(id = ticket.activity_id)
        qr_addr = "http://115.28.212.177:6060/fit/" + unique_id
    except:
        raise Http404

    return render_to_response('print_ticket.html', {
        'qr_addr': qr_addr,
        'activity': activity,
        'stu_id':ticket.stu_id
    }, context_instance=RequestContext(request))


def adjust_menu_view(request):
    return False
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())
    if not request.user.is_superuser:
        return HttpResponseRedirect(s_reverse_activity_list())
    activities = Activity.objects.filter(end_time__gt=datetime.now(), status=1)
    return render_to_response('adjust_menu.html', {
        'activities': activities,
    }, context_instance=RequestContext(request))


def custom_menu_get(request):
    return False
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())
    if not request.user.is_superuser:
        return HttpResponseRedirect(s_reverse_activity_list())
    custom_buttons = get_custom_menu()
    current_menu = []
    for button in custom_buttons:
        sbtns = button.get('sub_button', [])
        if len(sbtns) > 0:
            tmpkey = sbtns[0].get('key', '')
            if (not tmpkey.startswith(WEIXIN_BOOK_HEADER + 'W')) and tmpkey.startswith(WEIXIN_BOOK_HEADER):
                current_menu = sbtns
                break
    if auto_clear_old_menus(current_menu):
        modify_custom_menu(json.dumps(get_custom_menu_with_book_acts(current_menu), ensure_ascii=False).encode('utf8'))
    wrap_menu = []
    for menu in current_menu:
        wrap_menu += [{
                          'name': menu['name'],
                          'id': int(menu['key'].split('_')[-1]),
                      }]
    return HttpResponse(json.dumps(wrap_menu), content_type='application/json')


def custom_menu_modify_post(request):
    ### add by xiaohe###
    raise Http404
    ### end by xiaohe ##
    if not request.user.is_authenticated():
        raise Http404
    if not request.user.is_superuser:
        raise Http404
    if not request.POST:
        raise Http404
    if not 'menus' in request.POST:
        raise Http404
    menus = json.loads(request.POST.get('menus', ''))
    sub_button = []
    for menu in menus:
        sub_button += [{
                           'type': 'click',
                           'name': menu['name'],
                           'key': 'TSINGHUA_BOOK_' + str(menu['id']),
                           'sub_button': [],
                       }]
    return HttpResponse(modify_custom_menu(json.dumps(get_custom_menu_with_book_acts(sub_button), ensure_ascii=False).encode('utf8')),
                        content_type='application/json')


def activity_export_stunum(request, actid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())
    try:
        activity = Activity.objects.get(id=actid)
    except:
        raise Http404

    tickets = Ticket.objects.filter(activity=activity)
    wb = xlwt.Workbook()

    def write_row(ws, row, data):
        for index, cell in enumerate(data):
            ws.write(row, index, cell)

    ws = wb.add_sheet(activity.name)
    row = 1
    write_row(ws, 0, [u'学号', u'状态', u'座位'])
    statusMap = [u'已取消', u'未入场', u'已入场']
    for ticket in tickets:
        write_row(ws, row, [ticket.stu_id, statusMap[ticket.status], ticket.seat])
        row = row + 1

    ##########################################定义Content-Disposition，让浏览器能识别，弹出下载框
    fname = 'activity' + actid + '.xls'
    agent=request.META.get('HTTP_USER_AGENT')
    if agent and re.search('MSIE',agent):
        response = HttpResponse(content_type="application/vnd.ms-excel")  # 解决ie不能下载的问题
        response['Content-Disposition'] = 'attachment; filename=%s' % urlquote(fname)  # 解决文件名乱码/不显示的问题
    else:
        response = HttpResponse(content_type="application/ms-excel")  # 解决ie不能下载的问题
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(fname)  # 解决文件名乱码/不显示的问题
    ##########################################保存

    wb.save(response)
    return response




################################## Voting #################################
# By: Liu Junlin
def vote_add(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    return render_to_response('vote_detail.html', {
        'vote': {
            'name': u'新增投票'
        }
    }, context_instance=RequestContext(request))


def vote_list(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    vote_models = Vote.objects.filter(status__gte=0).order_by("-id").all()
    votes = []

    for vote in vote_models:
        votes += [wrap_vote_dict(vote)]
    print(votes)
    return render_to_response('vote_list.html', {
        'votes':votes
    }, context_instance=RequestContext(request))


def wrap_vote_dict(vote):
    dt = model_to_dict(vote)
    dt['id'] = vote.id
    return dt


def get_vote_items(vote):
    ret = []
    vote_items = VoteItem.objects.filter(vote_key=vote.key, status__gte=0)
    for item in vote_items:
        dict = {}
        dict['name'] = item.name
        dict['pic_url'] = item.pic_url
        dict['description_simply'] = item.description_simply
        dict['description'] = item.description
        dict['vote_num'] = int(item.vote_num)
        ret.append(dict)
    return ret


def vote_detail(request, voteid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    try:
        vote = Vote.objects.get(id=voteid)
        unpublished = (vote.status == 0)
        voteDict = wrap_vote_dict(vote)
        voteDict['items'] = get_vote_items(vote)
    except:
        raise Http404

    return render_to_response('vote_detail.html', {
        'vote': voteDict,
        'unpublished': unpublished
    }, context_instance=RequestContext(request))


def vote_post(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    if not request.POST:
        raise Http404

    post = request.POST
    rtnJSON = {}

    try:
        if 'id' in post:
            vote = vote_modify(post)
        else:
            iskey = Vote.objects.filter(key=post['key'])
            if iskey:
                now = datetime.now()
                for keyvote in iskey:
                    if now < keyvote.end_time:
                        rtnJSON['error'] = u"当前有投票活动正在使用该活动代称"
                        return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder),
                                            content_type='application/json')
            vote = vote_create(post)
            # rtnJSON['updateUrl'] = s_reverse_activity_detail(activity.id)
        voteDict = wrap_vote_dict(vote)
        voteDict['items'] = get_vote_items(vote)
        rtnJSON['vote'] = voteDict
    except Exception as e:
        print str(e)
        rtnJSON['error'] = str(e)

    return HttpResponse(json.dumps(rtnJSON, cls=DatetimeJsonEncoder), content_type='application/json')


def vote_modify(vote):
    curVote = Vote.objects.get(id=vote['id'])
    old_start_time = curVote.start_time

    for k in ['name', 'pic_url', 'description', 'background']:
        setattr(curVote, k, vote[k])

    for k in ['max_num', 'layout_style', 'has_images', 'vote_type']:
        setattr(curVote, k, int(vote[k]))
    now = datetime.now()
    if now < old_start_time:
        setattr(curVote, 'start_time', str_to_datetime(vote['start_time']))
    setattr(curVote, 'end_time', str_to_datetime(vote['end_time']))

    if 'publish' in vote:
        setattr(curVote, 'status', 1)
    else:
        setattr(curVote, 'status', 0)
    
    curVote.save()

    if (now < old_start_time):
        vote_item_delete(curVote.key)
        vote_item_create(vote, curVote)
    else:
        vote_item_modify(vote, curVote)
    return curVote


def vote_item_create(vote, newVote):
    item_num = int(vote['item_num'])
    for j in range(1, item_num + 1):
        preItem = {}
        for k in ['name', 'pic_url', 'description', 'description_simply']:
            preItem[k] = vote[k + str(j)]
        preItem['vote'] = newVote
        preItem['vote_key'] = newVote.key
        preItem['vote_num'] = 0
        preItem['status'] = newVote.status
        VoteItem.objects.create(**preItem)


def vote_item_modify(vote, newVote):
    voteItems = VoteItem.objects.filter(vote_key=newVote.key, status__gte=0)
    count = 0
    for item in voteItems:
        count = count + 1
        for k in ['name', 'pic_url', 'description', 'description_simply']:
            setattr(item, k, vote[k + str(count)])
        item.save()


def vote_create(vote):
    preVote = {}
    for k in ['name', 'key', 'description', 'pic_url', 'background']:
        preVote[k] = vote[k]
    for k in ['max_num', 'layout_style', 'has_images', 'vote_type']:
        preVote[k] = int(vote[k])
    for k in ['start_time', 'end_time']:
        preVote[k] = str_to_datetime(vote[k])
    preVote['status'] = 1 if ('publish' in vote) else 0
    preVote['display'] = 1
    newVote = Vote.objects.create(**preVote)

    vote_item_create(vote, newVote)

    return newVote


@csrf_exempt
def vote_delete(request):
    if not request.POST:
        raise Http404

    try:
        post = request.POST
        vote = Vote.objects.get(id=post.get('voteId', ''))
        vote.status = -1
        vote.save()
        vote_item_delete(vote.key)
    except Exception as e:
        print str(e)

    return HttpResponse('ok')


def vote_item_delete(key):
    vote_items = VoteItem.objects.filter(vote_key=key, status__gte=0)
    if vote_items.exists():
        for item in vote_items:
            item.status = -1
            item.save()


@csrf_exempt
def vote_modify_display(request, voteid):
    try:
        vote = Vote.objects.get(id=voteid)
        vote.display = 1 - vote.display
        vote.save()
    except Exception as e:
        print str(e)

    return HttpResponseRedirect(s_reverse_vote_list())


def vote_export(request, voteid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())
    try:
        vote = Vote.objects.get(id=voteid)
    except:
        raise Http404

    wb = xlwt.Workbook()
    ws1 = wb.add_sheet(u'投票排名')
    ws2 = wb.add_sheet(u'支持者情况')

    def write_row(ws, row, data):
        for index, content in enumerate(data):
            ws.write(row, index, content)

    voteItems = VoteItem.objects.filter(vote_key=vote.key, status=1).order_by('-vote_num')

    total_votes = 0
    for item in voteItems:
        total_votes += item.vote_num

    write_row(ws1, 0, [u'投票项名称', u'得票数', u'得票数占总票数百分比'])
    for index, item in enumerate(voteItems):
        if total_votes != 0:
            res = round(float(item.vote_num) / total_votes * 100, 2)
        else:
            res = 0
        write_row(ws1, index + 1, [item.name, item.vote_num, str(res) + '%'])

    row = 0
    for item in voteItems:
        write_row(ws2, row, [item.name, u'投票人学号', u'投票时间'])
        row = row + 1
        singleVotes = SingleVote.objects.filter(item_id=item.id, status=1)
        for sv in singleVotes:
            write_row(ws2, row, ['', sv.stu_id, str(sv.time)])
            row = row + 1
        write_row(ws2, row, [''])
        row = row + 1

    fname = vote.name + '.xls'
    agent=request.META.get('HTTP_USER_AGENT')
    if agent and re.search('MSIE',agent):
        response = HttpResponse(content_type="application/vnd.ms-excel")  # 解决ie不能下载的问题
        response['Content-Disposition'] = 'attachment; filename=%s' % urlquote(fname)  # 解决文件名乱码/不显示的问题
    else:
        response = HttpResponse(content_type="application/ms-excel")  # 解决ie不能下载的问题
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(fname)  # 解决文件名乱码/不显示的问题

    wb.save(response)
    return response


def vote_statistics(request, voteid):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    vote = Vote.objects.get(id=voteid)
    voteItems = VoteItem.objects.filter(vote_key=vote.key, status=1)

    total_votes = 0
    for item in voteItems:
        total_votes  = total_votes + item.vote_num

    voteDict = {}
    voteDict['name'] = vote.name
    voteDict['items'] = []
    for item in voteItems:
        itemDict = {}
        itemDict['vote_num'] = item.vote_num
        if total_votes != 0:
            itemDict['percent'] = float(item.vote_num) / total_votes
        else:
            itemDict['percent'] = 0
        itemDict['name'] = item.name
        voteDict['items'].append(itemDict)

    gap = (vote.end_time - vote.start_time) / 20
    voteDict['times'] = []
    for i in range(1, 21):
        t1 = vote.start_time + gap * (i - 1)
        t2 = vote.start_time + gap * i
        timeDict = {}
        timeDict['interval'] = str(t1) + '~' + str(t2)
        count = 0
        for item in voteItems:
            singleVotes = SingleVote.objects.filter(item_id=item.id, time__gte=t1, time__lte=t2, status=1)
            count = count + len(singleVotes)
        timeDict['height'] = count
        voteDict['times'].append(timeDict)

    return render_to_response('vote_statistics.html', {
        'vote': voteDict,
    }, context_instance=RequestContext(request))


def upload_pic(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    if not request.POST:
        raise Http404

    rtnJSON = {}
    try:
        if 'upfile' in request.FILES:
            filename = request.FILES['upfile']
        else:
            filename = ''
        optionIndex = request.POST.get('optionIndex', '')
        if filename:
            try:
                img = Image.open(filename)
            except Exception as e:
                rtnJSON['responseText'] = u'图片格式错误!'
                return HttpResponse(json.dump(rtnJSON), content_type='application/json')
            w, h = img.size
            if w < h:
                img.thumbnail((200, (h * 200 / w), Image.ANTIALIAS))
            else:
                img.thumbnail((w * 200 / h, 200), Image.ANTIALIAS)
            name = filename.__str__()
            index = name.find('.')
            name = name[:index] + str(optionIndex) + name[index:]
            img.save("urlhandler/userpage/static/img/" + name, img.format)
            rtnJSON['responseText'] = SITE_DOMAIN + "/static1/img/" + name
            return HttpResponse(json.dumps(rtnJSON), content_type='application/json')
        else:
            rtnJSON['responseText'] = u'图片名为空'
            return HttpResponse(json.dumps(rtnJSON), content_type='application/json')
    except Exception as e:
        print str(e)
        rtnJSON['responseText'] = str(e)
        return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def modify_pic(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(s_reverse_admin_home())

    if not request.POST:
        raise Http404

    rtnJSON = {}
    try:
        x1 = request.POST.get('x1', '')
        y1 = request.POST.get('y1', '')
        x2 = request.POST.get('x2', '')
        y2 = request.POST.get('y2', '')
        w = request.POST.get('w', '')
        h = request.POST.get('h', '')
        filename = request.POST.get('picfilename', '')
        if filename and x1 and x2 and y1 and y2 and w and h:
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            try:
                img = Image.open("urlhandler/userpage/static/img/" + filename)
            except Exception as e:
                rtnJSON['responseText'] = u'打开图片失败！'
                return HttpResponse(json.dump(rtnJSON), content_type='application/json')
            box = (x1, y1, x2, y2)
            img.crop(box).save("urlhandler/userpage/static/img/" + filename.__str__(), img.format)
            rtnJSON['responseText'] = SITE_DOMAIN + "/static1/img/" + filename.__str__()
            return HttpResponse(json.dumps(rtnJSON), content_type='application/json')
        else:
            rtnJSON['responseText'] = u'未获取到图片信息！'
            return HttpResponse(json.dumps(rtnJSON), content_type='application/json')
    except Exception as e:
        print str(e)
        rtnJSON['responseText'] = str(e)
        return HttpResponse(json.dumps(rtnJSON), content_type='application/json')

