#!/usr/bin/python

import sys, getopt
import serial
import time

port = ""
apname = ""
solicited = "1"
remote_ip = ""
# UDP header 8 bytes, IP header 20 bytes
# To get 200 bytes application data, 200 - 28 = 172 bytes
data = "1234567890123456789112345678921234567893123456789412345678951234567896123456789712345678981234567899123456789012345678911234567892123456789312345678941234567895123456789712"

def main(argv):
   serialport = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.5)
   try:
      opts, args = getopt.getopt(argv,"hakn:trc",["","PLMN="])
   except getopt.GetoptError:
      print "energy_nbiot.py -a -k -n <1:PLMN, 0:Auto> -t -r -c"
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print "energy_nbiot -a -k -n <1:PLMN, 0:Auto> -t -r -c"
         sys.exit()
      elif opt == '-a':
	 print "inspect whether communication with NB-IoT module working"
         serialport.write("AT\r")
         response = serialport.readlines(None)
	 if response[1].replace('\r\n', '') == 'OK':
	    print "NB-IoT module working"
	 else:
	    print "NB-IoT module not working"
      elif opt == '-k':
         print "Reset NB-IoT module and set full radio functionality"
         # Reset
         serialport.write("AT+NRB\r")
         time.sleep(5)
         response = serialport.readlines(None)
	 # Set Full Radio Functionality
         serialport.write("AT+CFUN=1\r")
         time.sleep(2)
         response = serialport.readlines(None)
      elif opt in ("-n", "--PLMN"):
         print "Registration and Context Activation"
         plmn = arg
	 if plmn == '1':
	    print "Using Fix PLMN"
	    serialport.write("AT+CGDCONT=1,\"IP\",\"" + apname + "\"\r")
            response = serialport.readlines(None)
            serialport.write("AT+COPS=1,2,\"502153\"\r")
            response = serialport.readlines(None)
            t1 = time.time()
            while True:
               serialport.write("AT+CSCON?\r")
               response = serialport.readlines(None)
               if response[1] == '+CSCON:0,1\r\n':
                  break;
            t2 = time.time()
            print "Time taken for NB-IoT to connect to network: ", (t2 - t1), "seconds"
	 else:
	    print "Using Auto (Expect Delay)"

	    #modify add 010617
	    serialport.write("AT+CGDCONT=1,\"IP\",\"" + apname + "\"\r")
            response = serialport.readlines(None)
	    #modify add 010617

	    serialport.write("AT+CGATT=1\r")
            response = serialport.readlines(None)

	    #modify remove 010617
            #serialport.write("AT+COPS=1,2,\"502153\"\r")

            response = serialport.readlines(None)
            t1 = time.time()
            while True:
               serialport.write("AT+CSCON?\r")
               response = serialport.readlines(None)
               if response[1] == '+CSCON:0,1\r\n':
                  break
            t2 = time.time()
            print "Time taken for NB-IoT to connect to network: ", (t2 - t1), "seconds"
         while True:
            serialport.write("AT+CGPADDR=1\r")
            response = serialport.readlines(None)
	    #response = serialport.readlines(None)
	    #print response
            if "+CGPADDR:1," in response[1]:
               break
         ipaddr = response[1].replace('\r\n', '')
         print "IP address for NB-IoT module: ", ipaddr.split('+CGPADDR:1,',1)[1]
      elif opt in ("-t"):
	 data = #"1234567890123456789112345678921234567893123456789412345678951234567896123456789712345678981234567899123456789012345678911234567892123456789312345678941234567895123456789712"
	 print "NB-IoT UL Tx"
	 # Create Socket
         sock = "AT+NSOCR=DGRAM,17," + port + "," + solicited + "\r";
         serialport.write(sock)
         response = serialport.readlines(None)
         socket = response[1].replace('\r\n', '')
	 t1 = time.time()
	 # Send data
	 send = "AT+NSOST=" + socket + "," + remote_ip + "," + port + "," + str(len(data)) + "," + #data.encode("hex") + "\r"
         serialport.write(send)
         response = serialport.readlines(20)
	 t2 = time.time()
	 print "Time taken for NB-IoT to Tx: ", (t2 - t1), "seconds"
	 # Close socket
	 sock = "AT+NSOCL=" + socket + "\r";
         serialport.write(sock)
         response = serialport.readlines(None)
      elif opt in ("-r"):
	 print 'NB-IoT DL Rx'
	 # Create Socket
         sock = "AT+NSOCR=DGRAM,17," + port + "," + solicited + "\r";
         serialport.write(sock)
         response = serialport.readlines(None)
         socket = response[1].replace('\r\n', '')
         # Send data
         data = "1"
         send = "AT+NSOST=" + socket + "," + remote_ip + "," + port + "," + str(len(data)) + "," + #data.encode("hex") + "\r"
         serialport.write(send)
         response = serialport.readlines(20)
	 print response
         t1 = time.time()
	 # Read data
         if len(response) == 6:
            if "+NSONMI:" in response[5]:
               rlength = response[5].replace('\r\n', '')
               read = "AT+NSORF=0," + rlength.split(',')[1] + "\r"
               serialport.write(read)
               response = serialport.readlines(None)
               rdata = response[1].split(',')[4]
               print "Attempt to read: ", rdata.decode("hex")
	 t2 = time.time()
         print "Time taken for NB-IoT to Rx: ", (t2 - t1), "seconds"
         # Close socket
         sock = "AT+NSOCL=" + socket + "\r";
         serialport.write(sock)
         response = serialport.readlines(None)
      elif opt in ("-c"):
	 print "NB-IoT move to idle state"
   print "NB-IoT AT Command Triggering for Energy Consumption Evaluation"

if __name__ == "__main__":
   main(sys.argv[1:])
