# Released under the MIT License. See LICENSE for details.
#汉化by edMedic
#QQ2091341667
#Email：medic163@163.com/edmedic@outlook.com
#禁止未经授权用于开服
#授权id：82B51274EA94336EB3D7DDEA4D1E738D
from playersData import pdata
import ba
import ba.internal





def clientid_to_accountid(clientid):
	"""
	Transform Clientid To Accountid 
	
	Parameters:
		clientid : int
	
	Returns:
		None 
	"""
	for i in ba.internal.get_game_roster():
		if i['client_id'] == clientid:
			return i['account_id']
	return None





def check_permissions(accountid, command):
	"""
	Checks The Permission To Player To Executive Command
	
	Parameters:
		accountid : str
		command : str
	
	Returns:
		Boolean
	"""
	roles = pdata.get_roles()

	if is_server(accountid):
		return True

	for role in roles:
		if accountid in roles[role]["ids"]  and "ALL" in roles[role]["commands"]:
			return True

		elif accountid in roles[role]["ids"] and command in roles[role]["commands"]:
			return True
	return False


def is_server(accid):
	for i in ba.internal.get_game_roster():
		if i['account_id']==accid and i['client_id']==-1:
			return True