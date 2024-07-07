import machine
import time

def reboot_device(timer):
    print("Rebooting the device...")
    time.sleep(1)  # Optional: short delay before reboot
    machine.reset()

# Create a Timer object
reboot_timer = machine.Timer(-1)

# Schedule the reboot function to run periodically (every 6 hours)
# Timer period is in milliseconds, so 6 hours = 6 * 60 * 60 * 1000 milliseconds
REBOOT_INTERVAL_MS = 6 * 60 * 60 * 1000

reboot_timer.init(period=REBOOT_INTERVAL_MS, mode=machine.Timer.ONE_SHOT, callback=reboot_device)

while True:
    print("Device running...")
    time.sleep(1)  # Simulate doing other work