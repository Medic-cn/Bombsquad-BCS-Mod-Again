# Released under the MIT License. See LICENSE for details.
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
import ba, _ba
import ba.internal
from serverData import serverdata
from features import profanity
from tools import servercheck
import time
import setting
from tools import logger
import _thread
from playersData import pdata
settings = setting.get_settings_data()

def check_permissions(accountid):
	roles = pdata.get_roles()
	for role in roles:
		if accountid in roles[role]["ids"]  and ( role == "bypass-warn" or role=="owner") :
			return True
	return False


def filter(msg,pb_id,client_id):
	new_msg=profanity.censor(msg)
	if new_msg!=msg:
		_ba.screenmessage("警告:不要刷屏!!!", color=(1,0,0), transient=True, clients=[client_id])
		if not check_permissions(pb_id):
			addWarn(pb_id,client_id)
		else:
			_ba.screenmessage("<您是特殊玩家，警告已失效>", color=(0,1,0), transient=True, clients=[client_id])

	now = time.time()
	if pb_id not in serverdata.clients:
		return None

	if "lastMsgTime" in serverdata.clients[pb_id]:
		count=serverdata.clients[pb_id]["cMsgCount"]
		smsgcount=serverdata.clients[pb_id]['cSameMsg']
		if now - serverdata.clients[pb_id]["lastMsgTime"] < 8:
			count+=1
			if count == 2: #when 3 msgs
				_ba.screenmessage("别发这么快，让我冷静下....", color=(1,0.40,0.50), transient=True, clients=[client_id])
			elif count >=3: #when 4 msgs
				_ba.screenmessage("警告:不要刷屏!!!", color=(1,0,0), transient=True, clients=[client_id])
				if not check_permissions(pb_id):
					addWarn(pb_id,client_id)
				else:
					_ba.screenmessage("<您是特殊玩家，警告已失效>", color=(0,1,0), transient=True, clients=[client_id])
				count =0
		elif now - serverdata.clients[pb_id]["lastMsgTime"] < 20:
# < 30
			if serverdata.clients[pb_id]["lastMsg"]==msg:
				if len(msg)>5:
					smsgcount+=1
					if smsgcount>=3:
						logger.log(pb_id+" | 刷屏 被踢")
						ba.internal.disconnect_client(client_id)
						smsgcount=0
				_ba.screenmessage("警告:不要刷屏!!", color=(1,0,0), transient=True, clients=[client_id])
				if not check_permissions(pb_id):
					addWarn(pb_id,client_id)
				else:
					_ba.screenmessage("<您是特殊玩家，警告已失效>", color=(0,1,0), transient=True, clients=[client_id])
			else:
				smsgcount=0
		else:
			count =0
			smsgcount=0


		serverdata.clients[pb_id]['cMsgCount']=count
		serverdata.clients[pb_id]['lastMsgTime']=now
		serverdata.clients[pb_id]['lastMsg']=msg
		serverdata.clients[pb_id]['cSameMsg']=smsgcount
	else:
		serverdata.clients[pb_id]['cMsgCount']=0
		serverdata.clients[pb_id]['lastMsgTime']=now
		serverdata.clients[pb_id]['lastMsg']=msg
		serverdata.clients[pb_id]['cSameMsg']=0
	return new_msg



def addWarn(pb_id,client_id):
	now=time.time()
	player=serverdata.clients[pb_id]
	warn=player['warnCount']
	if now - player['lastWarned'] <= settings["WarnCooldownMinutes"]*60:
		warn+=1
		if warn > settings["maxWarnCount"]:
			_ba.screenmessage(settings["afterWarnKickMsg"],color=(1,0,0),transient=True,clients=[client_id])
			logger.log(pb_id+"  | 刷屏 被踢出")
			ba.internal.disconnect_client(client_id)
			_thread.start_new_thread(servercheck.reportSpam,(pb_id,))
			
		else:
			_ba.screenmessage(settings["warnMsg"]+f"\n\n警告次数已达到 {warn}/3!!!",color=(1,0,0),transient=True,clients=[client_id])
	else:
		warn=0
	serverdata.clients[pb_id]["warnCount"]=warn
	serverdata.clients[pb_id]['lastWarned']=now



