from machine import ADC, Pin
import time
import math
import os
import network
import socket
import json
import ubinascii
import urequests
import gc
import math
import array

# Wi-Fi credentials
ssid = 'Warp Gate'
password = 'entaroadun'

port = 80
addr_info = ()
addr = ()

mId = machine.unique_id()
mId = ubinascii.hexlify(mId).decode()

# Ensure the 'log' directory exists
if 'log' not in os.listdir():
    os.mkdir('log')

# Count the number of files in the 'log' directory
log_files = os.listdir('log')
log_count = len(log_files)

# Create a new file with an incremented name
filename = "log/log_{}.txt".format(log_count + 1)

# Open the file once before the loop starts
file = open(filename, "a")

# Initialize ADC (assuming ADC pin is connected to GP26)
adc = ADC(Pin(27))

# Sampling parameters
sampling_rate = 2000  # Hz
sampling_interval = 1 / sampling_rate
num_samples = 2000  # Number of samples to take

# Offset and conversion factors
offset = 0  # ADC offset in count
voltage_conversion_factor = 3.3 / 65535  # Assuming 3.3V reference and 16-bit ADC
current_conversion_factor = 30  # 1V = 30A

led = Pin("LED", machine.Pin.OUT)

g23 = Pin(23, Pin.OUT)
g23.value(1)

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

def get_peak_value(samples):
    return max(samples)

def get_min_value(samples):
    return min(samples)

def get_average_value(samples):
    return sum(samples) // len(samples)

def sample_ac_signal():
    samples = []
    for _ in range(num_samples):
        adc_value = adc.read_u16()
        samples.append(adc_value)
        time.sleep(sampling_interval)
    return samples


def moving_average(data, window_size):
    smoothed_data = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        window_average = sum(window) / window_size
        smoothed_data.append(window_average)
    return smoothed_data

try:
    connect_to_wifi()
    
    while True:
        led.value(0)
        samples = sample_ac_signal()
        led.value(1)
        
        #print(samples)
        
        window_size = 25  # Adjust the window size as needed
        smoothed_data = moving_average(samples, window_size)

        peak_read = get_peak_value(samples)
        min_read = get_min_value(samples)
        avg_readRaw = get_average_value(smoothed_data)
        avg_read = avg_readRaw - offset - min_read

        #because we are reading ONLY half sine wave, multiply by 2
        
        # Convert average ADC reading to voltage and current
        avg_voltage = (avg_read) * voltage_conversion_factor * 2
        avg_current = avg_voltage * current_conversion_factor
        
        # Store the values in the buffer
        #buffer = ("Peak Read: {}, Min Read: {}, Avg Read: {}, Avg Tension: {:.4f} V, Avg Current: {:.4f} A\n".format(
        #     peak_read, min_read, avg_read, avg_voltage, avg_current))
        
        data = {
            "Peak": peak_read,
            "Min": min_read,
            "Avg": avg_read,
            "Raw": avg_readRaw,
            "off" : offset,
            "V": round(avg_voltage, 4),
            "A": round(avg_current, 4)
        }
        
        json_data = json.dumps(data)

        
        url = f"http://g1.carige.xyz/s2s.php?mId={mId}"
        
        response = urequests.post(url, data=json_data)
        
        
        for line in samples:
            file.write(str(line) + "\n")
        #file.write(samples)
        file.flush()
        print(json_data)
        gc.collect()

        # Sleep before the next round of sampling, 5min is a reasonable value for the boiler
        #time.sleep(300)
finally:
    # Make sure to close the file when done (although in this loop, it will run indefinitely)
    file.close()