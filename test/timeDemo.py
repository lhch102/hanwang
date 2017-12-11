# -*- coding: utf-8 -*-
import datetime, time


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


if __name__ == '__main__':
    # print(getFirstDay())
    # a = 10
    # b = 100
    # 09:20:27
    working_time = '10:20:27'
    date1 = datetime.datetime.strptime(working_time, "%H:%M:%S")
    date2 = datetime.datetime.strptime('9:05:59', "%H:%M:%S")
    s = date1 - date2
    s.strftime('%Y-%m-%d')
    print(s)
