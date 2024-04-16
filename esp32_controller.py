import network
import socket
import time
import ujson
import uasyncio
from machine import Pin
from dht import DHT22
from config import PC


# Configurar pin de encendido
PIN_PC_ON = Pin(6, Pin.OUT)

# Configurar pin de sensor DHT22
dht = DHT22(Pin(17))

# Wifi piso
ssid_piso = "MiFibra-0A20-24G"
password_piso = "9XKrvXK2"

# Wifi casa
ssid_casa = "LowiC73C"
password_casa = "DH63H4KU676JPC"

# --------------------- Servidor web ----------------------

port = 80

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', port))
server.listen(5)

# ---------------------------------------------------------

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado a wifi")


def PC_ON():
    print("PC-ON")
    

def get_temp_humd():
    print("temp-humd")
    

def handle_client(client, address):
    request = client.recv(1024).decode('utf-8')
    request_lines = request.split('\n')
    method = request_lines[0].split(' ')[0]
    path = request_lines[0].split(' ')[1]
    
    print(f'Client: {address[0]}')
    print(request)
    
    if '/control' in path:
        if f'/control?secret_class={PC.ON_KEY}&on=ON' == path:
            # Encender PC
            PIN_PC_ON.on()
            time.sleep(0.5)
            PIN_PC_ON.off()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nPC encendido"
        else:
            response = "HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\n\r\nForbidden"
    elif path == '/getTempAndHumd':
        dht.measure()
        temperature = dht.temperature()
        humidity = dht.humidity()
        data = {'temperature': temperature, 'humidity': humidity}
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n" + ujson.dumps(data)
    else:
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + "<!DOCTYPE html><html><head><title>ESP32 Web Server</title></head><body><h1>ESP32 Web Server</h1></body></html>"

    client.sendall(response.encode('utf-8'))
    client.close()


def run_server():
    while True:
        client, addr = server.accept()
        handle_client(client, addr)


def main():
    connect_wifi(ssid_piso, password_piso)
    run_server()


if __name__ == '__main__':
    main()
