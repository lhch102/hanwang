# -*- coding: utf-8 -*-

import datetime
import json

import pymysql
import requests

html = 'http://210.51.169.193:8080'
# 登录 url
loginUrl = html + '/login.whtml'
userCardInfoUrl = html + '/selfProcess/queryCurrentUserCardInfo.whtml'


# 通过用户名／密码获取cookies
def login(userName, password):
    '''
        登录信息  json.dumps	将 Python 对象编码成 JSON 字符串
                json.loads	将已编码的 JSON 字符串解码为 Python 对象
    '''
    jsonData = json.dumps(
        {
            'user': {
                'userName': userName,
                'password': password
            },
            'loginURL': html + '/login.html'
        }
    )

    userAgent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36'
    headers = {
        'User-Agent': userAgent,
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    responseIndex = requests.Session().post(loginUrl, data=jsonData, headers=headers)
    return responseIndex


# queryUrl = 'http://210.51.169.193:8080/system/queryCurrentUserInfo.whtml'
# responseUserInfo = requests.get(queryUrl, cookies=cookies)
def resultData(type, userName, password):
    responseIndex = login(userName, password)
    data = json.loads(responseIndex.text)
    if data['success']:
        # 提取cookies
        cookies = {c.name: c.value for c in responseIndex.cookies}
        # 没有此用户，爬取本月甚至所有的考勤
        if type == 0:
            userId = data['result']['id']
            name = data['result']['realName']
            # 插入用户表中
            insertUser = "insert into user values ('%d','%s','%s','%s') " % (userId, name, userName, password)
            # 连接MYsql
            connectionDataBase(insertUser, '')
        # 开始爬取数据
        responseIserCardInfo(type, cookies)
        return 0
    else:
        return data['message']


def getUser(userNameInput, passwordInput):
    # 查询当前登录用户是否存在；存在：直接爬取当天考勤，如果不存在，则爬取所有记录
    selectUser = "select user_name,password from user where user_name = %s" % (userNameInput)
    userList = connectionDataBase(selectUser, 'execute')
    if len(userList) > 0:
        userName = userList[0][0]
        password = userList[0][1]
        if (userNameInput != userName) or (passwordInput != password):
            return "用户名或密码错误"
        result = resultData(1, userName, password)
    else:
        result = resultData(0, userNameInput, passwordInput)
    # 正确
    if result == 0:
        selectUserInfo = "SELECT b.emp_name,a.date,a.working_time,a.off_time,a.day_type,a.week " \
                         "from attendance_info a, user b where a.user_id = b.id " \
                         "AND b.user_name = %s " \
                         "AND a.date = current_date()" % (userNameInput)
        userListInfo = connectionDataBase(selectUserInfo, 'execute')[0]
        return userListInfo
    else:
        return "用户名或密码错误"


def responseIserCardInfo(type, cookies):
    if type == 0:
        firstDay = getFirstDay()
        taday = currentDate()
    else:
        firstDay = taday = currentDate()
    jsonData = {
        'cardQueryParameter.begin': firstDay,
        'cardQueryParameter.end': taday,
        'start': 0,
        'count': 31
    }
    # 爬取考勤
    responseIserCardInfoUrl = requests.Session().post(userCardInfoUrl, data=jsonData, cookies=cookies)
    result = responseIserCardInfoUrl.text
    resultJson = json.loads(result)
    items = resultJson['items']
    userId = items[0]['userId']
    for dict in items:
        date = dict['date']
        periodCardInfoList = dict['periodCardInfoList']
        card = periodCardInfoList[0]['card']
        if len(periodCardInfoList) == 2:
            # 前面的时间
            working_time = card[:8]
            # 后面的时间
            off_time = periodCardInfoList[1]['card'][-9:][:-1]
        else:
            working_time = card[:8]
            if len(card) > 9:
                off_time = card[-9:][:-1]
            else:
                off_time = ''
        dayType = dict['dayType']
        week = dict['week']
        # 查询今天上班时间和下班时间
        tadayAttendance = "select working_time,off_time from attendance_info where user_id = %d and date = '%s'" % (
            userId, taday)
        tadayAttendanceList = connectionDataBase(tadayAttendance, 'execute')
        print("tadayAttendance:" + tadayAttendance)
        if len(tadayAttendanceList) > 0:
            if len(tadayAttendanceList[0]) > 0:
                if tadayAttendanceList[0][0] == '' and working_time != '':
                    updateWorkingTime = "update attendance_info set working_time = '%s' where user_id = %d and date = '%s'" % (
                        working_time, userId, taday)
                    result = connectionDataBase(updateWorkingTime, '')
                    print("updateWorkingTime:" + updateWorkingTime)
                if tadayAttendanceList[0][1] == '' and off_time != '':
                    updateOffTime = "update attendance_info set off_time = '%s' where user_id = %d and date = '%s'" % (
                        off_time, userId, taday)
                    result = connectionDataBase(updateOffTime, '')
                    print("updateOffTime:" + updateOffTime)
        else:
            # 将考勤明细插入数据库中
            insertAttendance = "insert into attendance_info " \
                               "(user_id,date,working_time,off_time,day_type,week) " \
                               "values (%d,'%s','%s','%s',%d,'%s')" \
                               % (userId, date, working_time, off_time, dayType, week)
            connectionDataBase(insertAttendance, '')


# 获取月初第一天的日期
def getFirstDay():
    datetimeDate = datetime.date
    getfirstDay = datetimeDate(datetimeDate.today().year, datetimeDate.today().month, 1)
    return getfirstDay


# 获取当前日期
def currentDate():
    # 今天的日期
    currentDate = datetime.datetime.today().date()
    return currentDate


def main():
    userName = '60000901'
    password = '60000901'
    # userName = '60000852'
    # password = '60000852'
    print(resultData(userName, password))


def connectionDataBase(sql, type):
    # 打开数据库连接
    conn = pymysql.connect(host='47.93.235.231',
                           port=3306,
                           user='lhch',
                           passwd='123456',
                           db='attendance',
                           charset='utf8',
                           use_unicode=True)
    # 使用 cursor() 方法创建一个游标对象 cursor
    cur = conn.cursor()
    try:

        # 使用 execute()  方法执行 SQL 查询
        cur.execute(sql)
        global result
        if type == 'execute':
            # 使用 fetchone() 方法获取单条数据.
            result = cur.fetchall()
        else:
            conn.commit()
    except ValueError as err:
        # 发生错误时回滚
        conn.rollback()
        print('Error: unable to fetch data', err)
    # 关闭数据库连接
    cur.close()
    conn.close()
    return result


if __name__ == '__main__':
    main()
