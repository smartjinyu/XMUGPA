#!/usr/bin/python
# -*- coding=utf-8 -*-


__author__ = 'smartjinyu'


import requests
import re
import getpass
from bs4 import BeautifulSoup
from prettytable import PrettyTable
id
def login(pwd):
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
    if u'登录须知：' in html.text:
        print "Login Failed, please check your id or password."
    else:
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
    while i < len(indexList):
        print trList[indexList[i]].find('b').getText() #2015-2016年度第三学期
        table = PrettyTable([u'课程名称',u'学分',u'成绩',u'绩点'])
        table.padding_width = 5
        table.align[u'课程名称'] = "1"
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
        print table
        if credit != 0:
            print ('本学期参与绩点计算的学分:%-5.1f 本学期总绩点:%-5.1f 本学期GPA:%-5.5f'%(credit,point,point/credit))
        else:
            print ('本学期参与绩点计算的学分:0.0 本学期总绩点:0.0 本学期GPA:0.00000')
        print
        point_all += point
        credit_all += credit
        i += 1
    print ('总计参与绩点计算的学分:%-8.1f 总绩点:%-8.1f GPA:%-5.5f' % (credit_all, point_all, point_all / credit_all))

def main():
    global id
    id = raw_input('Please input your XMU Student Id:')
    pwd = getpass.getpass('Please input the corresponding password:')
    login(pwd)

if __name__ == '__main__':
    main()