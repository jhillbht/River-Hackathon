import Foundation
import CoreLocation

class APIService {
    static let shared = APIService()
    
    // Base URL for the backend service
    private let baseURL = Constants.baseURL
    
    // API key for SerpAPI
    private let serpAPIKey = Constants.serpAPIKey
    
    // Session for network requests
    private let session = URLSession.shared
    
    private init() {}
    
    // MARK: - Device Registration
    
    func registerDeviceToken(token: String, completion: @escaping (Bool) -> Void) {
        let endpoint = "\(baseURL)/device/register"
        
        var request = URLRequest(url: URL(string: endpoint)!)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = [
            "device_token": token,
            "device_type": "iOS",
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "Unknown"
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        let task = session.dataTask(with: request) { data, response, error in
            guard error == nil,
                  let response = response as? HTTPURLResponse,
                  response.statusCode == 200 else {
                print("Error registering device token: \(error?.localizedDescription ?? "Unknown error")")
                completion(false)
                return
            }
            
            completion(true)
        }
        
        task.resume()
    }
    
    // MARK: - Driving Status
    
    func updateDrivingStatus(isDriving: Bool, completion: @escaping (Bool) -> Void) {
        // For demo purposes, just return success
        print("Would update driving status to: \(isDriving)")
        completion(true)
    }
    
    // MARK: - Location Updates
    
    func updateLocation(latitude: Double, longitude: Double, speed: Double, heading: Double, completion: @escaping (Bool) -> Void) {
        // For demo purposes, just return success
        print("Would update location to: lat=\(latitude), lon=\(longitude)")
        completion(true)
    }
    
    // MARK: - Traffic Incidents
    
    func fetchTrafficIncidents(completion: @escaping ([TrafficIncident]?) -> Void) {
        let austinTrafficAPI = Constants.trafficIncidentsAPI + "?$limit=50&$order=published_date DESC"
        
        guard let url = URL(string: austinTrafficAPI) else {
            completion(nil)
            return
        }
        
        let task = session.dataTask(with: url) { data, response, error in
            guard let data = data, error == nil else {
                print("Error fetching traffic incidents: \(error?.localizedDescription ?? "Unknown error")")
                completion(nil)
                return
            }
            
            do {
                if let jsonArray = try JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
                    let incidents = jsonArray.compactMap { TrafficIncident.fromAPI($0) }
                    completion(incidents)
                } else {
                    completion(nil)
                }
            } catch {
                print("Error parsing traffic incidents: \(error.localizedDescription)")
                completion(nil)
            }
        }
        
        task.resume()
    }
}
