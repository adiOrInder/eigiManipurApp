# 🚑 Eigi Manipur – Emergency Response App

A Kivy-based mobile/desktop application that helps users request emergency ambulance services with real-time location tracking and patient details.

---

## 📱 Features

- Emergency service request (ALS / BLS)
- Step-by-step medical questions
- Automatic GPS location fetching
- Sends data to backend server
- English & Manipuri language support
- Clean and simple UI

---

## 🛠 Tech Stack

- **Frontend:** Python, Kivy
- **Location:** CoreLocation (macOS / iOS)
- **Backend:** Flask (server API)
- **Networking:** Requests

---

## 📂 Project Structure

```
project/
│
├── main.py
├── eigimanipur.kv
├── src/
│   └── location.py
├── NotoSansMeeteiMayek-Medium.ttf
└── README.md
```

---

## 🚀 How to Run

### 1️⃣ Install dependencies

```bash
pip install kivy requests pyobjc
```

### 2️⃣ Update server IP

Edit in `main.py`:

```python
SERVER = "http://YOUR_IP:5000/location"
```

### 3️⃣ Run the app

```bash
python main.py
```

---

## 📡 API Endpoint

**POST** `/location`

### Sample Payload

```json
{
  "level": "ALS",
  "conscious": "Yes",
  "trauma": "No",
  "oxygen": "Yes",
  "age": "25",
  "lat": -,
  "lon": -
}
```

---

## 🌐 Language Support

- English 🇬🇧
- Manipuri (Meetei Mayek) 🏴

Switch using **"Switch Language"** button.

---

## 🔐 Permissions

- Location access required
- Internet access required

---

## 👨‍💻 Author

**Adiorinder**
🔗 GitHub: [https://github.com/adiorinder](https://github.com/adiorinder)

---

## ⭐ Future Improvements

- Android GPS support
- Map integration
- SMS emergency alert
- Hospital database
- Push notifications

---

## 📄 License

MIT License
