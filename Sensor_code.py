from mpu6050 import mpu6050
import RPi.GPIO as GPIO
import time
from time import sleep
import threading
import ibmiotf.device

organization = "towqb0"
deviceType = "raspberryPi"
deviceId = "MyCar"
appId = deviceId + "_receiver"
authMethod = "token"
authToken = "assembly_token"

MPU = mpu6050(0x68)
print (" waiting for the sensor to callibrate...")

GPIO.setmode(GPIO.BOARD)

INR = 1
USS = 0
X1 = 0
Y1 = 0
Z1 = 0

TRIG = 13
ECHO = 12

GPIO.setup(TRIG,GPIO.OUT)
GPIO.output(TRIG,0)
GPIO.setup(11, GPIO.IN)

GPIO.setup(ECHO,GPIO.IN)
sleep(0.1)

def myOnPublishCallback():
    print "Confirmed event received by IoTF\n"

# Initialize the device client.
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
client = ibmiotf.device.Client(deviceOptions)
print "init successful"

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
def send(data):
	
	success = client.publishEvent("data", "json", data, qos=0, on_publish=myOnPublishCallback)
	if not success:
		print "Not connected to IoTF"

def MPU6050():
    global X1
    global Y1
    global Z1
        
    while True:
         accel_data = MPU.get_accel_data()
         #print("Accelerometer data")
         #print("x: " + str(accel_data['x']))
         #print("y: " + str(accel_data['y']))
         #print("z: " + str(accel_data['z']))

         X1 = str(accel_data['x'])
         Y1 = str(accel_data['y'])
         Z1 = str(accel_data['z'])         

         sleep(0.5)

def IR_sens():
    global INR
    
    while True: 
        IR = GPIO.input(11)
    
        if IR == 1:
            #print("0")
            INR = 0
            

        elif IR == 0:
            #print("1")
            INR = 1

        sleep(0.5)   

        

def ultra():
    global USS
              
    while True:
            #print("tt")
              GPIO.output(TRIG, False)                 #Set TRIG as LOW
            ##print ("Waitng For Sensor To Settle")
              #sleep(2)                       #Delay of 2 seconds

              GPIO.output(TRIG, True)                  #Set TRIG as HIGH
              sleep(0.00001)                      #Delay of 0.00001 seconds
              GPIO.output(TRIG, False)                 #Set TRIG as LOW

              while GPIO.input(ECHO)==0:               #Check whether the ECHO is LOW
                pulse_start = time.time()              #Saves the last known time of LOW pulse
                #print("0")
                
              while GPIO.input(ECHO)==1:               #Check whether the ECHO is HIGH
                pulse_end = time.time()                #Saves the last known time of HIGH pulse 
                #print("1")

              pulse_duration = pulse_end - pulse_start #Get pulse duration to a variable

              distance = pulse_duration * 17150        #Multiply pulse duration by 17150 to get distance
              distance = round(distance, 2)            #Round to two distances
              #print(distance)
              USS = distance
              #print (distance)
              sleep(0.5)

             

def printing():
    while True:
        print(USS, INR ,X1, Y1, Z1)
        client.connect()
        send({'IR':INR, "US": USS, "X": X1, "Y": Y1, "Z": Z1 })
        client.disconnect()
        sleep(0.5)
        

        
if __name__=='__main__':
    t1 = threading.Thread(target=MPU6050)
    t2 = threading.Thread(target=IR_sens)
    t3 = threading.Thread(target=ultra)
    t4 = threading.Thread(target=printing)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
   # 
   # mp = Process(target = MPU6050)
   # ir = Process(target = IR_sens)
   # us = Process(target = ultra)
   # pr = Process(target = printing)

    
    #pr.start()
    #mp.start()
    #ir.start()
    #us.start()

    
    
    
