import os, sys
from stat import *
import shutil
import uuid
import hashlib
import pymysql
import re
if __name__ == '__main__':

    ccsnodict={}
    icsnodict={}
    dict_ics2ccs={}
    conn = pymysql.connect(host='172.16.1.137', port=3306, user='root', passwd='xxzx%#11',db='zszxalldata',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    #conn = pymysql.connect(host='124.193.169.146', port=3366, user='root', passwd='demo123#@!',db='zszxalldata',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    #init Dict
    cur.execute("SELECT classname,classno from zszx_ccs")
    for row in cur.fetchall():
        ccsnodict[row['classname']]=row['classno']

    cur.execute("SELECT classchinesename,classno from zszx_ics")
    for row in cur.fetchall():
        icsnodict[row['classno']]=row['classchinesename']

    cur.execute("SELECT icsclassno,ccsclassno from zszx_ics2ccs")
    for row in cur.fetchall():
        dict_ics2ccs[row['icsclassno']]=row['ccsclassno']

    #cur.execute("SELECT id,CCSNo,ICSNo FROM zszx_standards")
    cur.execute("SELECT id,Title,StdNo,CCSNo,ICSNo FROM zszx_standards_copy2 ")
    i=1
    content=''
    addfillrownum=1
    '''
        目标：
        1：根据ics，填充ccs分类为空的
            ics为空：不处理
            ics不为空，根据icsno找到ccsno，填充CCSNo的代码
        2：规范ccsno的原始中文值为代码
        
    '''
    for row in cur.fetchall():
        #print(row)


        init_content="\"%d\";\"%s\";\"%s\"\n"%(row['id'],row['CCSNo'],row['ICSNo'])
        rep_content=''
        rowid=row['id']
        init_ccsno=row['CCSNo']
        init_icsno=row['ICSNo']
        title=row['Title']
        stdno=row['StdNo']

        m=re.match(r'.*;$',init_ccsno)
        if(m):
            init_ccsno=init_ccsno[0:len(init_ccsno)-1]

        m=re.match(r'.*;$',init_icsno)
        if(m):
            init_icsno=init_icsno[0:len(init_icsno)-1]


        CCSNolist=init_ccsno.split(';')
        ICSNolist=init_icsno.split(';')

        repCCSNo=''
        repICSNo=''

        for ccsno in CCSNolist:
            try:
                repCCSNo+=ccsnodict[ccsno]+';'
            except:
                repCCSNo+='KeyError;'
        repCCSNo=repCCSNo[0:len(repCCSNo)-1]

        for iscno in ICSNolist:
            try:
                repICSNo+=icsnodict[icsno]+';'
            except:
                repICSNo+='KeyError;'
        repICSNo=repICSNo[0:len(repICSNo)-1]

        '''
        处理数据
        '''
        ccsnoaddtofill=''
        if (init_ccsno=='' or init_ccsno==None):
            if(init_icsno!='' and init_icsno!=None):
                for icsno in ICSNolist:
                    try:
                        ccsnoaddtofill+=dict_ics2ccs[icsno]+';'
                    except:
                        ccsnoaddtofill+='NoICSNoKey;'
                ccsnoaddtofill=ccsnoaddtofill[0:len(ccsnoaddtofill)-1]
                sql="update zszx_standards set CCSNo='"+ccsnoaddtofill+"' where id="+str(rowid);
                cur2=conn.cursor()
                print("execute sql: "+sql)
                addtofilllog="RowNum: %d\nRowId: %d\nTitle: %s\nStdNo: %s\n原始ICSNO: %s\n补充CCSNO: %s\n\n"%(addfillrownum,rowid,title,stdno,init_icsno,ccsnoaddtofill)
                with open("补充ccsno日志.txt",'a') as f:
                    try:
                        f.write(addtofilllog)
                    except Exception:
                        pass
                cur2.execute(sql)
                conn.commit()
                addfillrownum+=1

        rep_content="%d;\"%s\";\"%s\"\n"%(row['id'],repCCSNo,repICSNo)

        content+=init_content+rep_content


        if (i%1000==0):
            with open("step-1-result.txt",'a') as f:
                try:
                    f.write(content)
                    content=''
                except Exception:
                    pass
        i+=1


    cur.close()
    conn.close()
