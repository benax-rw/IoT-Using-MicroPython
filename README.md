
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

✅ You're now ready to start coding with MicroPython!

➡️ Next: [Write your first MicroPython script →](#)
