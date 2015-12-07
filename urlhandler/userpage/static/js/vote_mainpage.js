var lastSelect;

window.onload = function(){
        $.ajax({
        type: 'GET',
        // url: "{%url 'userpage.views.check_open_id' openid%}",
        url: "/u/check_open_id/" + voteId + '/' + openid,
        success: function(msg){
            is_validate = msg['is_validate'];
            if (voted == 0 && msg['voted'] == 1){
                    $("button").remove();
                    $('#itemList').html('');
                    voted = msg['voted'];
                    for (var i = 0; i < vote_items.length; i++)
                        vote_items[i].vote_num = msg['items'][i]['vote_num'];
                    onCreate_voted();
            }
        },
        error: function(){
            }
    });
}

function commitVote() {
    if (is_validate == 0){
        var conf_stu = confirm('您的账户尚未绑定学号，绑定学号方可投票，您确定前往绑定吗？');
        if (conf_stu == false)
            return false;
        location.href = validate_url;
//        location.reload(true);
        return false;
    }
    var name_list = generateVoteNames();
    if(votenum <= 0) {
        alert("你还没有选择节目哦！");
        return false;
    }
    var conf = confirm(name_list);
    if (conf == false) {
        return false;
    }
    var options = generateOptions();
    $('#voteItem').ajaxSubmit(options);
    return false;
}

function generateVoteNames() {
    var name_list = "您要投的是：";
    var votes = $(".item-val");
    for(var i = 0; i < votes.length; i++) {
        if($(votes[i]).attr("value") == "on") {
            name_list += vote_items[i].name + ", "
        }
    }
    name_list = name_list.substring(0, name_list.length - 2);
    return name_list;
}

function generateOptions() {
    var options = {
        dataType: 'json',
        success: function (data) {
            if(data.error == null) {
                successLoad(data);
            } else {
                alert(data.error);
            }
        },
        error: function (xhr) {
            console.log(xhr);
            alert("很抱歉，好像发生了奇怪的错误= =");
        }
    };
    return options;
}

function successLoad(data) {
    $("button").remove();
    var votes = $(".item-val");
    for(var i = 0; i < votes.length; i++) {
        if($(votes[i]).attr("value") == "on") {
            vote_items[i].vote_num+= 1;
        }
    }
    $('#itemList').html('');
    onCreate_voted();
}


function addImg() {
    for (var i = 0; i < vote_items.length; i++) {
        var item = vote_items[i];
        if (layout_style == 0) {
            $('#' + item.id + ' .item-image img').attr({
                'src' : ((has_images == 1) ? item.pic_url : default_item_pic)
            });
        } else if (layout_style == 1) {
            $('#' + item.id + ' .item-image-grid img').attr({
                'src' : ((has_images == 1) ? item.pic_url : default_item_pic)
            });
        }
    }
}

function addVoteNumber() {
    for (var i = 0; i < vote_items.length; i++) {
        if (layout_style == 0) {
            $($('.item-vote')[i]).html('人气：' + vote_items[i].vote_num);
        } else if (layout_style == 1) {
            $($('.item-vote-grid')[i]).html('人气：' + vote_items[i].vote_num);
        }
    }
}

function changeItemCover(id) {
    var td = $("#" + id);
    var tick, tips;
    if (layout_style == 0) {
        tick = td.children(".item-tick");
        tips = td.children(".item-vote").children(".item-tip");
    } else if (layout_style == 1) {
        tick = td.children(".item-tick-grid");
        tips = td.children(".item-vote-grid").children(".item-tip-grid");
    }
    var val = td.children(".item-val");
        
    if (val.attr("value") == "off") {
        tick.show();
        tips.hide();
        val.attr("value", "on");
        votenum = votenum + 1;
    } else {
        tick.hide();
        tips.show();
        val.attr("value", "off");
        votenum = votenum - 1;
    }
}

function selectItem(id) {
    changeItemCover(id);
    if(votenum > maxVote) {
        voteNumOverflow(maxVote, id);
    } else {
        lastSelect = id;
    } 
}

function voteNumOverflow(vtLim, id) {
    if(vtLim == 1) {
        changeItemCover(lastSelect);
        lastSelect = id;
    } else {
        changeItemCover(id);
        alert("您的投票数已经达到上限，不能再投啦！");
    }
}

function bindClickEvent() {
    if (layout_style == 0) {
        $(".item-box").click(function() {
            selectItem($(this).attr("id"));
        });
    } else if (layout_style == 1) {
        $(".item-box-grid").click(function() {
            selectItem($(this).attr("id"));
        });
    }

    for (var i = 0; i < vote_items.length; i++) {
        var item = vote_items[i];
        if (layout_style == 0) {
            $("#" + item.id + " .item-image a").click(function(e) {
                e.stopPropagation();
                // location.href = vote_items[i].url;
            });
        } else if (layout_style == 1) {
            $("#" + item.id + " .item-image-grid a").click(function(e) {
                e.stopPropagation();
                // location.href = vote_items[i].url;
            });
        }
    }
}

function createItemBox(item, id) {
    var depict;
    if (item.description_simply)
        depict = item.description_simply;
     else{
        depict = item.description;
        if (depict.length > 20) {
            depict = depict.substr(0, 20) + "...";
        }
    }
    var box = 
    '<div class="item-box" id="' + item.id + '">' +
        '<input type="text" class="item-val" style="display:none;" name="' + (item.id) + '" value="off"/>' +
        '<div class="item-image">' +
            '<a href="' + item.url + '">' + 
                '<img src=""/>' + 
            '</a>' +
        '</div>' +
        '<div class="item-name">' + 
            item.name + 
        '</div>' + 
        '<div class="item-description">' + 
            depict +
        '</div>' + 
        '<div class="item-vote">' +
        '<div class="item-tip"><p>点此投票</p></div>' +
        '</div>' + 
        '<div class="item-tick" style="display:none;">' +
            '<img src="' + selectedImg + '">' +
        '</div>' +
    '</div>';

    return box;
}

function createItemBoxForGridLayout(item, id) {
    var box = 
    '<div class="item-box-grid" id="' + item.id + '">' +
        '<input type="text" class="item-val" style="display:none;" name="' + (item.id) + '" value="off"/>' +
        '<div class="item-image-grid">' +
            '<a href="' + item.url + '">' + 
                '<img src=""/>' + 
            '</a>' +
        '</div>' +
        '<div class="item-name-grid">' + 
            item.name + 
        '</div>' + 
        // '<div class="item-description-grid">' + 
        //     item.description +
        // '</div>' + 
        '<div class="item-vote-grid">' +
        '<div class="item-tip-grid"><p>点此投票</p></div>' +
        '</div>' + 
        '<div class="item-tick-grid" style="display:none;">' +
            '<img src="' + selectedImg + '">' +
        '</div>' +
    '</div>';

    return box;
}

function modifyStyle() {
    // var previousWidth = clientWidth;

    // clientWidth = document.body.clientWidth;
        var width;
    if (window.orientation == 90 || window.orientation == -90) {
        width = screenHeight;
    } else {
        width = screenWidth;
    }

    $('#itemList').css({
        "width" : (width - 20) + "px",
        "margin" : "0 auto 0 auto",
        "float" : "left"
    });

    var delta = (width - 20 - 270) / 6;
    $('.item-box-grid').css({
        "margin-left" : delta + "px",
        "margin-right" : delta + "px"
    })
    
   // return (clientWidth != previousWidth);
}

function createVoteItem() {
    for (var i = 0; i < vote_items.length; i++) {
        var item = vote_items[i];
        var box;
        if (layout_style == 0) {
            box = createItemBox(item, i);
        } else if (layout_style == 1) {
            box = createItemBoxForGridLayout(item, i);
        }
        $('#itemList').append(box);
    }

    if (layout_style == 1) {
        modifyStyle();
    }
}

function createBasicVoteItem() {
    createVoteItem();
}

function onCreate_ended() {
    $("#info")[0].innerHTML = "投票已经结束"
    $("button").remove();
    createBasicVoteItem();
    addVoteNumber();
    addImg();
}

function onCreate_unstarted() {
    $("#info")[0].innerHTML = "投票尚未开始" 
    $("button").remove();
    $('#itemList').html('活动尚未开始，精彩敬请期待');
    //createBasicVoteItem();
    //addImg();
}

function onCreate_unvoted() {
    var str = vote_type == 1 ? "今天" : "";
    $("#info")[0].innerHTML = "您" + str +"最多可投" + maxVote + "张票，点击图片查看详情"
    $("button").show();
    createBasicVoteItem();
    bindClickEvent();
    addImg();
}

function onCreate_voted() {
    var str = vote_type == 1 ? "今天" : "";
    $("#info")[0].innerHTML = "您" + str +"已经投过票啦，感谢您的参与"
    $("button").remove();
    createBasicVoteItem();
    addVoteNumber();
    addImg();
}

function createExtraInfo() {
    $('title').text(activity_page_title);
    $('#activity_title').text(activity_title);

    var node = $('#activity_extra_info');
    for (var i in activity_extra_info) {
        if(i == 1) {
            node.append('<div>'+'<label id="info">'+activity_extra_info[i].c+'</label>'+'</div>');
        } else {
            node.append('<div>'+'<label>'+activity_extra_info[i].c+'</label>'+'</div>');
        }
    }
    node.append('<div>' + '<label>' + '点击头像查看详细信息' + '</label></div>');
}

function showPageImages() {
    $('#activity_title_image').css({
       "background" : "url(" + activity_title_image + ") no-repeat center",
       "background-size" : "auto 100%",
       "height" : "100px",
       "background-position" : "center"
    });
    // $('#activity_title_image').append('<img src="' + activity_title_image + '"/>');
    // var sw;
    // if (window.orientation == 90 || window.orientation == -90) {
    //     sw = screenHeight;
    // } else {
    //     sw = screenWidth;
    // }
    // var img = new Image();
    // img.src = activity_title_image;
    // img.onload = function () {
    //     var imgWidth = img.width;
    //     var imgHeight = img.height;
    //     var transImgWidth = imgWidth * (180 / imgHeight);
    //     alert(sw);
    //     alert(transImgWidth);
    //     $('#activity_title_image').children('img').css({
    //         'height': "180px",
    //         'width': transImgWidth + "px",
    //         'left': (sw - transImgWidth) / 2 + "px",
    //         'right': (sw - transImgWidth) / 2 + "px"
    //     });
    // };
    $('.info').css({
        "background" : background_pic + " repeat-y",
        "background-size" : "100% auto"
    });
}

function orientationChange() {
    if (layout_style == 1) {
        modifyStyle();
        // while (true) {
        //     if (modifyStyle())
        //         break;
        // }
    }
}

function onCreate_program_list() {
    $('title').text('新年联欢晚会节目单');
    $('#activity_title').text('新年联欢晚会节目单');
    $('#activity_title_image').css({
        "background" : "url(" + activity_title_image + ") no-repeat",
        "height" : "100px",
        "background-position" : "center"
    });
    
    if (started == 0) {
        $('#itemList').html('晚会尚未开始，精彩敬请期待');
    } else {
        $("button").remove();
        createBasicVoteItem();
        addImg();
    }
    
}

function addEvent() {
    addEventListener('load', function() {
        window.onorientationchange = orientationChange;
    });
}

function onCreate(){
    if (typeid == 1) {
        onCreate_program_list();
        return;
    }

    createExtraInfo();

    if(started == 0) {
        onCreate_unstarted();
    } else if(ended == 1) {
        onCreate_ended();
    } else if(voted == 0) {
        onCreate_unvoted();
    } else {
        onCreate_voted();
    }

    showPageImages();

    addEvent();
}

onCreate();



// 初始化WeixinApi，等待分享
// WeixinApi.ready(function(Api) {

//     // 微信分享的数据
//     var wxData = {
//         "appId": "wxa04c8f42f836340b", // 服务号可以填写appId
//         "imgUrl" : vote_pic_url,
//         "link" : 'http://mp.weixin.qq.com/s?__biz=MzA5MjEzOTQwNA==&mid=202215525&idx=1&sn=3a549a27e1d2847776db3e2a40f967cc#rd',
//         "desc" : vote_description,
//         "title" : vote_name
//     };

//     // 分享的回调
//     var wxCallbacks = {
//         // 收藏操作不执行回调，默认是开启(true)的
//         favorite : false,

//         // 分享操作开始之前
//         ready : function() {
//             // 你可以在这里对分享的数据进行重组
//         },
//         // 分享被用户自动取消
//         cancel : function(resp) {
//             // 你可以在你的页面上给用户一个小Tip，为什么要取消呢？
//         },
//         // 分享失败了
//         fail : function(resp) {
//             // 分享失败了，是不是可以告诉用户：不要紧，可能是网络问题，一会儿再试试？
//             alert("分享失败，msg=" + resp.err_msg);
//         },
//         // 分享成功
//         confirm : function(resp) {
//             // 分享成功了，我们是不是可以做一些分享统计呢？
//         },
//         // 整个分享过程结束
//         all : function(resp,shareTo) {
//             // 如果你做的是一个鼓励用户进行分享的产品，在这里是不是可以给用户一些反馈了？
//         }
//     };

//     // 用户点开右上角popup菜单后，点击分享给好友，会执行下面这个代码
//     Api.shareToFriend(wxData, wxCallbacks);

//     // 点击分享到朋友圈，会执行下面这个代码
//     Api.shareToTimeline(wxData, wxCallbacks);

//     // 点击分享到腾讯微博，会执行下面这个代码
//     Api.shareToWeibo(wxData, wxCallbacks);

//     // iOS上，可以直接调用这个API进行分享，一句话搞定
//     Api.generalShare(wxData,wxCallbacks);

// });

