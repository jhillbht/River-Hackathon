# River Hackathon - First Responder Traffic Alerts

A Swift-based iOS application built during the RiverHacks Hackathon that uses motion detection to automatically provide traffic incident notifications when first responders are driving.

## Features

- Automatic driving detection using iPhone motion sensors
- Real-time traffic incident notifications based on user's route
- Critical alerts that bypass Do Not Disturb mode
- Audio announcements for hands-free operation
- Customizable notification distance and severity filtering
- Interactive map with traffic incident visualization
- Alert history tracking

## Data Sources

- Austin Traffic Incidents API
- Traffic Cameras API
- Weather and routing information via SerpAPI/Google Maps

## Implementation

This app is designed to help first responders be notified of traffic incidents along their route. Key technical components:

- CoreMotion for driving detection
- CoreLocation for route tracking
- UserNotifications with Critical Alerts for high-priority notifications
- MapKit for visualization
- AVSpeechSynthesizer for audio alerts

## Project Structure

```
TrafficAlertApp/
├── AppDelegate.swift
├── SceneDelegate.swift
├── Models/
│   ├── IncidentModel.swift
│   ├── RouteModel.swift
│   └── UserPreferences.swift
├── Views/
│   ├── MainViewController.swift
│   ├── SetupViewController.swift
│   └── AlertHistoryViewController.swift
├── Services/
│   ├── MotionService.swift
│   ├── LocationService.swift
│   ├── NotificationService.swift
│   ├── APIService.swift
│   └── IncidentProcessor.swift
├── Utils/
│   ├── Constants.swift
│   └── Extensions.swift
└── Resources/
    ├── Assets.xcassets
    └── LaunchScreen.storyboard
```

## Required Permissions

- Location Always and When In Use
- Motion Usage
- Critical Alerts (requires special Apple entitlement)
- Background Modes (location, fetch, processing)

## Created during RiverHacks Hackathon 2025
