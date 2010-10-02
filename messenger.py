#!/usr/bin/python 

import json 
import time 
import urllib2

debug = 1 

class Messenger :
	def __init__( self, ckey , csecret ) : 
		""" Initilize  messenger class for use with the API """ 
		self.ckey = ckey 
		self.csecret = csecret 
		self.login_base = "https://login.yahoo.com"
		self.login_api_base = "https://api.login.yahoo.com"
		self.messenger_api_base = "http://developer.messenger.yahooapis.com"
		self.STATUS_AVALIABLE="0"
		self.STATUS_BUSY="2"
		self.STATUS_IDLE="999"
		self.STATUS_OFFLINE="-1"
		self.current_presense = self.STATUS_OFFLINE 
		self.current_statusmesg =None 



	def login (self, user='user' , password='password' ) :
		""" Login to yahoo messenger """
		self.user=user
		self.password=password
		req_tok = self.getRequestToken()
		self.oauth_tok = self.exchangeRequestTokenForOauthToken( req_tok ) 
		self.session = self.startSession()  
		#we are online now 
		self.current_presense = self.STATUS_ONLINE
		self.current_statusmesg = None 



	def getRequestToken(self) :
		url = self.login_base + "/WSLogin/V1/get_auth_token?"
		url += "&login=" + self.user 
		url += "&passwd=" + self.password
		url += "&oauth_consumer_key=" + self.ckey

		if debug :
			print "getRequestToken : " + url 

		resp = urllib2.urlopen(url).read()
		
		if debug : 
			print "getRequestToken : "+ resp 
		return resp.split('=')[1]


	def exchangeRequestTokenForOauthToken(self , token ) :
		req_tok = "oauth_token=" + token + "&oauth_token_secret=" + ""
		oauth_req = OauthReq( self.ckey , self.csecret , req_tok ) 
		url = self.login_api_base + "/oauth/v2/get_token?"
		url += oauth_req.getOauthParams()

		resp = urllib2.urlopen(url).read()
		return  OauthReq(self.ckey , self.csecret , resp )

	def startSession( self ) :
		url = self.messenger_api_base + "/v1/session?" 
		url += self.oauth_tok.getOauthParams()
		headers = { 'Content-Type':'application/json;charset=utf-8' } 
		data = '{}'

		req = urllib2.Request(url , data , headers  )

		json_resp = urllib2.urlopen(req).read()
		print json_resp 

		return MessengerSession(json_resp)



	def send_message(self , to  ,  message ) :
		url = self.messenger_api_base  + "/v1/message/yahoo/" + to  + "?"
		url += "sid=" + self.session.getsessionId()
		url += self.oauth_tok.getOauthParams()

		headers = { 'Content-Type':'application/json;charset=utf-8' } 

		data = '{ "message" : "' + message + '" }'

		req = urllib2.Request(url , data , headers  )

		urllib2.urlopen(req)
	

	def setPresence(self , status , mesg=None) :
		
		
		url = self.messenger_api_base  + "/v1/presence?" + self.session.getsessionId()
		url += self.oauth_tok.getOauthParams() 


		headers = { 'Content-Type':'application/json;charset=utf-8' } 

		data = '{ "presenceState" : "' + status + '",' 
		
		if mesg : 
			data += '{ "presenceMessage" : "' + mesg + '"' 

		data += '}'

		req = urllib2.Request(url , data , headers  )
		urllib2.urlopen(req)

		self.current_presense = status 
		self.current_statusmesg = mesg


	def getContacts(self) : 
		url = self.messenger_api_base  + "/v1/contacts?sid=" + self.session.getsessionId()  
		
		resp = urllib.urlopen(url).read()

		return resp 






class MessengerSession:
	def __init__(self , json_data ) :
		self.session_data = json.loads(json_data)
		
	
	def getsessionId(self) :
		return self.session_data['sessionId']

	def getNotifyServer(self) :
		return self.session_data['notifyServer']




class OauthReq :

	def __init__(self,ckey , secret , t=None ) :
		if ( t ) :
			self.token={}
			for m  in t.split('&')  : 
				( key , val ) =  m.split('=')
				self.token[key]=val

		self.token['ckey']=ckey 
		self.token['secret'] =secret
		

	def getOauthParams(self):
		params = ""
		params += "&oauth_consumer_key=" + self.token['ckey']
		params += "&oauth_signature_method=PLAINTEXT" 
		params += "&oauth_signature=" + self.token['secret'] + '%26' + str(self.token['oauth_token_secret'])
		params += "&oauth_auth_version=1.0" 
		params += "&oauth_nonce=123456" 
		params += "&oauth_timestamp=" + str(int(time.time())) 
		params += "&oauth_token=" + self.token['oauth_token']
		return params 


	def UpdateToken(self , t ) :
		#self.token = dict( m.split('=') for m in t.split('&') )
		for m  in t.split('&')  : 
				( key , val ) =  m.split('=')
				self.token[key]=val


	def RefreshToken(self):
		self.token['oauth_token_secret']=''
		url = self.login_api_base + '/oauth/v2/get_token?'
		url+=self.getOauthParams()
		url+="&oauth_session_handle=" +  self.token['oauth_session_handle']

		print url 

		resp = urllib2.urlopen(url).read()

		self.UpdateToken(resp)
	



