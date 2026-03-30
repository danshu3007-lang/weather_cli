# 🌤 Weather CLI

> Get live weather for any city — directly in your terminal. No API key. No signup. Just run it.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Powered by](https://img.shields.io/badge/Powered%20by-Open--Meteo-orange?style=flat-square)

```
$ python weather.py Delhi

────────────────────────────────────────
  📍  Delhi, India
────────────────────────────────────────
  🌡   Temperature : 32.4 °C
  💧  Humidity    : 55 %
  🌤   Conditions  : Partly cloudy
  💨  Wind speed  : 14.2 km/h
────────────────────────────────────────
```

---

## 🤔 Why I built this

I wanted a simple way to check the weather without opening a browser or signing up for an API key.
Most weather tools are either bloated or require accounts. This is **one Python file, one dependency, runs anywhere**.

---

## ✨ What it does

- 🌍 Live weather for **any city in the world**
- ⚡ **5-minute cache** — won't spam the API if you run it twice
- 🔁 **Auto-retries** on bad network with exponential backoff
- 🧾 **JSON mode** — pipe the output into other scripts
- 🛡 Handles errors cleanly — typos, network issues, bad responses
- 📦 **Single file** — no install, no config, just `python weather.py`

---

## 🚀 Setup

```bash
# 1. Install the only dependency
pip install requests

# 2. Run it
python weather.py London
```

That's it.

---

## 💻 Usage

```bash
python weather.py Mumbai                # basic lookup
python weather.py "New York"            # multi-word cities need quotes
python weather.py Tokyo --refresh       # skip cache, get fresh data
python weather.py Sydney --json         # raw JSON output
python weather.py Paris --verbose       # show debug logs
```

**JSON output** (useful for data pipelines):
```json
{
  "city": "Sydney",
  "country": "Australia",
  "temperature": 21.3,
  "humidity": 65,
  "description": "Partly cloudy",
  "wind_speed": 19.4,
  "cached": false
}
```

---

## ⚙️ How it works

```
Your input (city name)
      │
      ▼
 Geocoding API  ──►  city name → lat/lon coordinates
      │
      ▼
 Weather API    ──►  lat/lon → temperature, humidity, wind
      │
      ▼
 Cache layer    ──►  stores result for 5 minutes
      │
      ▼
 Your terminal  ──►  clean formatted output
```

The entire flow is handled in one file with no global state leaking between layers.

---

## 🛠 Technical choices

| What | How | Why |
|---|---|---|
| HTTP | `requests` + `urllib3.Retry` | Auto-retry on 5xx errors and timeouts |
| Caching | In-memory dict with TTL | No database needed for a CLI tool |
| Error handling | Custom exception hierarchy | Different errors need different responses |
| Data source | Open-Meteo API | Free, no API key, reliable |

---

## 📦 Requirements

```
Python 3.10+
requests>=2.31.0
```

---

## 👨‍💻 About me

I'm **Deepanshu**, a BCA student at Chandigarh University passionate about Data Analytics and building practical tools with Python.

This project was my way of learning how to write **production-style Python** — not just code that works, but code that handles failures gracefully, respects resources (caching), and is easy for others to use.

📫 Connect with me on GitHub — I'm always building something new.

---

## 📄 License

MIT — free to use, modify, and share.
