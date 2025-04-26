import Foundation

class UserPreferences {
    static let shared = UserPreferences()
    
    private let defaults = UserDefaults.standard
    
    private enum Keys {
        static let isFirstLaunch = "isFirstLaunch"
        static let alertsEnabled = "alertsEnabled"
        static let criticalAlertsOnly = "criticalAlertsOnly"
        static let notificationDistance = "notificationDistance"
        static let audioAlertsEnabled = "audioAlertsEnabled"
    }
    
    var isFirstLaunch: Bool {
        get { return defaults.bool(forKey: Keys.isFirstLaunch) }
        set { defaults.set(newValue, forKey: Keys.isFirstLaunch) }
    }
    
    var alertsEnabled: Bool {
        get { return defaults.bool(forKey: Keys.alertsEnabled) }
        set { defaults.set(newValue, forKey: Keys.alertsEnabled) }
    }
    
    var criticalAlertsOnly: Bool {
        get { return defaults.bool(forKey: Keys.criticalAlertsOnly) }
        set { defaults.set(newValue, forKey: Keys.criticalAlertsOnly) }
    }
    
    var notificationDistance: Double {
        get { return defaults.double(forKey: Keys.notificationDistance) }
        set { defaults.set(newValue, forKey: Keys.notificationDistance) }
    }
    
    var audioAlertsEnabled: Bool {
        get { return defaults.bool(forKey: Keys.audioAlertsEnabled) }
        set { defaults.set(newValue, forKey: Keys.audioAlertsEnabled) }
    }
    
    private init() {
        // Set default values if this is the first launch
        if defaults.object(forKey: Keys.isFirstLaunch) == nil {
            defaults.set(true, forKey: Keys.isFirstLaunch)
            defaults.set(true, forKey: Keys.alertsEnabled)
            defaults.set(false, forKey: Keys.criticalAlertsOnly)
            defaults.set(1000.0, forKey: Keys.notificationDistance) // 1km default
            defaults.set(true, forKey: Keys.audioAlertsEnabled)
        }
    }
    
    func reset() {
        defaults.removeObject(forKey: Keys.isFirstLaunch)
        defaults.removeObject(forKey: Keys.alertsEnabled)
        defaults.removeObject(forKey: Keys.criticalAlertsOnly)
        defaults.removeObject(forKey: Keys.notificationDistance)
        defaults.removeObject(forKey: Keys.audioAlertsEnabled)
        
        // Re-initialize with defaults
        _ = UserPreferences.shared
    }
}
