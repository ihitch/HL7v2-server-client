import socket
import matplotlib.pyplot as plt
import datetime
from datetime import datetime as date
import hl7

obxs = None

def plot(x,y,unit,parameter):
    #x = range(1,len(y)+1)
    plt.plot(x, y) 
    plt.xlabel('x - Time') 
    plt.ylabel('y - Value in '+ unit) 
    plt.title(parameter) 
    plt.show() 

def obr_generating(message,msgCID):
    global obxs
    message = message.split('|')
    dt = datetime.datetime.now()
    dt1 = dt.strftime("%Y%m%d%H%M%S")
    msgCID = dt.strftime("%Y%m%d") + str(msgCID).zfill(6)
    message_hl7 = 'MSH|^~\&|NIHON KOHDEN|NIHON KOHDEN|CLIENT APP|CLIENT FACILITY|'+str(dt1)+'||ORU^R01^ORU_R01|' + str(msgCID) + '|P|2.4|||NE|AL|Japan|ASCII||ASCII\n'
    message_hl7 = message_hl7 + 'PID|||' + str(message[0]) + '||^^^^^^L^A|||O\n' + 'PV1||I|^^OR-1^10.2.56.5:1\n' + 'ORC|RE\n'
    message_hl7 = message_hl7 + 'OBR|1|||VITAL|'+str(dt1)+'|'+str(message[2]) +'|'+ str(message[3])+'||||||||||||||||||A\n'
    obxs = message[1].split(' & ')
    for i in range(len(obxs)):
        message_hl7 = message_hl7 + 'OBX|1|NM|'+ str(obxs[i])+'||||||||||||||\n'
    message_hl7 = message_hl7 + 'MSH|^~\&|||||||ACK^R01^ACK|' + str(msgCID) + '|P|||||||ASCII||ASCII\n'+'MSA|AA|' + str(msgCID)
    return message_hl7

def client_program():
    host = socket.gethostname() 
    port = 5000  

    client_socket = socket.socket()  
    client_socket.connect((host, port))  

    message = input(" -> ")
    msgCID = 1
        
    while message.lower().strip() != 'q':
        try:
            message_hl7 = obr_generating(message,msgCID)
            client_socket.send(message_hl7.encode()) 
            data = client_socket.recv(8388608).decode() 

            print('Received from server: \n' + data)
            data = str(data)
            if data != 'Wrong query':
                client_socket.send('Message was successfully received.'.encode())
            data = data.replace('\n','\r')
            data = hl7.parse(data)
            values = list()
            times = list()
            unit = ''
            counter = 0
            l = open('/Users/jaroslav/Desktop/E-health/Loinc/unique_words.txt','r')
            loinc = l.read()
            loinc = loinc.split('\n')
            obx_old = obxs[0]
            for ii in range(len(obxs)):
                for yy in range(len(loinc)):
                    loinc_line = loinc[yy].split('|')
                    if str(obxs[ii]) == str(loinc_line[0]) and str(loinc_line[1]) != '':
                        obxs[ii] = str(loinc_line[1])
            for k in range(len(data)):
                if str(data[k][0]) == 'OBX' and str(data[k][3]) == str(obxs[0]):
                    counter += 1
                    if counter == 1:
                        unit = str(data[k][6])
                    values.append(float(str(data[k][5])))
                    dtt = date.strptime(str(data[k][14]),'%Y%m%d%H%M%S')
                    dttres = dtt.strftime('%H:%M')
                    times.append(dttres)

            if str(obxs[0]) != str(obx_old):
                nazev = str(obx_old) +'; LOINC CODE: '+str(obxs[0])
            else:
                nazev = str(obxs[0])
            plot(times,values,str(unit),nazev)

            message = input(" -> ")
            msgCID = msgCID + 1
            if message != 'q':
                message_hl7 = obr_generating(message,msgCID)

        except:
            print('Cannot process this request.')
            break

    client_socket.close()

if __name__ == '__main__':
    client_program()


#2011021|001000^VITAL HR & 058000^VITAL ICP(S)|20110616122516|20110616123016   --- PID| parametry, které lze oddělovat & | počáteční čas | konečný čas
# parametr který stojí na prvním místě se později vykreslí do grafu
# 2011021|058000^VITAL ICP(S)|20110616122516|20110616123016