#-*- coding:utf-8 -*-

WEIXIN_TOKEN = 'F8ZFW1Cyzr5z6nNoJ5uZhA8iXEbe1hvX'

WEIXIN_APPID = 'wxb2545ef150be8096'

WEIXIN_SECRET = '8416b20564e9430bfe5a7c3fd88016f2'

WEIXIN_EVENT_KEYS = {
    'info_activity': 'V1001_TODAT_ACTIVE',
    'info_lecture': 'V1001_TODAT_LECTURE',
    'info_news': 'V1001_SCHOOL_NEWS',
    'info_organization': 'V1001_OGNIZATION',
    'ticket_book_what': 'TSINGHUA_BOOK_WHAT',
    'ticket_book_tmp':'BOOK_TMP',
    'ticket_get': 'TSINGHUA_TICKET',
    'account_bind': 'TSINGHUA_BIND',
    'help': 'TSINGHUA_HELP',
    'ticket_no_book_recommand': 'TSINGHUA_NO_BOOK_ACTS',
    'ticket_book_header': 'TSINGHUA_BOOK_',
    'modern_figure': 'V1001_MODERN_FIGURE',
    'vote_query': 'IN_THE_AIR_VOTE',
    'list_query': 'IN_THE_AIR_LIST'
}
'''
weixin_custom_menu_template = {
    "button": [
        {
            "name": "资讯",
            "sub_button": [
                {
                    "type": "click",
                    "name": "文艺",
                    "key": weixin_event_keys['info_activity'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "讲座",
                    "key": weixin_event_keys['info_lecture'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "新闻",
                    "key": weixin_event_keys['info_news'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "就业",
                    "key": weixin_event_keys['modern_figure'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "社团",
                    "key": weixin_event_keys['info_organization'],
                    "sub_button": []
                }
            ]
        },
        {
            "name": "服务",
            "sub_button": [
                {
                    "type": "click",
                    "name": "抢啥",
                    "key": weixin_event_keys['ticket_book_what'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "查票",
                    "key": weixin_event_keys['ticket_get'],
                    "sub_button": []
                },
                #{
                #    "type": "click",
                #    "name": "指路",
                #    "key": "tsinghua_path",
                #    "sub_button": []
                #},
                {
                    "type": "click",
                    "name": "绑定",
                    "key": weixin_event_keys['account_bind'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "帮助",
                    "key": weixin_event_keys['help'],
                    "sub_button": []
                }
            ]
        },
        {
            "name": "抢票",
            "sub_button": []
        }
    ]
}
'''
#### start by xiaohe 新的菜单 #######
weixin_custom_menu_template = {
    "button": [
        {
            "name": "资讯",
            "sub_button": [
                {
                    "type": "click",
                    "name": "文艺",
                    "key": "V1001_TODAT_ACTIVE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "讲座",
                    "key": "V1001_TODAT_LECTURE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "新闻",
                    "key": "V1001_SCHOOL_NEWS",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "就业",
		    "key": "V1001_MODERN_FIGURE",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "社团",
                    "key": "V1001_OGNIZATION",
                    "sub_button": []
                }
            ]
        },
        {
            "name":"团聚清华",
            "sub_button":[
                {
                    "type":"view",
                    "name":"校级组织",
                    "url":"http://115.28.212.177/tuanju:8080/cube?tuanju_type=organizations"
                },
                {
                    "type":"view",
                    "name":"院系所",
                    "url":"http://115.28.212.177/tuanju:8080/cube?tuanju_type=departments"
                },
                {
                    "type":"view",
                    "name":"团支部",
                    "url":"http://115.28.212.177/tuanju:8080/cube?tuanju_type=zhibu"
                },
                {
                    "type":"view",
                    "name":"清华周边",
                    "url":"http://115.28.212.177/tuanju:8080/cube?tuanju_type=surround"
                }
            ]
        },
        {
            "name": "服务",
            "sub_button": [
		{
                    "type":"click",
                    "name":"抢票",
                    "key":"TSINGHUA_BOOK_WHAT",
                    "sub_button":[]
                },
                {
                    "type": "click",
                    "name": "投票",
                    "key": WEIXIN_EVENT_KEYS['vote_query'],
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "抢啥",
                    "key": "TSINGHUA_BOOK_WHAT",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "查票",
                    "key": "TSINGHUA_TICKET",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "绑定",
                    "key": "TSINGHUA_BIND",
                    "sub_button": []
                },
                {
                    "type": "click",
                    "name": "帮助",
                    "key": "TSINGHUA_HELP",
                    "sub_button": []
                }
            ]
        }
    ]
}

#### end by xiaohe #################
WEIXIN_BOOK_HEADER = 'TSINGHUA_BOOK_'


def get_custom_menu_with_book_acts(actbtns):
    tmpmenu = WEIXIN_CUSTOM_MENU_TEMPLATE.copy()
    #### start by xiaohe 屏蔽抢票一级菜单#####
    return tmpmenu
    #### end by xiaohe #######################
    book_btn = tmpmenu['button'][2]
    if len(actbtns) == 0:
        book_btn['type'] = 'click'
        book_btn['key'] = WEIXIN_EVENT_KEYS['ticket_no_book_recommand']
    book_btn['sub_button'] = actbtns
    return tmpmenu

