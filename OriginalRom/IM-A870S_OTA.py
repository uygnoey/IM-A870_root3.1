
#-*-coding:utf-8-*-
import httplib
global model, version

def xmlInf(Elements):
	from xml.dom.minidom import getDOMImplementation
	impl = getDOMImplementation()
	SKY_REQUEST = impl.createDocument(None, "SKY_REQUEST", None)
	Request = SKY_REQUEST.documentElement
	for Element in Elements:
		Ele = SKY_REQUEST.createElement(Element[0])
		Ele.appendChild(SKY_REQUEST.createTextNode(Element[1]))
		Request.appendChild(Ele)
	SKY_REQUEST.appendChild(Request)
	return SKY_REQUEST.toxml(encoding='UTF-8')

def getinfo(ResponseStr):
	from xml.dom import minidom
	import time
	data = time.strftime('%X %x')+"\n"
	SKY_RESPONSE = minidom.parseString(ResponseStr).documentElement
	data += "---------------------------------------------------------\n"
	SKY_CMD = SKY_RESPONSE.getElementsByTagName("SKY_CMD")[0]
	data += SKY_CMD.childNodes[0].nodeValue + "\t" +model+"\n"
	data += "---------------------------------------------------------\n"
	APK_INFO = SKY_RESPONSE.getElementsByTagName("APK_INFO")
	if str(APK_INFO) == "[]":
		print "Model Name\n"
		data = ""
		return data
	data += APK_INFO[0].nodeName + "\n"
	for node in APK_INFO[0].childNodes:
		if node.nodeType == node.ELEMENT_NODE:
			for info in APK_INFO:
				try:
					data += info.getElementsByTagName(node.nodeName)[0].nodeName
					if len(node.nodeName) >= 15:
						data += ":"
					else:
						data += ":\t" 
					data += str(info.getElementsByTagName(node.nodeName)[0].childNodes[0].nodeValue) + "\n"
				except:
					print "Error! Check Response.xml"
					o = open("Response.xml", 'wb')
					o.write(ResponseStr)
					o.close()
					data += "Error occured!!!\n"
	data += "---------------------------------------------------------\n"
	return data
	

if __name__ == "__main__":
	print "Model Name IM-A870S"
	model = "IM-A870S"
	version = "S0218138"
	RequestInf = [['SKY_CMD', 'GET_PKG_DETAIL_INFO'], ['TERMINAL_NAME', model], ['BOARD_SOFT_VER', version], ['PKG_NAME', 'com.pantech.firmware.bin.'+model]]
	xml = xmlInf(RequestInf)
	params = "--pkgname\nContent-Disposition:form-data;name=\"file\";filename=GET_PKG_DETAIL_INFO.xml\n\n" + xml + "\n--pkgname--"
	headers = {"Content-Type":"multipart/form-data;boundary=pkgname", "Connection":"Keep-Alive"}
	i = 0
	conn = httplib.HTTPConnection("apkmanager.skyservice.co.kr")
	data = ""
	while i < 10:
		try:
			conn.request(method="POST",url="/apkmanager/Process/sky_station_30_server.php",body=params,headers=headers)
			response = conn.getresponse()
			data = response.read()
			conn.close()
			break
		except:
			conn.close()
			i += 1
			print "Connection Error!, for the first"+str(i)+"Retry"
	if data != "":
		f = open("updateinfo.txt", "a")
		data = getinfo(data)
		f.write(data+"\n")
		f.close()
		
	if data != "":
		print data
		otaver = data[data.find("PKG_VERSIONNAME:")+16:][:data[data.find("PKG_VERSIONNAME:")+16:].find("\n")]
		size = data[data.rfind("PKG_SIZE:")+10:][:data[data.rfind("PKG_SIZE:")+10:].find("\n")]
		print "OTA Upgraded Version :" + str(otaver) + "\nSize :" + str(size)
		RequestOTA = [['SKY_CMD', 'GET_PKG_DOWN'], ['TERMINAL_NAME', model], ['BOARD_SOFT_VER', version], ['PKG_NAME', 'com.pantech.firmware.bin.'+model], ['PKG_VERSIONNAME', otaver]]
		xml = xmlInf(RequestOTA)
		params = "--read_stream:com.pantech.firmware.bin." +model+ "\nContent-Disposition:form-data;name=\"file\";filename=GET_PKG_DOWN.xml\n\n" + xml + "\n--read_stream:com.pantech.firmware.bin." + model +"--"
		headers = {"Content-Type":"multipart/form-data;boundary=read_stream:com.pantech.firmware.bin." + model, "Connection":"Keep-Alive"};
		i = 0
		conn = httplib.HTTPConnection("apkmanager.skyservice.co.kr")
		data = ""
		while i < 10:
			try:
				conn.request(method="POST",url="/apkmanager/Process/sky_station_30_server.php",body=params,headers=headers)
				response = conn.getresponse()
				file = open('OriginalRom/'+model+'_Update.zip', 'wb')
				done = 0.
				while True:
					tmp = response.read(100*1024)
					if not tmp:break
					file.write(tmp)
					done += 100*1024
					if done/int(size)>1:
						print "\r100%    "
					else:
						print "\r" + str(round(done/int(size)*100,2)) + "",
				file.close()
				conn.close()
				break
			except:
				conn.close()
				i += 1
				print "Connection Error!, for the first"+str(i)+"Retry"
