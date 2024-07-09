import argparse
import socket
import os
import struct
import time
import select
import sys,_thread,traceback, ssl



ICMP_ECHO_REQUEST = 8
timeRTT = []
packageSent = 0
packageRev = 0

MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


timeTraceRTT = []
tracePackageSent = 0
tracePackageRev = 0
count=0
loss=0



def setupArgumentParser() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='A collection of Network Applications developed for SCC.203.')
        parser.set_defaults(func=Proxy, hostname='lancaster.ac.uk')
        subparsers = parser.add_subparsers(help='sub-command help')
        
        parser_p = subparsers.add_parser('ping', aliases=['p'], help='run ping')
        parser_p.set_defaults(timeout=4)
        parser_p.add_argument('hostname', type=str, help='host to ping towards')
        parser_p.add_argument('--count', '-c', nargs='?', type=int,
                              help='number of times to ping the host before stopping')
        parser_p.add_argument('--timeout', '-t', nargs='?',
                              type=int,
                              help='maximum timeout before considering request lost')
        parser_p.set_defaults(func=ICMPPing)

        parser_t = subparsers.add_parser('traceroute', aliases=['t'],
                                         help='run traceroute')
        parser_t.set_defaults(timeout=4, protocol='icmp')
        parser_t.add_argument('hostname', type=str, help='host to traceroute towards')
        parser_t.add_argument('--timeout', '-t', nargs='?', type=int,
                              help='maximum timeout before considering request lost')
        parser_t.add_argument('--protocol', '-p', nargs='?', type=str,
                              help='protocol to send request with (UDP/ICMP)')
        parser_t.set_defaults(func=Traceroute)

        parser_w = subparsers.add_parser('web', aliases=['w'], help='run web server')
        parser_w.set_defaults(port=8080)
        parser_w.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_w.set_defaults(func=WebServer)

        parser_x = subparsers.add_parser('proxy', aliases=['x'], help='run proxy')
        parser_x.set_defaults(port=8000)
        parser_x.add_argument('--port', '-p', type=int, nargs='?',
                              help='port number to start web server listening on')
        parser_x.set_defaults(func=Proxy)

        args = parser.parse_args()
        return args

class NetworkApplication:

    def checksum(self, dataToChecksum: str) -> str:
        csum = 0
        countTo = (len(dataToChecksum) // 2) * 2
        count = 0

        while count < countTo:
            thisVal = dataToChecksum[count+1] * 256 + dataToChecksum[count]
            csum = csum + thisVal
            csum = csum & 0xffffffff
            count = count + 2

        if countTo < len(dataToChecksum):
            csum = csum + dataToChecksum[len(dataToChecksum) - 1]
            csum = csum & 0xffffffff

        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)

        answer = socket.htons(answer)

        return answer

    def printOneResult(self, destinationAddress: str, packetLength: int, time: float, ttl: int, destinationHostname=''):
        if destinationHostname:
            print("%d bytes from %s (%s): ttl=%d time=%.2f ms" % (packetLength, destinationHostname, destinationAddress, ttl, time))
        else:
            print("%d bytes from %s: ttl=%d time=%.2f ms" % (packetLength, destinationAddress, ttl, time))

    def printAdditionalDetails(self, packetLoss=0.0, minimumDelay=0.0, averageDelay=0.0, maximumDelay=0.0):
        print("%.2f%% packet loss" % (packetLoss))
        if minimumDelay > 0 and averageDelay > 0 and maximumDelay > 0:
            print("rtt min/avg/max = %.2f/%.2f/%.2f ms" % (minimumDelay, averageDelay, maximumDelay))


class ICMPPing(NetworkApplication):
    
    def checksum(self,str):
        csum = 0
        countTo = (len(str) / 2) * 2
        count = 0
        while count < countTo:
            thisVal = str[count + 1] * 256 + str[count]
            csum = csum + thisVal
            csum = csum & 0xffffffff
            count = count + 2
        if countTo < len(str):
            csum = csum + str[len(str) - 1].decode()
            csum = csum & 0xffffffff
        csum = (csum >> 16) + (csum & 0xffff)
        csum = csum + (csum >> 16)
        answer = ~csum
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer


    def receiveOnePing(self,mySocket, ID, sequence, destAddr, timeout):
        timeLeft = timeout
        global packageRev, timeRTT

        #this loop will check whether the packet is received in the required timeout if the packet is received in the required timeout this will proceed to get the data from packet 

        while 1:
            startedSelect = time.time()
            whatReady = select.select([mySocket], [], [], timeLeft)
            howLongInSelect = (time.time() - startedSelect)
            if whatReady[0] == []:
                return None

            timeReceived = time.time()
            #we will receive the packet from port number 1024
            recPacket, addr = mySocket.recvfrom(1024)

            # Fill in start
            header = recPacket[20: 28]
            #unpack the packet to get the information like type,code,checksum,packetID, sequence of packet
            type, code, checksum, packetID, sequence = struct.unpack("!bbHHh", header)
            #now check if the type of the replied pccke is type 3 which means Echo Reply and then unpack the data from packet received
            if type == 0 and packetID == ID: 
                byte_in_double = struct.calcsize("!d")
                timeSent = struct.unpack("!d", recPacket[28: 28 + byte_in_double])[0]
                timeRTT.append(timeReceived-timeSent)
                packageRev += 1
                           
                delay = timeReceived - timeSent
                ttl = ord(struct.unpack("!c", recPacket[8:9])[0].decode())
                return (delay, ttl, byte_in_double)
                #type 3 means destination host/network unreachable
            elif(type==3):
                   print("Destination Host/Network Unreachable")
                   return None
                
            timeLeft = timeLeft - howLongInSelect
            if timeLeft <= 0:
                return None


    def sendOnePing(self,mySocket, ID, sequence, destAddr):

        ##the function sendOnePing will send one ping to the destination address using socket.
        myChecksum = 0
        ## this line will create header for the packet to be sent
        header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
        # this line will create data part of the packet adding current time also.
        data = struct.pack("!d", time.time())
        myChecksum = self.checksum(header + data)
        ## for security reason checksum will be calculated to create the final header of the packet to be sent.
        header = struct.pack("!bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, sequence)
        packet = header + data
        # finally packet will be sent to against the given socket.
        mySocket.sendto(packet, (destAddr, 1)) 


    def doOnePing(self,destAddr, ID, sequence, timeout):
            #getting the protocol for the ICMP protocol.
        icmp = socket.getprotobyname("icmp")
        # will create a raw socket because raw socket is most powerfull socket in networking
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        #this will call sendOnePing function find the given destination address.
        self.sendOnePing(mySocket, ID, sequence, destAddr)
        #this line will get the response of the packet that was sent using sendOnePing() and that message will return the delay 
        delay = self.receiveOnePing(mySocket, ID, sequence, destAddr, timeout)
        mySocket.close()
        return delay

    def __init__(self, args):
        
        print('Ping to: %s...' % (args.hostname))
        host=args.hostname
        timeout=1

        dest = socket.gethostbyname(host)
        print("Pinging " + dest + " using Python:")
        print("")
        myID = os.getpid() & 0xFFFF  
        loss = 0
        #this loop will send 4 consecutive ping requests and fetch the results and show them
        for i in range(4):
            result = self.doOnePing(dest, myID, i, timeout)
            if not result:
                print("Request timed out.")
                loss += 1
            else:
                delay = int(result[0]*1000)
                ttl = result[1]
                bytes = result[2]
                self.printOneResult(args.hostname,int(bytes),float(delay),int(ttl))

        time.sleep(1)
        #this will show the statics of the ping result.
        print("Packet: sent = " + str(4) + " received = " + str(4-loss) + " lost = " + str(loss))
        print ('maxRTT:', (max(timeRTT) if len(timeRTT) > 0 else 0), \
            '\tminRTT:', (min(timeRTT) if len(timeRTT) > 0 else 0), \
            '\naverageRTT:', float((sum(timeRTT)
                                   / len(timeRTT) if len(timeRTT)
                                   > 0 else float('nan'))))
        self.printAdditionalDetails(loss,max(timeRTT),float(sum(timeRTT)/ len(timeRTT)),min(timeRTT))

        return


class Traceroute(NetworkApplication):
        #function build packe will create the packet to be sent to destination host.
        def build_packet(self):

            myChecksum = 0
            #this line will create the process id that will be used to identify that the packet we received was sent by us.
            #this will not send the packet just creat the packet and return it to the parent calling function.
            myID = os.getpid() & 0xFFFF
                #creating pacet header.
            header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
                #create the data packet using the current time.
            data = struct.pack("d", time.time())
                #calculate the checksum to ensure the security
            myChecksum = self.checksum(header+data)    
            header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, myID, 1)
            packet = header + data
            return packet
        
        

        
        def get_route(self,hostname):
            timeLeft = TIMEOUT
            #this function will send the packet to next host untill the our destination is reached this will send two packet to each upcoming host to confirm that is the actual host
            #there will be two loops one for the maximum number of hops and the second loop will try the same next hope two times
            global tracePackageSent,tracePackageRev, timeTraceRTT
            try:     
                for ttl in range(1,MAX_HOPS):
                    for tries in range(TRIES):
                            #get the destination IP address address of the destination.
                        destAddr = socket.gethostbyname(hostname)
                        #get the protocol for ICMP socket
                        icmp = socket.getprotobyname("ICMP")
                        #creating raw socket
                        mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
                        mySocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
                        # if timeout is negative or becomes 0 then it will return from this function
                        if(TIMEOUT<=0):
                                return None
                        mySocket.settimeout(TIMEOUT)
                        #this loop will build and send packet to the next hope and keep sending the request to next hope untill destination is reached
                        try:
                            d = self.build_packet()
                            mySocket.sendto(d, (hostname, 1))
                            tracePackageSent+=1
                            t = time.time()
                            
                            startedSelect = time.time()
                            
                            whatReady = select.select([mySocket], [], [], timeLeft)
            
                            howLongInSelect = (time.time() - startedSelect)
                            if whatReady[0] == []: 
                                print ("*    *    * Request timed out.")
                                
            
                            recvPacket, addr = mySocket.recvfrom(1024)
                            tracePackageRev+=1

                            timeReceived = time.time()
                            timeLeft = timeLeft - howLongInSelect
            
                            if timeLeft <= 0:
                                print ("*    *    * Request timed out.")
                                return None
                        except socket.timeout:
                            continue
                        else:
                                #this will unpack the data from the packet and get required information.
            
                            icmpHeader = recvPacket[20:28]
                            request_type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
            
                            #this part is important because it may send different types of packets
                            #because if the next hope is not known the the router it will then send discovery packets to the next connected routers.
                            #it will send type 11 (Time Exceeded), type 3(destination unreachable) & type 0(Echo Reply)
                            # so we have to pick all the packets that belongs to us(sent by us)
                            if request_type == 11:
                                bytes = struct.calcsize("d")
                                timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                self.printOneResult(addr[0],bytes,(timeReceived-t)*1000,ttl)
                                timeTraceRTT.append((timeReceived-t)*1000)                                
                                count+1

                            elif request_type == 3:
                                bytes = struct.calcsize("d")
                                timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                self.printOneResult(addr[0],bytes,(timeReceived-t)*1000,ttl)

                               
                                
                            elif request_type == 0:
                                bytes = struct.calcsize("d")
                                timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                                self.printOneResult(addr[0],bytes,(timeReceived-timeSent)*1000,ttl)

                                return
                            else:
                                print ("error")
                                break
                        finally:
                            mySocket.close()
        #if the user will inturrupt it by keyboard it will exit this function and return to the main function
            except KeyboardInterrupt:
                print("inturrupted by keyboard..")
                print("Exiting!!!")
                return None

        

        def __init__(self, args):
                
                print('Traceroute to: %s...' % (args.hostname))
                #call the function get_route() to get the route to destination
                self.get_route(args.hostname)
                #this will print the statistics of the whole process displaying minimum time, average time, max time
                print ('maxRTT:', (max(timeTraceRTT) if len(timeTraceRTT) > 0 else 0), \
                            '\tminRTT:', (min(timeTraceRTT) if len(timeTraceRTT) > 0 else 0), \
                            '\naverageRTT:', float((sum(timeTraceRTT)
                                                   / len(timeTraceRTT) if len(timeTraceRTT)
                                                   > 0 else float('nan'))))
                print("Packets Sent:",tracePackageSent)
                print("Packets Loss:",tracePackageSent-tracePackageRev)
                self.printAdditionalDetails(tracePackageSent-tracePackageRev,min(timeTraceRTT),float(sum(timeTraceRTT)/ len(timeTraceRTT)),max(timeTraceRTT))



class WebServer(NetworkApplication):
        
        

        def handleRequest(self):
            HOST = '127.0.0.1'
            PORT = 8080
            # Create server socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the server socket to server address and server port
            server_socket.bind((HOST, PORT))
            server_socket.listen(1)
            print(f"Starting server at http://{HOST}:{PORT} ...")
            #Continuously listen for connections to server socket
            while True:
                client_socket, client_address = server_socket.accept()
                # Receive request message from the client on connection socket
                request = client_socket.recv(1024).decode()
                print(request)
                
                try:
                        # Extract the path of the requested object from the message (second part of the HTTP header)
                        headers = request.split('\n')
                        filename = headers[0].split('/')[1]
                        print(filename)
                        filename=filename.split(' ')
                       
                        filename="/"+filename[0]
                except:
                        print("error parsing file please restart server")
                        return

                if filename == '/':
                    filename = '/index.html'

                try:
                    # file inside public directory. ex. public/index.html
                     # Read the corresponding file from disk
                    client_file = open(f'public{filename}')
                    #  Store in temporary buffer
                    file_content = client_file.read()
                    client_file.close()
                   
                    # Send the correct HTTP response error
                    response = f"HTTP/1.0 200 OK\n\n{file_content}"
                except FileNotFoundError:
                    response = 'HTTP/1.0 404 NOT FOUND\n\n<h1>ERROR 404: File Not Found...</h1>'
                except KeyboardInterrupt:
                        print("inturrupted by keyboard..")
                        print("Exiting!!!")
                 # Send the content of the file to the socket
                client_socket.sendall(response.encode())
                # Close the connection socket
                client_socket.close()
            # Close server socket
            server_socket.close()

        def __init__(self,args):
                    #print('Web Server starting on port: %i...' % (args.port))
                    self.handleRequest()
            
class Proxy(NetworkApplication):
        #this function will decode the incoming packet to identify the client address and client request and the port number on which the packet has to arrive. 
        def conn_string(self,conn, data, addr):
            try: 
                print(addr)
                first_line = data.decode("utf-8").split("\n")[0]
                print(first_line)
                url = first_line.split(" ")[1]
         
                http_pos = url.find("://")
                if http_pos == -1:
                    temp = url
                else:
                    temp = url[(http_pos + 3):]
         
                port_pos = temp.find(":")
                webserver_pos = temp.find("/")
                if webserver_pos == -1:
                    webserver_pos = len(temp)
                webserver = ""
                port = -1
                if port_pos == -1 or webserver_pos < port_pos:
                    port = 80
                    webserver = temp[:webserver_pos]
                else:
                    port = int(temp[(port_pos + 1):][:webserver_pos - port_pos -1])
                    webserver = temp[:port_pos]
         
                print(webserver)
                self.proxy_server(webserver,port,conn,data,addr)
            except Exception as e:
                print(e)
                traceback.print_exc()
         #this function will implement the actual functionality of a proxy server
        def proxy_server(self,webserver, port, conn, data, addr):
            print("{} {} {} {}".format(webserver, port, conn, addr))
            try:
                    #create the server socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((webserver, port))
                s.send(data)
                #loop to continuosly listen for receiving requests.
                while 1:
                    reply = s.recv(buffer_size)
                 
                    if len(reply) > 0:
                        #reply to the client with requested data
                        conn.sendall(reply)
                        print("[*] Request sent: {} > {}".format(addr[0],webserver))
                    else:
                        break        
         
                s.close()
                conn.close()
         
            except Exception as e:
                print(e)
                traceback.print_exc()
                s.close()
                conn.close()
                sys.exit(1)
        
        

        def __init__(self, args):
                print('Web Proxy starting on port: %i...' % (8000))
                global listen_port, buffer_size, max_conn
                #listen on the port
                try:
                        listen_port = 8000
                except KeyboardInterrupt:
                        sys.exit (0)
                #limit of the maimum connection that can be made and buffer size to store request data temporarily
                max_conn = 10000
                buffer_size = 10000
                try:
                        #creat the server socket on the given port
                        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        #bind and listen to on socket
                        s.bind(("", listen_port))
                        s.listen(max_conn)
                        print("Server started successfully [{}]".format(listen_port))
                except Exception as e:
                        print(e)
                        sys.exit(2)
                 #listen connections and receive requests form client 
                while True:
                        try:
                            conn,addr = s.accept()
                            data = conn. recv(buffer_size)
                            #initialize threading
                            _thread.start_new_thread(self.conn_string,(conn, data, addr))
                        except KeyboardInterrupt:
                            s.close()
                            print("\nShutting down...")
                            sys.exit(1)
                s.close()



if __name__ == "__main__":
    args = setupArgumentParser()
    args.func(args)
