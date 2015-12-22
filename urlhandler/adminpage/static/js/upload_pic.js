/**
 * Created by wangbb13 on 2015/12/5.
 */

var currentBtn = 0;

$(document).ready(function()
{
    $('#upload_pic_btn').click(function() {
        var options = {
            dataType: 'json',
            success: successRes,
            error: errorRes
        };
        $('#fileUploader').ajaxSubmit(options);
        return false;
    });
    $('#modify_pic_btn').click(function () {
        var options = {
            dataType: 'json',
            success: sRes,
            error: eRes
        };
        $('#mfileUploader').ajaxSubmit(options);
        return false;
    });
    hideUploader();
    $("#alphaCover").click(hideUploader);
    $("#input-uploadPic_0").click(function(){
        showUploader();
        currentBtn = 0;
        $("#optionIndex").val(0);
    });
    $("#modify-pic_0").click(function () {
        currentBtn = 0;
        showModify();
    });
    $("#input-uploadPic_1").click(function(){
        showUploader();
        currentBtn = 1;
        $("#optionIndex").val(1);
    });
    $("#modify-pic_1").click(function () {
        currentBtn = 1;
        showModify();
    });
    $('#malphaCover').click(hideModify);
});

// 上传图片
function hideUploader()
{
    $("#globalCover").css("visibility","hidden");
    $("#alphaCover").css("opacity","0");
    $("#windowCover").css("top","-100px");
}

function showUploader()
{
    $("#globalCover").css("visibility","visible");
    $("#alphaCover").css("opacity","0.3");
    $("#windowCover").css("top","10%");
    $("#errCosntent").text("");
}

// 修改图片
function hideModify() {
    $("#mglobalCover").css("visibility","hidden");
    $("#malphaCover").css("opacity","0");
    $("#mwindowCover").css("top","-100px");
    $(".jcrop-holder").hide();
}

function showModify() {
    $("#mglobalCover").css("visibility","visible");
    $("#malphaCover").css("opacity","0.3");
    $("#mwindowCover").css("top","10%");
    $("#merrCosntent").text("");
    var addr = $("#input-pic_url_" + currentBtn).val();
    var img = $('<img src="' + addr + '?temp=' + Math.random() + '" id="target" />');
    try {
        $('#mwindowCover #target').remove();
        $(".jcrop-holder").remove();
    } catch (e) {}
    $('#mwindowCover').prepend(img);
    ready();
    var index = addr.lastIndexOf('/');
    var filename = addr.substr(index + 1);
    $('#picfilename').val(filename);
}

function errorRes(data)
{
    if (data && data.status==200)
    {
        successRes(data);
        return;
    }
    $("#windowCover").removeClass("shadowBlue").addClass("shadowRed");
    setTimeout(function()
    {
        $("#windowCover").removeClass("shadowRed").addClass("shadowBlue");
    },1000);
    if (data.responseText instanceof String)
    {
        $("#errCosntent").text(data);
    }
    else
    {
        $("#errCosntent").text("上传失败");
    }
}

function successRes(data)
{
    if (data.responseText.substr(0, 4)!="http")
    {
        errorRes();
        return;
    }
    $("#input-pic_url_" + currentBtn)[0].value=data.responseText;
    hideUploader();
    // 为修改图片做准备
    if($('#mwindowCover #target').length != 0){
        $('#mwindowCover #target').remove();
        $(".jcrop-holder").remove();
    }
    $('#mwindowCover').prepend('<img src="' + data.responseText + '" id="target" />');
    $("#modify-pic_" + currentBtn).css("display", "block");
    var filename = data.responseText;
    var index = filename.lastIndexOf('/');
    filename = filename.substr(index + 1);
    $('#picfilename').val(filename);
    var img = new Image();
    img.src = data.responseText;
    img.onload = function () {
        var width = img.width;
        var height = img.height;
        $("#mwindowCover").css({
            "width": (width + 150) + "px",
            "height": (height + 150) + "px"
        });
    }
}

function sRes(data) {
    if(data.responseText.substr(0, 4) != "http") {
        eRes(data);
        return;
    }
    if($('#mwindowCover #target').length != 0){
        $('#mwindowCover #target').remove();
        $(".jcrop-holder").remove();
    }
    $('#mwindowCover').prepend('<img src="' + data.responseText + '?temp=' + Math.random() + '" id="target" />');
    hideModify();
}

function eRes(data) {
    if(data.responseText) {
        $('#merrCosntent').text(data.responseText);
    } else {
        $('#merrCosntent').text("修改失败!");
    }
}

function ready(){
    var jcrop_api;
    $('#target').Jcrop({
      onChange:   showCoords,
      onSelect:   showCoords,
      onRelease:  clearCoords,
      setSelect: [ 0, 0, 90, 90 ]
    },function(){
      jcrop_api = this;
    });

    $('#mfileUploader').on('change','input',function(e){
      var x1 = $('#x1').val(),
          x2 = $('#x2').val(),
          y1 = $('#y1').val(),
          y2 = $('#y2').val();
      jcrop_api.setSelect([x1,y1,x2,y2]);
    });
}

// Simple event handler, called from onChange and onSelect
// event handlers, as per the Jcrop invocation above
function showCoords(c)
{
    $('#x1').val(c.x);
    $('#y1').val(c.y);
    $('#x2').val(c.x2);
    $('#y2').val(c.y2);
    $('#w').val(c.w);
    $('#h').val(c.h);
}

function clearCoords()
{
    $('#mfileUploader #x1').val('');
    $('#mfileUploader #y1').val('');
    $('#mfileUploader #x2').val('');
    $('#mfileUploader #y2').val('');
    $('#mfileUploader #w').val('');
    $('#mfileUploader #h').val('');
}

