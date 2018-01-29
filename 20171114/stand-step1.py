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
    # conn = pymysql.connect(host='172.16.155.1', port=3306, user='root', passwd='Root123!@#',db='zszxdata',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='root', db='zszxdata',charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
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

    i=1
    content=''
    addfillrownum=1
    updaterownum = 1
    count = 0
    doloop=True
    '''
        目标：
        不规范样例：
        13.120 - Domestic safety37.060.10 - Motion picture equipment97.180 - Miscellaneous domestic and commercial equipment 
        13.120 - Domestic safety97.180 - Miscellaneous domestic and commercial equipment 
        1：根据ICSClassification不规范字段（包含‘-’字符），处理为规范字段，填充到icsno
            ics是否包含‘-’
            利用正则判断，然后在分类号前面加个；号
        2:需要递归处理多个不规范分类的情况
    '''

    while doloop:
        count=0
        cur.execute("SELECT GUID,id,Title,StdNo,CCSNo,ICSNo FROM zszx_standards_update20171114 ")
        for row in cur.fetchall():
            #print(row)


            init_content="\"%d\";\"%s\";\"%s\"\n"%(row['id'],row['CCSNo'],row['ICSNo'])
            rep_content=''
            rowid=row['id']
            init_ccsno=row['CCSNo']
            init_icsno=row['ICSNo']
            title=row['Title']
            stdno=row['StdNo']
            repICSNo = ''


            # print(init_icsno)
            if (init_icsno != '' or init_icsno != None):
                # m = re.match(r'.*(\s-\s.*)\d+.*', init_icsno)
                # m = re.match(r'.*\s-\s.*', init_icsno)
                m = re.match(r'(.*[a-zA-Z])([\d.]+\s-\s.*)', init_icsno)
                if(m):
                    print("--------------------------")
                    print(m.group())
                    print(m.group(1))
                    print(m.group(2))
                    repICSNo = ''
                    repICSNo=m.group(1)+";"+m.group(2)
                    print("rep= " + repICSNo)


                    count+=1
                    sql = "update zszx_standards_update20171114 set ICSNo=\"" + repICSNo + "\" where id=" + str(rowid);
                    cur2 = conn.cursor()
                    print("execute sql: " + sql)
                    addtofilllog = "RowNum: %d\nRowId: %d\nTitle: %s\nStdNo: %s\n原始ICSNO: %s\n更新ICSNO: %s\n\n" % (
                    updaterownum, rowid, title, stdno, init_icsno, repICSNo)
                    with open("step1日志.txt", 'a') as f:
                        try:
                            f.write(addtofilllog)
                        except Exception:
                            pass
                    cur2.execute(sql)
                    conn.commit()
                    updaterownum += 1

        print(count)
        if count==0:
            doloop=False

    cur.close()
    conn.close()