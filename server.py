# skript serveru, stačí supustit ve složce se složkou nezpracovaných zpráv (HL7_v2_zpravy)
import socket
import hl7
import datetime
import shutil
import os

def preprocessing_msg(file):
    pa = '/Users/jaroslav/Desktop/E-health/HL7_v2_zpravy/'
    path = pa + file
    pa2 = 'messages/'
    path2 = pa2 + 'out_' + file
    with open(path) as infile, open(path2, 'w') as outfile:
        for line in infile:
            if not line.strip(): continue
            if line.strip("\n") != "Recv Timeout":
                if line.strip("\n") != "Connect!!!!!!!!!!!!":
                    outfile.write(line)
    f = open(path2,"r")
    content = f.read()
    content = content.replace("\n","\r")
    h = hl7.parse(content)
    for x in range(len(h)):
        if 'start' not in locals():
            if str(h[x][0]) == 'MSH':
                start = x
        if str(h[x][0]) == 'PID':
            pid = h[x][3]
        if str(h[x][0]) == 'MSA':
            konec = x
            path3 = 'messages_final/' + str(pid) + '.txt'
            soubor = open(path3,"a+")
            for i in range(start,konec+1):
                soubor.write(str(h[i])+"\r")
            if 'start' in locals():
                del start


def server_program():
    host = socket.gethostname()
    port = 5000  
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    conn, address = server_socket.accept()

    print("Connection from: " + str(address))

    while True:
        data = conn.recv(4096).decode()
        if not data:
            break
        print("from connected user: \n" + str(data))
        data = str(data)
        if data != 'Message was successfully received.':
            data = data.replace('\n','\r')
            client_message = hl7.parse(data)
            time_from = str(client_message.segment('OBR')[6])
            if time_from == '':
                time_from = 0
            time_to = str(client_message.segment('OBR')[7])
            if time_to == '':
                time_to = float("inf")
            try:
                f = open('/Users/jaroslav/Desktop/E-health/messages_final/' + str(client_message.segment('PID')[3]) + '.txt','r')
                file = f.read()
                file = file.replace("\n","\r")
                file = hl7.parse(file)
                message_out = ''
                for x in range(5):
                    message_out += str(client_message[x]) + '\n'

                for i in range(len(file)):
                    if str(file[i][0]) == 'OBX':
                        for y in range(len(client_message)):
                            if str(client_message[y][0]) == 'OBX':
                                if str(file[i][3]) == str(client_message[y][3]) and float(str(file[i][14])) >= float(time_from) and float(str(file[i][14])) <= float(time_to):
                                    message_out += str(file[i]) + '\n'

                message_out += str(client_message[len(client_message)-2]) +'\n' + str(client_message[len(client_message)-1])
                message_out = message_out.replace("\n","\r")
                message_out = hl7.parse(message_out)
                dt = datetime.datetime.now()
                dt1 = dt.strftime("%Y%m%d%H%M%S")
                message_out[0][7] = str(dt1)
                message_out1 = ''
                l = open('/Users/jaroslav/Desktop/E-health/Loinc/unique_words.txt','r')
                loinc = l.read()
                loinc = loinc.split('\n')
                for ii in range(len(message_out)):
                    for yy in range(len(loinc)):
                        loinc_line = loinc[yy].split('|')
                        if str(message_out[ii][0]) == 'OBX' and str(message_out[ii][3]) == str(loinc_line[0]) and str(loinc_line[1]) != '':
                            message_out[ii][3] = str(loinc_line[1])
                    message_out1 += str(message_out[ii]) + '\n'
                message_out1 = str(message_out1)

                conn.send(message_out1.encode())
            except:
                message_out = 'Wrong query'
                conn.send(message_out.encode())

    conn.close()

if __name__ == '__main__':
    dirName = 'messages'
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    dirName = 'messages_final'
    if not os.path.exists(dirName):
        os.mkdir(dirName)

    preprocessing_msg('comm_1.txt')
    preprocessing_msg('comm_2.txt')
    preprocessing_msg('comm_3.txt')
    preprocessing_msg('comm_4.txt')
    preprocessing_msg('comm_5.txt')
    dir_path = 'messages/'
    try:
        shutil.rmtree(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))

    print('- preprocessing done, starting server -')
    server_program()
