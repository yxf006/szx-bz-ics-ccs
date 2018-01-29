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

    i=1
    content=''
    addfillrownum=1
    updaterownum = 1
    count = 0
    doloop=True
    '''
        目标：
        1：将已经加好分号的icsno字段（包含‘-’字符），替换英文为空
            ics是否包含‘-’
            利用正则判断，然后替换不规范内容为空
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
            s1=''
            s2=''


            # print(init_icsno)
            if (init_icsno != '' or init_icsno != None):
                # m = re.match(r'(.*)(\s-\s.*;)(.*)', init_icsno)
                s1=re.sub('\s-\s[^-]*;', ';', init_icsno)   #处理开头和中间带分号结尾的情况 13.120 - Domestic safety;37.060.10 - Motion picture equipment;
                s2=re.sub('\s-\s.*','',s1)  #处理结尾没有分号的情况
                repICSNo=s2
                # m = re.match(r'.*\s-\s.*', init_icsno)
                # m = re.match(r'(.*[a-zA-Z])([\d.]+\s-\s.*)', init_icsno)
                # if(m):
                #     print("--------------------------")
                #     print(m.group())
                #     print(m.group(1))
                #     print(m.group(2))
                #     print(m.group(3))
                #     repICSNo = ''
                #     repICSNo=m.group(1)+";"+m.group(2)
                #     print("rep= " + repICSNo)
                print(rowid,repICSNo)


                # count+=1
                sql = "update zszx_standards_update20171114 set ICSNo=\"" + repICSNo + "\" where id=" + str(rowid);
                cur2 = conn.cursor()
                print("execute sql: " + sql)
                addtofilllog = "RowNum: %d\nRowId: %d\nTitle: %s\nStdNo: %s\n原始ICSNO: %s\n更新ICSNO: %s\n\n" % (
                updaterownum, rowid, title, stdno, init_icsno, repICSNo)
                with open("step2日志.txt", 'a') as f:
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