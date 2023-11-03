# ba_meta require api 7
#CNS_Proxy Server by inkMedic
#Discord: Medic#3158
#python codes by wsdx233
import _ba
import ba
# ba_meta export plugin
class CNS_Proxy(ba.Plugin):
    def on_app_running(self):
        def new_master(source=-1,version=1):
            if source in (-1,0):
                if version == 1:
                    return "http://cn.bombsquadgame.com"
                elif version == 2:
                    return "https://cns.inker.ga"
            else:
                if version == 1:
                    return "http://cn.bombsquadgame.com"
                elif version == 2:
                    return "https://cns.inker.ga"
        ba.internal.get_master_server_address = new_master
        print("CNS Proxy is running")