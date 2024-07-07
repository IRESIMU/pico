import network
import socket
import time
import machine

# Wi-Fi credentials
ssid = 'Warp Gate'
password = 'entaroadun'

led = machine.Pin("LED", machine.Pin.OUT)  # Replace 15 with the GPIO pin you are using
url = "g1.carige.xyz"
port = 80
addr_info = ()
addr = ()

# Function to connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        led.value(1)
        print('Connecting to network...')
        time.sleep(0.5)
        led.value(0)
        time.sleep(0.1)
    print('Network connected:', wlan.ifconfig())
    network.hostname("demoPico01")
    return wlan

# Function to perform HTTP GET request
def http_get(adc_value):
    s = socket.socket()
    #print(addr)
    s.connect(addr)
    path = f"/s2s.php?rpi=pico&adc={adc_value}"
    request = f"GET {path} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
    s.send(request.encode())
    s.close()

# Function to read ADC value
def read_adc():
    adc = machine.ADC(0)  # Initialize ADC on pin 31 (GP26)
    adc_value = adc.read_u16()  # Read ADC value (0-65535)
    return adc_value

# Main function
def main():
    global addr
    connect_to_wifi()
    addr_info = socket.getaddrinfo(url, port)
    addr = addr_info[0][-1]
    #print(addr)
    while True:
        adc_value = read_adc()
        #print(adc_value)
        http_get(adc_value)
        led.value(1)
        time.sleep(0.02)
        led.value(0)
        time.sleep(1)

# Run the main function
main()