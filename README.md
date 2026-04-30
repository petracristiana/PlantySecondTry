# Planty - IoT Plant Health Monitoring Dashboard

A real-time plant health monitoring dashboard built for the IoT Essentials course at Thomas More University. Planty connects to the ThingSpeak cloud platform to fetch live sensor data from IoT devices and displays it in an interactive, visual dashboard.

## Team

- Rohma Awais
- Maxime Wouters
- Petra Niste Damsa

## What It Does

Planty reads sensor values (such as light intensity and temperature) from a ThingSpeak channel and displays the data in real time. Based on the readings, the dashboard calculates a health score for the plant and shows an animated plant graphic that reacts to its current conditions — happy when conditions are good, sad when they are not. If no IoT hardware is connected, a built-in demo mode generates realistic synthetic data so the dashboard can be tested without any physical device.

## Features

- **Live sensor monitoring** — polls ThingSpeak every 15 seconds for new data across up to 4 configurable sensor fields
- **Plant health visualization** — an animated SVG plant changes mood (good / ok / bad) based on how close sensor values are to their targets
- **Historical charts** — line charts built with Chart.js display the last 30 readings per sensor
- **Demo mode** — generates simulated data with realistic daily sine-wave patterns when no ThingSpeak channel is configured
- **Persistent settings** — Channel ID and API key are saved to localStorage so they survive page reloads
- **Status indicators** — live, polling, and offline states are shown with animated indicators and toast notifications

## Technologies

| Layer | Technology |
|---|---|
| UI | HTML5, CSS3 (flexbox, grid, animations), Vanilla JavaScript (ES6+) |
| Charts | Chart.js (CDN) |
| Fonts | Google Fonts — Nunito |
| IoT Platform | ThingSpeak REST API |
| Data persistence | Browser localStorage |

## How to Use

1. Open `dashboard.html` in a browser.
2. Click the settings icon and enter your ThingSpeak **Channel ID** and **Read API Key**.
3. The dashboard will immediately start polling for live data and updating the charts and plant visualization.
4. To test without hardware, close the settings modal without entering credentials — demo mode starts automatically.

## Architecture

```
IoT Device  →  ThingSpeak Cloud  →  Planty Dashboard (dashboard.html)  →  Browser
```

The entire application is contained in a single file (`dashboard.html`) with no build step or server required.

## Course

IoT Essentials — Thomas More University, Bachelor Year 1, Semester 2 (2025–2026)
