import Foundation
import CoreMotion

class MotionService {
    static let shared = MotionService()
    
    private let motionManager = CMMotionActivityManager()
    private let motionQueue = OperationQueue()
    
    var isDriving: Bool = false {
        didSet {
            if isDriving != oldValue {
                notifyDrivingStatusChanged()
            }
        }
    }
    
    var onDrivingStatusChanged: ((Bool) -> Void)?
    
    private init() {
        motionQueue.name = "com.trafficAlerts.motionQueue"
    }
    
    func startMonitoring() {
        guard CMMotionActivityManager.isActivityAvailable() else {
            print("Motion activity not available on this device")
            return
        }
        
        motionManager.startActivityUpdates(to: motionQueue) { [weak self] (activity) in
            guard let activity = activity else { return }
            
            // Check if the user is in automotive mode
            let isCurrentlyDriving = activity.automotive && activity.confidence == .high
            
            // Update driving status on main thread
            DispatchQueue.main.async {
                self?.isDriving = isCurrentlyDriving
            }
        }
    }
    
    func stopMonitoring() {
        motionManager.stopActivityUpdates()
        isDriving = false
    }
    
    private func notifyDrivingStatusChanged() {
        onDrivingStatusChanged?(isDriving)
        
        // When driving starts, notify the backend
        if isDriving {
            APIService.shared.updateDrivingStatus(isDriving: true) { success in
                print("Updated driving status on backend: \(success)")
            }
            
            // Start location updates when driving begins
            LocationService.shared.startUpdatingLocation()
        } else {
            APIService.shared.updateDrivingStatus(isDriving: false) { success in
                print("Updated driving status on backend: \(success)")
            }
            
            // Stop location updates when driving ends to save battery
            LocationService.shared.stopUpdatingLocation()
        }
    }
}
