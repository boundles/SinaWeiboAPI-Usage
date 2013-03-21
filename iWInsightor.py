#-*-coding:UTF-8-*-

from weibo import APIClient
from re import split
import urllib,httplib
import webbrowser
import operator
import numpy as np
import matplotlib.pyplot as plt

class iWInsightor(object):
    def __init__(self,ID,PW):
        self.ACCOUNT = ID
        self.PASSWORD = PW
        self.CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'
        self.APP_KEY = 'XXXXXX' #your key
        self.APP_SECRET = 'XXXXXXXX' #your secret
        self.client = APIClient(app_key=self.APP_KEY, app_secret=self.APP_SECRET, redirect_uri=self.CALLBACK_URL)
        self.url = self.client.get_authorize_url()
        self.get_Authorization()
    
    def get_code(self):  
        conn = httplib.HTTPSConnection('api.weibo.com')
        postdata = urllib.urlencode({'client_id':self.APP_KEY,'response_type':'code','redirect_uri':self.CALLBACK_URL,'action':'submit','userId':self.ACCOUNT,'passwd':self.PASSWORD,'isLoginSina':0,'from':'','regCallback':'','state':'','ticket':'','withOfficalFlag':0})
        conn.request('POST','/oauth2/authorize',postdata,{'Referer':self.url,'Content-Type': 'application/x-www-form-urlencoded'})
        res = conn.getresponse()
        location = res.getheader('location')
        code = location.split('=')[1]
        conn.close()
        return code
    
    def get_Authorization(self):
        code = self.get_code()
        r = self.client.request_access_token(code)
        access_token = r.access_token
        expires_in = r.expires_in
        self.client.set_access_token(access_token, expires_in)

    #发送微博消息   
    def post_weibo(self,message):
        self.client.post.statuses__update(status=message.decode('gbk'))
        
    #获取当前用户ID
    def getCurrentUid(self):
        try:
            uid = self.client.account.get_uid.get()['uid']
            return uid
        except Exception:
            print 'get userid failed'
            return

    #获取用户关注列表
    def getFocus(self,userid):
        focuses = self.client.get.friendships__friends(uid=userid,count=200)
        Resfocus = []
        for focus in focuses["users"]:
            try:
                Resfocus.append((focus["screen_name"],focus["gender"]))   
            except Exception:
                print 'get focus failed'
                return
        return Resfocus

    #获取用户标签
    def getTags(self,userid):
        try:
            tags = self.client.tags.get(uid=userid)
        except Exception:
            print 'get tags failed'
            return
        userTags = []
        sortedT = sorted(tags,key=operator.attrgetter('weight'),reverse=True)
        for tag in sortedT:
            for item in tag:
                if item != 'weight':
                   userTags.append(tag[item])
        return userTags

    #获取用户发布的微博
    def getWeibo(self,uesrid,infile):
        contents = self.client.get.statuses__user_timeline(uid=uesrid, count=100)
        for content in contents.statuses:
            try:
                f = open(infile,'a')
                f.write(content.text.encode('gbk'))
                f.write('\n')
                f.close()
            except Exception:
                print 'get text failed'

    def autolabel(self,rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x()+rect.get_width()/2., 1.03*height, '%s' % float(height))
    
    #画出用户的关注男女比例图
    def getSexplot(self,userid,m,f,n):
        res = self.client.get.users__show(uid=userid)
        ind = np.arange(1,4) 
        width = 0.25      
        plt.subplot(111)
        rects1 = plt.bar(left=ind, height=(m,f,n), width=0.25,align = 'center')

        plt.ylabel('The Focus Number')
        plt.title('Sex Analysis(effective samples:%d)' % (m+f+n))
     
        plt.xticks(ind, ("Male","Female","Unknown") )
        self.autolabel(rects1)
        plt.legend((rects1,),("User:%s" % res["screen_name"],))
        plt.show()
        
if __name__ == '__main__':
    usrID = raw_input('请输入新浪微博用户名：')
    usrPW = raw_input('请输入新浪微博密码:')
    AppClient = iWInsightor(usrID, usrPW)
    
    userid = AppClient.getCurrentUid()
    infile = "E://data/weibo.dat"
    AppClient.getWeibo(userid,infile)

    Focus = AppClient.getFocus(userid)
    m = 0
    f = 0
    n = 0
    for i in Focus:
        if i[1] == "m":
            m = m+1
        elif i[1] == "f":
            f = f+1
        else:
            n = n+1
    AppClient.getSexplot(userid,m,f,n)
