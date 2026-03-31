# 🌤 Weather CLI

> Get live weather for any city — directly in your terminal. No API key. No signup. Just run it.

[![PyPI version](https://img.shields.io/pypi/v/weather-cli-tool?style=flat-square&color=blue)](https://pypi.org/project/weather-cli-tool/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Powered by Open-Meteo](https://img.shields.io/badge/Powered%20by-Open--Meteo-orange?style=flat-square)](https://open-meteo.com/)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

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

I wanted a simple way to check weather without opening a browser or signing up anywhere.
Most weather tools are either bloated or require API keys. This is **one Python file, one dependency, runs anywhere**.

---

## ✨ Features

- 🌍 Live weather for **any city in the world**
- ⚡ **5-minute cache** — no redundant API calls
- 🔁 **Auto-retry** with exponential backoff on network errors
- 🧾 **JSON output** mode for scripting and data pipelines
- 🛡 Clean error handling — wrong city, timeout, network failure
- 📦 **Single file** — download and run, zero complex setup

---

## 🚀 Installation

**Option A — pip (recommended):**
```bash
pip install weather-cli-tool
weather-cli London
```

**Option B — run directly:**
```bash
pip install requests
python weather.py London
```

---

## 💻 Usage

```bash
weather-cli Mumbai                # basic lookup
weather-cli "New York"            # multi-word cities need quotes
weather-cli Tokyo --refresh       # skip cache, fetch fresh data
weather-cli Sydney --json         # raw JSON output
weather-cli Paris --verbose       # show debug logs
```

**JSON output — great for data pipelines:**
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
Your input  →  Geocoding API  →  city name to lat/lon
                                        │
                                        ▼
               Weather API    →  temperature, humidity, wind
                                        │
                                        ▼
               Cache layer    →  stores result 5 minutes
                                        │
                                        ▼
               Your terminal  →  clean formatted output
```

---

## 🛠 Technical decisions

| What | How | Why |
|---|---|---|
| HTTP | `requests` + `urllib3.Retry` | Auto-retry on 5xx and timeouts |
| Caching | In-memory dict with TTL | No database needed for a CLI |
| Errors | Custom exception types | Different failures need different responses |
| Data | Open-Meteo API | Free, open, no key required |

---

## 📦 Requirements

```
Python 3.10+
requests>=2.31.0
```

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

Some ideas if you want to contribute:
- Add `--fahrenheit` flag
- Add sunrise/sunset times
- Add weekly forecast with `--week`
- Add support for lat/lon coordinates directly

---

## 👨‍💻 About

Built by **Deepanshu** — BCA Student at Chandigarh University, aspiring Data Analyst.

This project was my way of practising **production-style Python** — not just code that works, but code that handles failures gracefully, respects API resources with caching, and is easy for others to use and contribute to.

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and distribute.
