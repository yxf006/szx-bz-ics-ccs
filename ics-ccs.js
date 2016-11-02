'use strict'
const readline=require('readline')
const fs=require("fs")
const iconv=require("iconv-lite")


const r1=readline.createInterface({
  //input:fs.createReadStream("ICS-CCS.csv")
  input:fs.createReadStream("ICS-CCS-step1-nobomutf8.csv")
});

var i=1;
r1.on('line',(line)=>{
  console.log('Line '+i+':  '+line);

  let arr;
  arr=line.split(',');
  console.log(arr);
  console.log(arr[0]);
  let icskey=arr[0];
  console.log('icskey='+icskey);

  let rowmap={}
  let rowmapvaluearr=[]
  for(let j=1,l=arr.length;j<l;j++){
    if (arr[j]=='') {


    } else {
      console.log(arr[j]);
      rowmapvaluearr.push(arr[j]);

    }
  }
  rowmap[icskey]=rowmapvaluearr;
  //fs.appendFile('result.csv',iconv.encode(icskey+','+arr[j]+'\n','GBK'),function(err){
  let linedata;
  if (rowmapvaluearr.length>0){
    //linedata=icskey+','+rowmap[icskey]+'\n';
    linedata=''
    for(let i=0,l=rowmapvaluearr.length;i<l;i++){
      linedata+=icskey+','+rowmapvaluearr[i]+'\n';
    }
  }else {
    linedata=icskey+'\n';
  }
  fs.appendFile('result.csv',linedata,function(err){
    if (err) {
      console.log('write file fail: '+ err);
    } else {
      console.log('write '+rowmap[icskey]+'  ok! ')
    }
  })


  console.log('End Line')
  i+=1
});

console.log("End File,Bingo!");
