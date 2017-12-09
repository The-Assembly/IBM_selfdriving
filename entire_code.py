from mpu6050 import mpu6050
import RPi.GPIO as GPIO
import time
from time import sleep
import threading
import ibmiotf.device
import bluetooth
GPIO.setwarnings(False)

server_socket=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

port = 1
server_socket.bind(("",port))
server_socket.listen(1)


organization = "0j8hk9"
deviceType = "raspberryPi"
deviceId = "MyCar"
authMethod = "token"
authToken = "assembly_token"

MPU = mpu6050(0x68)
print (" waiting for the sensor to callibrate...")

GPIO.setmode(GPIO.BCM)#for now i set everything to board...
#NOTE: THESE MOTOR PINS ARE IN BCM MODE WHILE THE SENSORS ARE IN BOARD MODE
#motor A 
in1_pin = 4
in2_pin = 17
in3_pin = 18 #PWM for speed

#motor B 
in4_pin = 5
in5_pin = 6
#in6_pin = 18 #PWM for speed
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)
GPIO.setup(in5_pin, GPIO.OUT)
my_pwm=GPIO.PWM(in3_pin,100)
my_pwm.start(0)

def clockwise(fast):
    GPIO.output(in1_pin, True)    
    GPIO.output(in2_pin, False)
    GPIO.output(in3_pin, fast)
 
def counter_clockwise(fast):
    GPIO.output(in1_pin, False)
    GPIO.output(in2_pin, True)
    GPIO.output(in3_pin, fast)

def stop():
    GPIO.output(in1_pin, False)
    GPIO.output(in2_pin, False)
    GPIO.output(in4_pin, False)
    GPIO.output(in5_pin, False)
    GPIO.output(in3_pin,0)

def left():
    GPIO.output(in4_pin, False)
    GPIO.output(in5_pin, True)

def right():
    GPIO.output(in4_pin, True)
    GPIO.output(in5_pin, False)

def straight():
    GPIO.output(in4_pin, False)
    GPIO.output(in5_pin, False)

INR = 1
USS = 0
X1 = 0
Y1 = 0
Z1 = 0

TRIG = 27
ECHO = 13
Irar = 23

GPIO.setup(TRIG,GPIO.OUT)
GPIO.output(TRIG,0)
GPIO.setup(Irar, GPIO.IN)

GPIO.setup(ECHO,GPIO.IN)
sleep(0.1)

def myOnPublishCallback():
    print ("Confirmed event received by IoTF\n")
# Initialize the device client.
deviceOptions = {"org": organization, "type": deviceType, "id": deviceId, "auth-method": authMethod, "auth-token": authToken}
client = ibmiotf.device.Client(deviceOptions)
print ("init successful")

# Connect and send a datapoint "hello" with value "world" into the cloud as an event of type "greeting" 10 times
def send(data):
    success = client.publishEvent("data", "json", data, qos=0, on_publish=myOnPublishCallback)
    if not success:
        print ("Not connected to IoTF")

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

         X1 = (accel_data['x'])/9.80665
         Y1 = (accel_data['y'])/9.80665
         Z1 = (accel_data['z'])/9.80665     

         sleep(0.5)

def IR_sens():
    global INR
    
    while True: 
        IR = GPIO.input(Irar)
    
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
        print(USS, INR ,'{0:.2f}'.format(X1), '{0:.2f}'.format(Y1), '{0:.2f}'.format(Z1))
        client.connect()
        send({"IR": INR, "US": USS, "acc_x": X1, "acc_y": Y1, "acc_z":Z1 })
        client.disconnect()
        sleep(0.5)

client_socket,address = server_socket.accept()
print"Accepted connection from ",address


if __name__=='__main__':
    t1 = threading.Thread(target=MPU6050)
    t2 = threading.Thread(target=IR_sens)
    t3 = threading.Thread(target=ultra)
    t4 = threading.Thread(target=printing)
    t1.start()
    t2.start()
    t3.start()
    t4.start()


while 1:

    
    data1 = client_socket.recv(1024)
    print "Received: %s" % data1

    

    if (data1 == "f"):
        print ("forward")
        my_pwm.ChangeDutyCycle(20)
        clockwise(20)
    
    if (data1 == "b"):
        print ("backwards")
        my_pwm.ChangeDutyCycle(20)
        counter_clockwise(20)
    
    if (data1 == "l"):    
        print ("left")
        left()
         
    if (data1 == "r"):
        print ("right")
        right()

    if (data1 == "p"):        
        print ("pause")
        stop()
    
    if (data1 == "s"):
        print ("straight")
        straight()


