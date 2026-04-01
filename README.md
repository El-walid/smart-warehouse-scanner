# 📦 Smart Warehouse Scanner (Mobile-to-Cloud)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white) 
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

## 📋 Overview
The **Smart Warehouse Scanner** is a lightweight, mobile-friendly web application designed for factory floor workers. It eliminates paper-based inventory tracking by turning any standard smartphone into an enterprise-grade barcode and QR code scanner.

Instead of buying expensive proprietary hardware, workers simply open a local web link on their phones, scan a product, enter the quantity, and the system instantly updates the master centralized database (Excel/SQL) in real-time.

## 🚀 Key Features
* **📱 Bring Your Own Device (BYOD):** Runs entirely in the smartphone's web browser via Streamlit. No app store installation required.
* **📷 Real-Time Computer Vision:** Utilizes `pyzbar` and `OpenCV` to instantly decode barcodes and QR codes from the device's live camera feed.
* **⚡ Instant Synchronization:** Eliminates end-of-day data entry. When a worker taps "Update," the central inventory ledger is updated in milliseconds.
* **🚇 WSL / Secure Tunneling Support:** Configured to easily bypass local firewall restrictions using SSH tunneling, enabling secure HTTPS mobile camera access anywhere.

## 🛠️ Technical Stack
* **Frontend/Backend Engine:** Streamlit (Python)
* **Computer Vision:** OpenCV (`opencv-python-headless`) & PyZbar
* **Data Management:** Pandas & Openpyxl

## ⚙️ Setup & Installation

### 1. Install System Dependencies (Linux/WSL)
*Note: The `pyzbar` library requires the C++ ZBar engine to be installed on the operating system to decode images.*
```bash
sudo apt-get update
sudo apt-get install libzbar0 -y
```

### 2. Initialize the Python Environment
```bash
git clone [https://github.com/El-walid/smart-warehouse-scanner.git](https://github.com/El-walid/smart-warehouse-scanner.git)
cd smart-warehouse-scanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🏃‍♂️ How to Run & Demo on Mobile

To demo this software, you host it on your machine and access it via a smartphone. 

**Step 1: Start the Server**
```bash
streamlit run app.py
```

**Step 2: Connect the Smartphone**
* **If on the same Wi-Fi (Standard Mac/Windows):** Type the `Network URL` (e.g., `http://192.168.1.X:8501`) provided in the terminal directly into your phone's browser.
* **If using WSL (Windows Subsystem for Linux) or remote networks:** WSL hides the local IP. To give your phone secure HTTPS access to the camera, open a second terminal and run an SSH tunnel:
```bash
ssh -R 80:localhost:8501 nokey@localhost.run
```
Open the generated `https://...localhost.run` link on your smartphone, grant camera permissions, and start scanning!

## 👨‍💻 Author
**El Walid El Alaoui Fels**
*Data Engineer | Automation Specialist*


