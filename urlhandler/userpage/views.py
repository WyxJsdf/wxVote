#-*- coding:utf-8 -*-

from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from urlhandler.models import User, Activity, Ticket
from urlhandler.settings import STATIC_URL
import urllib, urllib2
import datetime
from django.utils import timezone


from userpage.safe_reverse import *
from weixinlib.settings import WEIXIN_TOKEN
from userpage.barcode import *
import json
from django.views.decorators.csrf import csrf_exempt

from weixinlib.base_support import get_access_token
from urlhandler.models import Vote, VoteItem, SingleVote
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from weixinlib.settings import WEIXIN_APPID, WEIXIN_SECRET, WEIXIN_APPID


def home(request):
    return render_to_response('mobile_base.html')


###################### Validate ######################
# request.GET['openid'] must be provided.
def validate_view(request, openid):
    if User.objects.filter(weixin_id=openid, status=1).exists():
        isValidated = 1
    else:
        isValidated = 0
    studentid = ''
    if request.GET:
        studentid = request.GET.get('studentid', '')
    return render_to_response('validation.html', {
        'openid': openid,
        'studentid': studentid,
        'isValidated': isValidated,
        'now': datetime.datetime.now() + datetime.timedelta(seconds=-5),
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


def validate_post(request):
    if (not request.POST) or (not 'openid' in request.POST) or \
            (not 'username' in request.POST) or (not 'password' in request.POST):
        raise Http404
    userid = request.POST['username']
    if not userid.isdigit():
        raise Http404
    userpass = request.POST['password'].encode('gb2312')
    validate_result = validate_through_learn(userid, userpass)
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
        act_abstract = act_text[0:MAX_LEN]+u'...'
    act_photo = activity[0].pic_url
    cur_time = timezone.now() # use the setting UTC
    act_seconds = 0
    if act_bookstart <= cur_time <= act_bookend:
        act_delta = act_bookend - cur_time
        act_seconds = act_delta.total_seconds()
        act_status = 0 # during book time
    elif cur_time < act_bookstart:
        act_delta = act_bookstart - cur_time
        act_seconds = act_delta.total_seconds()
        act_status = 1 # before book time
    else:
        act_status = 2 # after book time
    variables=RequestContext(request,{'act_name':act_name,'act_text':act_text, 'act_photo':act_photo,
                                      'act_bookstart':act_bookstart,'act_bookend':act_bookend,'act_begintime':act_begintime,
                                      'act_endtime':act_endtime,'act_totaltickets':act_totaltickets,'act_key':act_key,
                                      'act_place':act_place, 'act_status':act_status, 'act_seconds':act_seconds,'cur_time':cur_time,
                                      'act_abstract':act_abstract, 'act_text_status':act_text_status,'act_ticket_remian':act_ticket_remian})
    return render_to_response('activitydetails.html', variables)


def ticket_view(request, uid):
    ticket = Ticket.objects.filter(unique_id=uid)
    if not ticket.exists():
        raise Http404  #current activity is invalid
    activity = Activity.objects.filter(id=ticket[0].activity_id)
    act_id = activity[0].id
    act_name = activity[0].name
    act_key = activity[0].key
    act_begintime = activity[0].start_time
    act_endtime = activity[0].end_time
    act_place = activity[0].place
    ticket_status = ticket[0].status
    now = datetime.datetime.now()
    if act_endtime < now:#表示活动已经结束
        ticket_status = 3
    ticket_seat = ticket[0].seat
    act_photo = "http://115.28.212.177:6060/fit/"+uid
    variables=RequestContext(request,{'act_id':act_id, 'act_name':act_name,'act_place':act_place, 'act_begintime':act_begintime,
                                      'act_endtime':act_endtime,'act_photo':act_photo, 'ticket_status':ticket_status,
                                      'ticket_seat':ticket_seat,
                                      'act_key':act_key})
    return render_to_response('activityticket.html', variables)

def help_view(request):
    variables=RequestContext(request,{'name':u'“紫荆之声”'})
    return render_to_response('help.html', variables)


def activity_menu_view(request, actid):
    activity = Activity.objects.get(id=actid)
    return render_to_response('activitymenu.html', {'activity': activity})

def helpact_view(request):
    variables=RequestContext(request,{})
    return render_to_response('help_activity.html', variables)

def helpclub_view(request):
    variables=RequestContext(request,{})
    return render_to_response('help_club.html', variables)

def helplecture_view(request):
    variables=RequestContext(request,{})
    return render_to_response('help_lecture.html', variables)




################################## Voting #################################
# By: LiuJunlin
def vote_validate_user(request, voteid):
    url = 'https://open.weixin.qq.com/connect/oauth2/authorize?'\
              'appid=' + WEIXIN_APPID + \
              '&redirect_uri=' + s_reverse_vote_mainpage(voteid) + \
              '&response_type=code' + \
              '&scope=snsapi_base' + \
              '&state=STATE' + \
              '#wechat_redirect'

    return HttpResponseRedirect(url)


def vote_main_view(request, voteid, openid):
    '''
    if not ('code' in request.GET):
        return HttpResponseRedirect(s_reverse_vote_validate_user(voteid))
    else:
        code = request.GET['code']
        req_url = 'https://api.weixin.qq.com/sns/oauth2/access_token' + \
                   '?appid=' + WEIXIN_APPID + \
                   '&secret=' + WEIXIN_SECRET + \
                   '&code=' + code + \
                   '&grant_type=authorization_code'
        req = urllib2.Request(url=req_url)
        res_data = urllib2.urlopen(req).read()
        res_dict = json.loads(res_data)
        openid = res_dict['openid']
        users = User.objects.filter(weixin_id=openid)
        if not users.exists():
            return HttpResponseRedirect(s_reverse_validate(openid))
    '''

    vote = Vote.objects.get(id=voteid)
    voteDict = {}
    voteDict['id'] = voteid
    voteDict['name'] = vote.name
    voteDict['description'] = vote.description
    voteDict['pic_url'] = vote.pic_url
    voteDict['end_time'] = vote.end_time
    voteDict['max_num'] = vote.max_num
    voteDict['items'] = []
    voteDict['voted'] = 0

    user = User.objects.filter(weixin_id=openid)[0]
    stu_id = user.stu_id

    voteItems = VoteItem.objects.filter(vote_key=vote.key, status__gte=0)
    for item in  voteItems:
        itemDict = {}
        itemDict['name'] = item.name
        itemDict['pic_url'] = item.pic_url
        itemDict['description'] = item.description
        itemDict['vote_num'] = int(item.vote_num)
        itemDict['id'] = int(item.id)
        itemDict['voted'] = 0
        singleVotes = SingleVote.objects.filter(stu_id=stu_id, item_id=itemDict['id'])
        if singleVotes.exists():
            itemDict['voted'] = 1
            voteDict['voted'] = 1
        voteDict['items'].append(itemDict)

    return render_to_response('vote_mainpage.html', {
        'vote': voteDict,
        'openid': openid
    }, context_instance=RequestContext(request))


@csrf_exempt
def vote_user_post(request, voteid, openid):
    if not request.POST:
        raise Http404

    post = request.POST
    rtnJSON = {}

    try:
        user = User.objects.filter(weixin_id=openid)[0]
        vote = Vote.objects.get(id=voteid)
        voteItems = VoteItem.objects.filter(vote_key=vote.key, status__gte=0)

        now = datetime.datetime.now()
        if vote.end_time < now:
            rtnJSON['error'] = u'投票活动已经过了截止日期啦！'
            return HttpResponse(json.dumps(rtnJSON), content_type='application/json')

        for item in voteItems:
            singleVotes = SingleVote.objects.filter(stu_id=user.stu_id, item_id=item.id)
            if singleVotes.exists():
                rtnJSON['error'] = u'你已经投过票啦！'
                return HttpResponse(json.dumps(rtnJSON),content_type='application/json')

        items = []
        for item in voteItems:
            k = str(item.id)
            itemDict = model_to_dict(item)
            itemDict['voted'] = 0
            if (k in post) and (post[k] == 'on'):
                preVote = {}
                preVote['item_id'] = item.id
                preVote['stu_id'] = user.stu_id
                SingleVote.objects.create(**preVote)
                item.vote_num = item.vote_num + 1
                item.save()
                itemDict['vote_num'] = item.vote_num
                itemDict['voted'] = 1
            items.append(itemDict)
        rtnJSON['items'] = items
    except Exception as e:
        print 'Error occured!!!!!' + str(e)
        rtnJSON['error'] = str(e)
        return HttpResponse(json.dumps(rtnJSON), content_type='application/json')

    return HttpResponse(json.dumps(rtnJSON), content_type='application/json')


def vote_item_detail(request, itemid):
    vote = VoteItem.objects.get(id=itemid)
    voteDict = {}
    voteDict['name'] = vote.name
    voteDict['pic_url'] = vote.pic_url
    voteDict['description'] = vote.description

    return render_to_response('vote_item_detail.html', {
        'vote': voteDict,
    }, context_instance=RequestContext(request))

