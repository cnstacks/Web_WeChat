from flask import Flask, render_template, session, jsonify
import requests
import time
import re

app = Flask(__name__)

app.secret_key = "1231sdfasdf"
from bs4 import BeautifulSoup


def xml_parse(text):
    result = {}
    soup = BeautifulSoup(text, 'html.parser')
    tag_list = soup.find(name='error').find_all()
    for tag in tag_list:
        result[tag.name] = tag.text
    return result


@app.route('/login')
def login():
    ctime = int(time.time() * 1000)
    qcode_url = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}".format(
        ctime)
    rep = requests.get(
        url=qcode_url,

    )
    qcode = re.findall('uuid = "(.*)";', rep.text)[0]
    # qcode = re.findall('uuid = "(.*)";', rep.text)[0]
    session['qcode'] = qcode
    return render_template('login.html', qcode=qcode)


@app.route('/check/login')
def check_login():
    qcode = session['qcode']
    ctime = int(time.time() * 1000)
    check_login_url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip=0&r=-976036168&_={1}'.format(
        qcode, ctime)
    rep = requests.get(
        url=check_login_url
    )
    result = {'code': 408}
    if 'window.code=408 ' in rep.text:
        # 用户未扫码;
        result['code'] = 408
    elif 'window.code=201' in rep.text:
        # 用户扫码，获取头像；
        result['code'] = 201
        result['avatar'] = re.findall("window.userAvatar = '(.*)';", rep.text)[0]
    elif 'window.code=200' in rep.text:
        redirect_uri = re.findall('window.redirect_uri="(.*)";', rep.text)[0]
        print(redirect_uri)
        # https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AX1MQULQ88Eu8UBNTaGWLo_k@qrticket_0&uuid=4ZamPqjrWw==&lang=zh_CN&scan=1536713739
        redirect_uri = redirect_uri + "&fun=new&version=v2"
        ru = requests.get(
            url=redirect_uri
        )
        print(
            ru.text)  # <error><ret>0</ret><message></message><skey>@crypt_7f94ab6d_09c6f5c641735b9d508b2973de7e1c73</skey><wxsid>dxtAt/oUed7drgJw</wxsid><wxuin>2150889942</wxuin><pass_ticket>DgAlY28j5CsCBMamz1h0FU42CAK6Bn%2BLk888LtaZnsOlckkPWFpgMu0KBFY91IUi</pass_ticket><isgrayscale>1</isgrayscale></error>
        ticket_dict = xml_parse(ru.text)
        session['ticket_dict'] = ticket_dict
        result['code'] = 200
    return jsonify(result)


@app.route('/index')
def index():
    pass_ticket = session['ticket_dict']['pass_ticket']
    init_url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=880750577&lang=zh_CN&pass_ticket={0}".format(pass_ticket)
    return render_template('index.html')
    requests.post(
        url=init_url,
        json={
            'BaseRequest':{

            }
        }
    )

if __name__ == '__main__':
    app.run()

'''
window.code=201;window.userAvatar = 'data:img/jpg;base64,/9j/4AAQSkZJRgABAQAASABIAAD/2wBDAAcFBQYFBAcGBgYIBwcICxILCwoKCxYPEA0SGhYbGhkWGRgcICgiHB4mHhgZIzAkJiorLS4tGyIyNTEsNSgsLSz/2wBDAQcICAsJCxULCxUsHRkdLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCwsLCz/wAARCACEAIQDASIAAhEBAxEB/8QAGwAAAQUBAQAAAAAAAAAAAAAAAAECAwQGBQf/xAA5EAABAwIEBAEKBQMFAAAAAAABAAIDBBEFEiFRBhMxQWEUFSJEUnGSobHRI0KBkcEHMkMzNGJy8f/EABoBAAIDAQEAAAAAAAAAAAAAAAACAQMEBQb/xAAqEQACAgECBQMDBQAAAAAAAAAAAQIRAwQSBRMhMVEUQXEiI2EyM6HB8f/aAAwDAQACEQMRAD8A80DUoCcAnWXqjxdDQEXTrIspIsbdFvBOsiyAsZZF0+yRAUMskIUlrpCFBNkRCSykskIUDWQkJCFIRqkISjpkJKaSpbJpCVliZEW6oT7IQNZ0bJcqWyWyuMFiWRZOsjKgi6obZFk6yLICxmTwRlT7JLIJsZY7JLqSyaSglMZdNIUhCSygZMiITSFKQm2SsdMiCaQpSEwhKOmR2QnEaoUDWdGyUBSZUob4K6zFTI7IspciMqLDayKyS6myppZqiwpkd0llLkGyMtkBTIrpLKYt0TS1Fk0yIhNIUuRIWqLG6kJCQhSlqaWqBupE4phGimLUwhKx1ZCeqE8t1QlGOxkShqscpAjU2TsIMqMisGPwSthc9wa1pLibAAalFhsKuVJkXY8wYiXlgpiXNOUjMLg7dU2bAsRgjL5aORrR1JHhf+FG9eSNhyciQsVgxkI5ZTWG0rZU0sVrlnZNMevRFk7CrlSFqtthc94Yxpc5xsABckq07AsUsD5tq7HoeS7X5JXNIaOGT7M5BYmlq6c+FV1M0unoqiIDqXxkAfuFTLPBG6weNruiqWpharRYmFiiydpWshTGPVCLDaaLlJREuj5Md1YosKkrZ8jAABq5x6NCp3mjacynoKirkLKaCSd4Fy2Nhcbb2C1vAXDcr+JmT4hTSxMpWmVjZYy3O/t1Ha9/0XWw2CHDx5NTNyty5nvP9zzpqf36K3z5IpWzROLZGG7SqZzck0iMc4xkm+tCcY4I6GUYtR2Ycw5rb2Dj9/8AzZTYTh5NIJqjLI6VvbUWP2VOvnq8RmkqqyYPDATFE3Rkem3c+JVHDqrEqPmRUkjeVIDo8X5ZP5m/boq9s3j231GU8Uc/Mrp/fkxuL4NLQYtU0zI3vZG8hpAJ06jX3Fc8wkGxaQR2XqNMPJYQ0PJd1Liep7lZjFMP8vdNUx6ztkfmHtC5+a0Rm+zKm4uXwZMxadErKWSY2jjc8js0XXWosKnr6tlPAzM937AbnxXpWB4MzBYeRT2Ly28knQvOny2CTLnWNfk6ej4fPVPwl7mS/pzw4ajHZK6ric1tC0PY17bZnnoddrE++y2WKUZpKptXDI1kbzZ7HGwvuFbkEzSHteQ9urSufJSzVFVJW1rxK8A8tg0bGNgP5XLy5HkluZ6vQaNaTona9/yWKyCKroH08lpI5mEEjUEEdl4nXYfJRVs1NIDmieWXt1t3XrTJ5aFr4oB+E7oD/j8W/ZXY8UbFTtiiYYw0b6p8GZ4rKtdw16pp3VHhpiTDGvQuI+GhVw+cqJn4rm5pox+bdw8d1jDTnZdOGVTVo8vqdHPTT2T/ANOaY0Locg7ITbzLsNt5EfZUkEMlNMJI9CPmtN5tHso82j2Vg5xv5BQinGYy2tdmW2xuEeU3Cs1dKKeDMR1K5xsei0Qe5WcnNDlTcSZ8wdDI0d2n6JkczYmBrRqoXH0Xe4qO5HdOU2W3TktK5cExY6XKMzuY42/VW2uJXRpcNY6mY9rAM4zGw6kpJz2IvwYudPr7HJwyrnw6vfOGAsl0kaBa4v2W1pKmKotLG67XMP1K4hwwbKzQU7qV7yCQC3p+oWLI1Lqeq4fllifKfZ/wdV79dSoJXgRP17FV3yHcqF7yWO17LOehUQc8bAlNyRnUtCjz2Ts4IQWFasrY6CgY4elKW+gz+T4LGTUzp5nyvAzPJcbC2q1E1EZpHPNzc6X2UJw3wWrHJQR5TXZpaidPsjMeQ+CFpfNp2QreYYOUegchuyTkN3Vu6SwXPs30Z7iGINo4+13/AMLPEWWm4oNqSG3tn6LMZl0tP+hHA1v7zFLfRPuUdgpC8Bh07KPO3ZXmIXoFrcNgBwymO8Y+iyIsStrh1hhlML/42/VZdT2R0+HL638DjTBQVEIjhJCulw3VWteDBpusNnodMvuwOU9Md/pu9yVztUxzhkd7kHoyMWIQSB0TLFH5UDUdGCnDqdjtylNKFYpP9nF/1CedUWeVyL638FE0rb9EK5ZCLEo7ZBHZRvJHZXMqQxNd1ASWNRlOJH3p4R/yP0WcuVvsQwCLE2tBmfFlJPogG65p4GhPr0vwBb8OaEYJI4+q0uTJkcoroZGR34Z1UbBmK2J4EhOnl0vwBOHA0LRYVsnwBXeox+TL6LN4MfmDQSu9SV8go4W66MA+Svu4FiPrz/gH2XQp+H4KaFkeZ0mUAXOl1nz5YzSSN+i0+TFJubOKa2TYprap02Zp7C60fmuD2FE/A4JQcrjGT3CyWjtYGo5FJmbc5RPdoVozwxEfWn/CEw8Kxn1p/wAIRaO0tXi8mbLrJhkAWkdwmw+tv+EJh4Ri71cnwhFon1mHycumrjy2sHbRXGzOcFchwCCnFs7nncqyKCNo0CizhZOsm0c0Od4oXS8mYPyoRZXR10qEJQHtTkITIgEIQpIBRuCEJSWJZAGqEIHQ6yQoQoHGprkIQBCQmHqhCBRpGqEIUkH/2Q==';
'''
