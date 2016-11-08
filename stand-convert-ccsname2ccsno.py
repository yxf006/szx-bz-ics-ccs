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
    cur.execute("SELECT id,Title,StdNo,CCSNo,ICSNo FROM zszx_standards ")
    i=1
    content=''
    updaterownum=1
    '''
        目标：
        规范ccsno的原始中文值为代码
            ccsno为空：不处理
            ccsno不为空，
                规范代码，不处理
                纯粹中文描述，填充CCSNo的代码
                代码和中文混杂，改为CCSNo代码
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
        repCCSNo=''
        if (init_ccsno!='' or init_ccsno!=None):
            for ccsno in CCSNolist:
                repCCSNotemp=''
                #纯中文字符串
                m=re.match(r"^[^A-Za-z0-9].*\D$",ccsno)
                if(m):
                    try:
                        repCCSNotemp=ccsnodict[ccsno]
                        pass
                    except:
                        repCCSNotemp='CCSNoKeyError'
                        pass
                #代码和中文混合:ccsnoxxx
                m=re.match(r"(^[A-Z][A-Z0-9/]*)([^A-Za-z0-9]*)",ccsno)
                if(m):
                    try:
                        repCCSNotemp=m.group(1)
                        pass
                    except:
                        repCCSNotemp='CCSNoGroupOneKeyError'
                        pass
                #代码和中文混合:xxx(ccsno)
                m=re.match(r"(^[^A-Za-z0-9]*)(\()([A-Za-z0-9]*)(\)$)",ccsno)
                if(m):
                    try:
                        repCCSNotemp=m.group(3)
                        pass
                    except:
                        repCCSNotemp='CCSNoGroupOneKeyError'
                        pass
                #规范代码格式
                m=re.match(r"^[A-Z][A-Z0-9/]*\d$",ccsno)
                if(m):
                    repCCSNotemp=ccsno
                    pass

                repCCSNo+=repCCSNotemp+';'
            repCCSNo=repCCSNo[0:len(repCCSNo)-1]


            sql="update zszx_standards set CCSNo='"+repCCSNo+"' where id="+str(rowid);
            cur2=conn.cursor()
            print("execute sql: "+sql)
            addtofilllog="RowNum: %d\nRowId: %d\nTitle: %s\nStdNo: %s\n原始CCSNO: %s\n更新CCSNO: %s\n\n"%(updaterownum,rowid,title,stdno,init_ccsno,repCCSNo)
            with open("转换ccsno日志.txt",'a') as f:
                try:
                    f.write(addtofilllog)
                except Exception:
                    pass
            #cur2.execute(sql)
            #conn.commit()
            updaterownum+=1

        i+=1


    cur.close()
    conn.close()
