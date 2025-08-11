# 🚀 IoT Using MicroPython – Environment Setup

This section helps you set up everything you need to get started with IoT projects using MicroPython on ESP8266, ESP32, or ESP32-CAM.

---

## 🔌 Hardware Requirements

- ESP8266 (e.g., NodeMCU) or ESP32/ESP32-CAM board  
- Micro-USB cable (data-enabled)  
- Optional: Breadboard, sensors, jumper wires  

---

## 💻 Software Requirements

### 1. Install Python (v3.7 or higher)

- 📥 [Download Python](https://www.python.org/downloads/)
- During installation, make sure to check **“Add Python to PATH”**

```bash
python --version
pip --version
```

---

### 2. Install MicroPython Tools

#### a. `esptool` – for flashing firmware

```bash
pip install esptool
```

#### b. `mpremote` – for REPL access & file transfer

```bash
pip install mpremote
```

> Optional tools:  
> - `ampy` (file upload tool)  
> - `thonny` (IDE with MicroPython support)

---

### 3. Download MicroPython Firmware

📦 Get firmware from the official site:  
👉 [https://micropython.org/download](https://micropython.org/download)

Save the `.bin` file to a known directory like:

- `~/firmware/` on macOS/Linux  
- `C:\firmware\` on Windows

---

### 4. Put Board into Flash Mode

For ESP8266 or ESP32:
- Hold down the **BOOT** button
- While holding it, press and release **EN/RESET**
- Then release the **BOOT** button

---

### 5. Flash MicroPython Firmware

Replace `COM3` (on Windows) or `/dev/ttyUSB0` (on macOS/Linux) with your actual port.

```bash
# Erase flash
esptool.py --port COM3 erase_flash

# Flash firmware
esptool.py --port COM3 --baud 460800 write_flash --flash_size=detect 0x0 firmware/esp8266-xxxx.bin
```

---

### 6. Connect to the Board with MicroPython

Use `mpremote` to open a REPL session:

```bash
mpremote connect COM3
```

Try a test command:

```python
>>> print("Hello MicroPython!")
```

---

## 🌐 Using WebREPL Locally (No HTTPS Blocking)

The online WebREPL client (`https://micropython.org/webrepl`) won’t connect to your ESP over `ws://` due to browser mixed-content restrictions.  
**Solution:** run the WebREPL client locally.

### 1. Clone This Repository
```bash
git clone https://github.com/<your-username>/IoT-Using-MicroPython.git
cd IoT-Using-MicroPython/webrepl_client
```

### 2. Start a Local HTTP Server
```bash
python3 -m http.server 8000
```

### 3. Connect to ESP8266 AP
Join the ESP’s access point (SSID `MicroPython-xxxx`).

### 4. Open the Client
In your browser:
```
http://localhost:8000/webrepl.html#192.168.4.1:8266
```
Click **Connect**, enter your WebREPL password.

---

### 📂 `webrepl_client` Directory Contents
```
webrepl_client
├── FileSaver.js
├── term.js
├── webrepl.css
├── webrepl.html
└── webrepl.js
```
> These files are from the official [micropython/webrepl](https://github.com/micropython/webrepl) repo and allow you to run WebREPL entirely offline.

---

## 🤖 Why This Matters for Robotics & IoT

With WebREPL running locally:
- You can **control circuits** and peripherals on your ESP wirelessly
- Upload new control scripts without USB cables
- Send live commands to a robot or IoT device over Wi-Fi

Example:
```python
from machine import Pin
motor = Pin(5, Pin.OUT)
motor.value(1)  # Turn motor ON
motor.value(0)  # Turn motor OFF
```

---

✅ You're now ready to flash firmware, connect wirelessly, and start building IoT or robotics projects with MicroPython!

➡️ Next: [Write your first MicroPython script →](#)
