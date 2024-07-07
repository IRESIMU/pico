import machine
import ubinascii

random_bytes = machine.unique_id()
uuid = ubinascii.hexlify(random_bytes).decode()
    
print(uuid)
