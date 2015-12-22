/**
 * Created with Sublime.
 * User: SwingACE
 * Date: 14-12-23
 * Time: 下午23:09
 */

function histogram(){
	var controls={};
	var bgColor=new Array("#666666","#21AA7C","#2277BB","#dc7644","#BBAA22","#AA22AA","#338800","#1099EE","#ffcc33","#ED3810");
	this.init=function(data,y){
		setControls();
		buildHtml(data,y);
	}
	function setControls(){
		controls.histogramContainer=$("#histogram-container");
		controls.histogramBgLineUL=controls.histogramContainer.children("div.histogram-bg-line");
		controls.histogramContentUL=controls.histogramContainer.children("div.histogram-content");
		controls.histogramY=controls.histogramContainer.children("div.histogram-y");
	}
	function buildHtml(data,y){
		var len=data.length,perArr=new Array(),maxNum,maxTotal,yStr='';
		var contentStr='',bgLineStr='',bgLineAll='';
		var widthPer=Math.floor(100/len);
		minWidth=len*21+60;
		controls.histogramContainer.css("min-width",minWidth+"px");
		
		for(var a=0;a<len;a++){
			perArr[a]=parseInt(data[a]['per']);		
		}
		maxNum=String(perArr.max());
		if(maxNum.length>2){
			var x=parseInt(maxNum.substr(maxNum.length-2,1))+1;
			maxTotal=Math.floor(parseInt(maxNum/100))*100+x*10;
		}else{
			maxTotal=Math.floor(parseInt(maxNum/10))*10+10;
		}
		
		//y轴部分
		if(y=="%"){
			yStr+='<li>100%</li><li>80%</li><li>60%</li><li>40%</li><li>20%</li><li>0%</li>';			
		}else{
			var avg=maxTotal/5;
			for(i=5;i>=0;i--){
				yStr+='<li>'+avg*i+'</li>';
			}
		}
		
		//柱状条部分
		for(var i=0;i<len;i++){
			var per=Math.floor(parseInt(data[i]['per'])/maxTotal*100);
			var n=Math.floor(parseInt(per)/10);
			contentStr+='<li style="width:'+widthPer+'%">';
			contentStr+='<span class="histogram-box"><a style="height:'+per+'%'+';background:'+bgColor[n]+';" title="'+data[i]['per']+'"></a></span><span class="histogram-name">'+data[i]['name']+'</span>';
			contentStr+='</li>';
			bgLineStr+='<li style="width:'+widthPer+'%;"><div></div></li>';
		}
		
		//背景方格部分
		for(var j=0;j<5;j++){
			bgLineAll+='<ul>'+bgLineStr+'</ul>';
		}
		bgLineAll='<div class="histogram-bg-line">'+bgLineAll+'</div>';
		contentStr='<div class="histogram-content"><ul>'+contentStr+'</ul></div>';
		yStr='<div class="histogram-y"><ul>'+yStr+'</ul></div>';
		controls.histogramContainer.html(bgLineAll+contentStr+yStr);
		controls.histogramContainer.css("height",controls.histogramContainer.height()+"px");//主要是解决IE6中的问题		
	}
}
Array.prototype.max = function(){//最大值
 return Math.max.apply({},this) 
} 


 // 一下为格式示例
 //  var multiData = {values:[
 // { value0:[
 //   {x:"Jan",y:5},
 //   {x:"Feb",y:5},
 //   {x:"Mar",y:80},
 //   {x:"Apr",y:10},
 //   {x:"May",y:30},
 //   {x:"Jun",y:30},
 //   {x:"Jul",y:60},
 //   {x:"Aug",y:10}
 //  ]},
 //  { value1:[
 //    {x:"Jan",y:50},
 //    {x:"Feb",y:40},
 //    {x:"Mar",y:60},
 //    {x:"Apr",y:10},
 //    {x:"May",y:20},
 //    {x:"Jun",y:10},
 //    {x:"Jul",y:40},
 //    {x:"Aug",y:10}
 //   ]}
 //  ]	
 // }
 //必须按照这个格式定义数据，关键字values value0 value1 ...... 
   /*
    *@param0: canvas 的id
    *@param1: json 数据
    *@param2: 坐标距离画布的间隙padding
    *@param3: 如果只有一条数据时数据的颜色，多条数据颜色随机
    *@param4: 点的颜色
    *@param5: 是否绘制背景线
    *@param6: 是否是多条数据
    */
   //先定义数据线的名字，再绘制数据
 
		
var LineChart={
    keynames:[],//数据信息数组
    can:undefined,
    ctx:undefined,
    width:undefined,
    lineColor:undefined,
    dotColor:undefined,
    isBg:false,
    isMultiData:false,
    setData:function(canId,data,padding,lineColor,dotColor,isBg,isMultiData){
      this.lineColor = lineColor;
      this.dotColor = dotColor;
      this.can = document.getElementById(canId);
      this.ctx = this.can.getContext("2d");
      this.isBg = isBg;
      this.isMultiData = isMultiData;
      this.drawXY(data,0,padding,this.can);
			
    },
   isMultiData:function(data){
      if(data.values.length>1){
        this.isMultiData = true;
       }
    },//是否是多条数据线
	
    drawXY:function(data,key,padding,can){
	this.ctx.lineWidth="4";
	this.ctx.strokeStyle="black";
	this.ctx.font = 'italic 15px sans-serif';
	this.ctx.beginPath();
	this.ctx.moveTo(padding,0)
	this.ctx.lineTo(padding,can.height-padding);
	this.ctx.lineTo(can.width,can.height-padding);
	this.ctx.stroke();
	var perwidth = this.getPixel(data,key,can.width,padding);//x 轴每一个数据占据的宽度
	var maxY =  this.getMax(data,0,this.isMultiData);//获得Y轴上的最大值
	var yPixel = this.getYPixel(maxY,can.height,padding).pixel;
	var ycount = this.getYPixel(maxY,can.height,padding).ycount;
	for( var i=0,ptindex;i< data.values[key]["value"+key].length;i++ ){
		ptindex = i+1;
		var x_x = this.getCoordX(padding,perwidth,ptindex);
		var x_y = can.height-padding+20;
		this.ctx.fillText(data.values[key]["value"+key][i].x,x_x,x_y,perwidth);
	}
	this.ctx.textAlign = "right"//y轴文字靠右写
	this.ctx.textBaseline = "middle";//文字的中心线的调整
	for(var i=0;i< ycount/10;i++){
	   this.ctx.fillText(i*10,padding-10,(ycount/10-i)*10*yPixel,perwidth);
	}
	if(this.isBg){
	   var x =  padding;
	   this.ctx.lineWidth="1";
	   this.ctx.strokeStyle="#e8e8e8";
	   for( var i=0;i< ycount/10;i++ ){
		var y = (ycount/10-i)*10*yPixel;
		this.ctx.moveTo(x,y);
		this.ctx.lineTo(can.width,y);
		this.ctx.stroke();
	  }
     }//选择绘制背景线
	this.ctx.closePath();
	this.drawData(data,0,padding,perwidth,yPixel,this.isMultiData);
    },//绘制XY坐标 线 以及点
	
    drawData:function(data,key,padding,perwidth,yPixel,isMultiData,lineColor){
  	if(!isMultiData){
		var keystr = "value"+key;
		this.ctx.beginPath();
		this.ctx.lineWidth="2";
		if(arguments[6]){
	        this.ctx.strokeStyle=lineColor;
	       }else{
		   this.ctx.strokeStyle=this.lineColor;
             }
		var startX = this.getCoordX(padding,perwidth,0);
		var startY = this.getCoordY(padding,yPixel,data.values[key][keystr][0].y);
		this.ctx.beginPath();
		this.ctx.lineWidth="2";
		for( var i=0;i< data.values[key][keystr].length;i++ ){
		  var x = this.getCoordX(padding,perwidth,i+1);
		  var y = this.getCoordY(padding,yPixel,data.values[key][keystr][i].y);
		  this.ctx.lineTo(x,y);
		}
		this.ctx.stroke();
		this.ctx.closePath();
		/*下面绘制数据线上的点*/
		this.ctx.beginPath();
		this.ctx.fillStyle=this.dotColor;
		for( var i=0;i< data.values[key][keystr].length;i++ ){
		   var x = this.getCoordX(padding,perwidth,i+1);
		   var y = this.getCoordY(padding,yPixel,data.values[key][keystr][i].y);
		   this.ctx.moveTo(x,y);
		   this.ctx.arc(x,y,3,0,Math.PI*2,true);//绘制数据线上的点
		   this.ctx.fill();
		}
		this.ctx.closePath();
		}else{//如果是多条数据线
		   for( var i=0;i< data.values.length;i++ ){
			var color = "rgb("+parseInt(Math.random()*256)+","+parseInt(Math.random()*256)+","+parseInt(Math.random()*256)+")";
			LineChart.drawData(data,i,padding,perwidth,yPixel,false,color);
			LineChart.drawKey(color,this.keynames[i],padding,i);
		     }
		  }
		},//绘制数据线和数据点
		getPixel:function(data,key,width,padding){
		  var count = data.values[key]["value"+key].length;
		  return (width-20-padding)/(count+(count-1)*1.5);	
		},//宽度
		getCoordX:function(padding,perwidth,ptindex){//下标从1开始 不是从0开始
			return 2.5*perwidth*ptindex+padding+10-2*perwidth;
		},//横坐标X 随ptindex 获得
		getCoordY:function(padding,yPixel,value){
			var y = yPixel*value;
			return this.can.height-padding-y;
		},//纵坐标X 随ptindex 获得(注意 纵坐标的算法是倒着的因为原点在最上面)
		 getYPixel:function(maxY,height,padding){
			var ycount = (parseInt(maxY/10)+1)*10+10;//y轴最大值
			return {pixel:(height-padding)/ycount,ycount:ycount};
		},//y轴的单位长度
        	
          getMax:function(data,key,isMultiData){
        	if(!isMultiData){
                var maxY = data.values[key]["value"+key][0].y;
        	  var length = data.values[key]["value"+key].length;
        	  var keystr = "value"+key;
        	  for( var i=1;i< length;i++ ){
        		if(maxY< data.values[key][keystr][i].y) maxY=data.values[key][keystr][i].y;
        	  }
        	  return maxY;//返回最大值 如果不是多数据
        	  }else{
        	    var maxarr=[];
        	    var count = data.values.length;//多条数据的数据长度
        	    for(var i=0;i< count;i++){
        		maxarr.push(LineChart.getMax(data,i,false));
        	    }
        	    var maxvalue = maxarr[0];
        	    for(var i=1;i< maxarr.length;i++){
        		maxvalue = (maxvalue< maxarr[i])?maxarr[i]:maxvalue; 
        	    }
        	    return maxvalue;
        	}//如果是多数据
           },
        	
        setKey:function(keynames){//keynames 是数组
        	for(var i=0;i< keynames.length;i++){
                this.keynames.push(keynames[i]);//存入数组中
        	}
         },
        
 	drawKey:function(color,keyname,padding,lineindex){
      		var x = padding+10;
      		var y = this.can.height - padding+20+13*(lineindex+1);
      		this.ctx.beginPath();
      		this.ctx.strokeStyle = color;
      		this.ctx.font="10px";
      		// this.ctx.moveTo(x,y);
      		// this.ctx.lineTo(x+50,y);
      		// this.ctx.fillText(":"+keyname,x+80,y,30);
      		this.ctx.stroke();
      		this.ctx.closePath();
      	}
    }	

function init (){
	var items = vote.items;
    sort(items);
    var newItems = [];
    for (var i = vote.items.length-1; i >= 0; --i){
    	newItems.push({
    		"name":(vote.items.length-i).toString(),
    		"per":(items[i].vote_num).toString()
    	})
    	var tr = $('<tr></tr>');
        $("<td class='table-item'></td>").html((vote.items.length-i).toString()).appendTo(tr);
        $("<td class='table-item'></td>").html(items[i].name).appendTo(tr);
        $('#histogram-table').append(tr);
    }
	new histogram().init(newItems);

	var times = [];
	for (var i = 0; i < vote.times.length; i++){
		times.push({
    		x:(i+1).toString(),
    		y:vote.times[i].height
    	})
    	var tr = $('<tr></tr>');
        $("<td class='table-item'></td>").html((i+1).toString()).appendTo(tr);
        $("<td class='table-item'></td>").html(vote.times[i].interval).appendTo(tr);
        $('#lineargram-table').append(tr);
	}
	var data = {values:[{value0:times}]};
	LineChart.setKey([""]);
	LineChart.setData("canvas",data,60,"red","#333",true,true);
	showHistogram();
}

function showHistogram (){
	$("#histogram-container").show();
	$("#histogram-table").show();
	$("#histogram-caption").show();
	$("#canvas").hide();
	$("#lineargram-table").hide();
	$("#lineargram-caption").hide();
}

function showLineargram() {
	$("#histogram-container").hide();
	$("#histogram-table").hide();
	$("#histogram-caption").hide();
	$("#canvas").show();
	$("#lineargram-table").show();
	$("#lineargram-caption").show();
}

function sort(arr){
    return quickSort(arr,0,arr.length-1);
    function quickSort(arr,l,r){            
        if(l<r){         
            var mid=arr[parseInt((l+r)/2)].vote_num,i=l-1,j=r+1;         
            while(true){
                while(arr[++i].vote_num<mid);
                while(arr[--j].vote_num>mid);             
                if(i>=j)break;
                var temp=arr[i];
                arr[i]=arr[j];
                arr[j]=temp;
            }       
            quickSort(arr,l,i-1);
            quickSort(arr,j+1,r);
        }
        return arr;
    }
}

init();