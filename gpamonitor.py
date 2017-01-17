#!/usr/bin/python
# -*- coding=utf-8 -*-


__author__ = 'smartjinyu'

import sys
import requests
import re
from bs4 import BeautifulSoup
from prettytable import PrettyTable
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pickle
import os
import traceback


# 请在此处设置个人信息
id = "19020202201234"  # 校园卡账号，如 id = "19020202201234"
pwd = "password"      # 教务系统密码，如 pwd = "password"

# 请在此设置邮箱信息，默认仅供参考无法使用
mail_host = 'smtp.exmail.qq.com'   #发送邮箱 SMTP 服务器地址
mail_port = 465                    #发送邮箱 SMTP 服务器端口
mail_useSSL = True                 #是否使用 SSL
mail_user = 'nofity@smartjinyu.com'    #发送邮箱用户名
mail_pass = 'adminadmin'            #发送邮箱密码

mail_receivers = 'smartjinyu@gmail.com'  #用于接收通知的接收邮箱地址
#

def login():
    loginUrl = 'http://ssfw.xmu.edu.cn/cmstar/userPasswordValidate.portal'
    gradeUrl = 'http://ssfw.xmu.edu.cn/cmstar/index.portal?.pn=p1201_p3535'
    postData = {
        'Login.Token1': id,
            'Login.Token2': pwd,
            'goto': 'http://ssfw.xmu.edu.cn/cmstar/loginSuccess.portal',
            'gotoOnFail': 'http://ssfw.xmu.edu.cn/cmstar/loginFailure.portal'
        }
    s = requests.session()
    s.post(loginUrl,postData)
   # html = requests.get(loginUrl,postData)
    html = s.get(gradeUrl)
    print html.text
    if u'登录须知：' in html.text:
        print "Login Failed, please check your id or password."
    else:
        print "Login Succeeded."
        parse_page(html)

def parse_page(html):
    soup = BeautifulSoup(html.text,'lxml')
    name = soup.find(text = re.compile(u"欢迎您：")).encode('utf-8')
    name = name[name.find("：")+3:]
    print ("姓名: %s  学号: %s"%(name,id))
    print '本程序只计算主修成绩，如有需要计算辅修交流成绩请自行修改源代码'
    print

    grade_list_soup = soup.find('table',attrs={'class','xmu_table_class'})
    trList = grade_list_soup.find_all('tr')
    indexList = [i for i,item in enumerate(trList) if re.search("学年",item.encode('utf-8'))]
    i = 0
    point_all = 0 #总绩点
    credit_all = 0 #总学分
    table = PrettyTable([u'课程名称', u'学分', u'成绩', u'绩点'])
    table.padding_width = 5
    table.align[u'课程名称'] = "1"
    while i < len(indexList):
        j = indexList[i] + 1
        if i < len(indexList) -1 :
            end = indexList[i+1]
        else:
            end = len(trList)
        point =  0 #学期总绩点
        credit = 0 #学期总学分
        while j < end:
            curTr = trList[j]
            detail = curTr.find_all('font')
            name = detail[0].text
            ccredit = detail[1].text #学分
            cgrade = detail[4].text #成绩
            temp = cgrade.encode('gbk')
            if temp.isdigit():
                if temp == '100':
                    cgpa = 4.0
                elif temp >= '90':
                    cgpa = 4.0
                elif temp >= '85':
                    cgpa = 3.7
                elif temp >= '81':
                    cgpa = 3.3
                elif temp >= '78':
                    cgpa = 3.0
                elif temp >= '75':
                    cgpa = 2.7
                elif temp>= '72':
                    cgpa = 2.3
                elif temp >= '68':
                    cgpa = 2.0
                elif temp >= '64':
                    cgpa = 1.7
                elif temp>= '60':
                    cgpa =1.0
                else:
                    cgpa = 0

                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)


            elif temp == 'A+':
                cgpa = 4.0
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'A':
                cgpa = 4.0
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'A-':
                gpa = 3.7
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'B+':
                cgpa = 3.3
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'B':
                cgpa = 3.0
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'B-':
                cgpa = 2.7
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'C+':
                cgpa = 2.3
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'C':
                cgpa = 2.0
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'C-':
                cgpa = 1.7
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            elif temp == 'D':
                cgpa =1.0
                credit += float(ccredit)
                point += float(ccredit) * float(cgpa)
            else:
                cgpa = '--'



            table.add_row([name,ccredit,cgrade,cgpa])
            j += 1
        table.add_row([trList[indexList[i]].find('b').getText() +" 总计",credit,point,"%.4f" %(point / credit)])
        #学期总计
        table.add_row(["---------------------","------------","------------","------------"])

        point_all += point
        credit_all += credit
        i += 1

    curGPA = float("%.4f" %(point_all / credit_all))
    table.add_row(["全部学年总计", credit_all, point_all,curGPA ])

    print table

    if(os.path.isfile('xmugpa.dat')):
        f = open('xmugpa.dat', 'rb')
        preGPA = float(pickle.load(f))
        if (preGPA == curGPA):
            print "GPA not changed!"
        else:
            print "GPA has changed, we will send you an e-mail."
            f.close()
            f = open('xmugpa.dat', 'wb')
            if (sendMail(table)):
                pickle.dump(curGPA, f)
        f.close()
    else:
        f = open('xmugpa.dat', 'wb')
        print "Create new GPA record file, we will send you an e-mail"
        if (sendMail(table)):
            pickle.dump(curGPA, f)
        f.close()


def sendMail(table):
    mail_msg = table.get_html_string(attributes = {"class": "foo"})
    message = MIMEText(mail_msg,'html','utf-8')
    message['From'] = Header(mail_user,'utf-8')
    message['To']= Header(mail_receivers, 'utf-8')
    subject = u'您的成绩已更新'
    message['Subject'] = Header(subject,'utf-8')
    try:
        if (mail_useSSL):
            smtpObj = smtplib.SMTP_SSL()
        else:
            smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host,mail_port)
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(mail_user, [mail_receivers], message.as_string())
        smtpObj.close()
        print "Sending Mail Succeeded"
        return True
    except smtplib.SMTPException:
        print "Error: Sending Mail Failed"
        print traceback.format_exc()
    return False

def main():
    reload(sys)
    sys.setdefaultencoding('utf8')
    login()


if __name__ == '__main__':
    main()