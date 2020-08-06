# By Somsak Lima and Itti  Srisumalai
import machine
import time, ubinascii
import utime as time
from machine import UART, Pin, ADC
from cayennelpp import CayenneLPP
from Fssd1306 import SSD1306_I2C

led = Pin(2, Pin.OUT)
relay1 = Pin(12, Pin.OUT)

WaterValue = 1200  # WaterValue = 1680;
AirValue = 3035  # AirValue = 3620;

i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21))
oled = SSD1306_I2C(128, 64, i2c)
uart = UART(2, 115200, timeout=300)
pot = ADC(Pin(34))
pot.atten(ADC.ATTN_11DB)  # Full range: 3.3v

rstr = ""

def sendATcommand(ATcommand):
    print("Command: {0}\r\n".format(ATcommand))
    uart.write("{0}\r\n".format(ATcommand))
    rstr = uart.read().decode("utf-8")
    print(rstr)
    return rstr

def Oledhello():
    oled.show_text(0, 0, "Hello", 12)
    oled.show_text(0, 20, "LoRaWAN Thailand", 16)
    oled.show_text(0, 35, "Start OTA Join", 16)
    oled.show()

Oledhello()
sendATcommand("AT")
sendATcommand("AT+INFO")
sendATcommand("AT+APPEUI")
sendATcommand("AT+DEVEUI")
sendATcommand("AT+APPKEY")
sendATcommand("AT+NCONFIG")
sendATcommand("AT+CHSET")
sendATcommand("AT+NRB")

while rstr != "+CGATT:1":
    rstr = sendATcommand("AT+CGATT")
    time.sleep(20.0)
    print("Respond String")
    print(rstr)
    if rstr.startswith("+CGATT:1"):
        print("++++OTAA OK+++++")
        break
    print("Retry OTAA Continue")
print("Join Success")
oled.clear()
oled.show_text(0, 24, "Join Success", 16)
oled.show()
time.sleep(5.0)

count = 1
while True:
    print("\r\n\r\nPacket No #{}".format(count))
    pot_value = pot.read()

    percent = 100 - (100 * (pot_value - WaterValue) / (AirValue - WaterValue))
    print("                Soil Moisture (%):" + str(percent))
    percentT = str(round(percent, 2))
    print("Round Soil Moisture to 2 digid(%):" + percentT)

    oled.clear()
    oled.show_text(0, 0, "#", 24)
    oled.show_text(10, 0, str(count), 24)
    oled.show_text(30, 24, percentT, 24)
    oled.show_text(78, 24, "%   ", 24)
    oled.show()
    c = CayenneLPP()
    c.addAnalogInput(1, round(percent, 2))
    b = ubinascii.hexlify(c.getBuffer())
    print("************    Sending Data Status   **************")
    led.value(1)
    ATresp = sendATcommand(
        "AT+NMGS={0},{1}".format(
            int(len(b.decode("utf-8")) / 2),
            (ubinascii.hexlify(c.getBuffer())).decode("utf-8"),
        )
    )
    print("********Finish Sending & Receiving Data Status******")
    led.value(0)
    count = count + 1
    time.sleep(10.0)

