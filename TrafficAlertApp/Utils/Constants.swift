import Foundation

enum Constants {
    // API Endpoints
    static let baseURL = "https://your-backend-api.com"
    static let trafficIncidentsAPI = "https://data.austintexas.gov/resource/dx9v-zd7x.json"
    static let trafficCamerasAPI = "https://data.austintexas.gov/resource/b4k4-adkb.json"
    
    // SerpAPI Configuration
    static let serpAPIKey = "YOUR_SERP_API_KEY" // Replace with your actual key
    
    // App Constants
    static let notificationCategory = "TRAFFIC_INCIDENT"
    static let defaultNotificationDistance = 1000.0 // meters
    
    // Motion Detection
    static let minDrivingSpeed = 5.0 // meters per second
    static let drivingConfidenceThreshold = 0.8
    
    // UI Constants
    static let mapDefaultZoom = 2000.0 // meters
    static let mapTrafficUpdateInterval = 30.0 // seconds
}
