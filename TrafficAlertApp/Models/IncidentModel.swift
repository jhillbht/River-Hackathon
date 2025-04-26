import Foundation
import CoreLocation

struct TrafficIncident: Codable {
    let id: String
    let type: String
    let address: String
    let latitude: Double
    let longitude: Double
    let timestamp: Date
    let publishedDate: Date
    let status: String
    let severity: IncidentSeverity
    
    var coordinate: CLLocationCoordinate2D {
        return CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
    }
    
    enum IncidentSeverity: String, Codable {
        case low
        case medium
        case high
        case critical
        
        var color: String {
            switch self {
            case .low: return "green"
            case .medium: return "yellow"
            case .high: return "orange"
            case .critical: return "red"
            }
        }
    }
    
    // Parse from Austin Traffic API response
    static func fromAPI(_ json: [String: Any]) -> TrafficIncident? {
        guard let id = json["traffic_report_id"] as? String,
              let typeRaw = json["issue_reported"] as? String,
              let address = json["address"] as? String,
              let latString = json["latitude"] as? String,
              let lonString = json["longitude"] as? String,
              let publishedDateString = json["published_date"] as? String,
              let status = json["status"] as? String,
              let latitude = Double(latString),
              let longitude = Double(lonString),
              let publishedDate = ISO8601DateFormatter().date(from: publishedDateString) else {
            return nil
        }
        
        // Determine severity based on incident type
        let severity: IncidentSeverity
        if typeRaw.contains("COLLISION WITH INJURY") {
            severity = .critical
        } else if typeRaw.contains("COLLISION") {
            severity = .high
        } else if typeRaw.contains("BLOCKED") {
            severity = .medium
        } else {
            severity = .low
        }
        
        return TrafficIncident(
            id: id,
            type: typeRaw,
            address: address,
            latitude: latitude,
            longitude: longitude,
            timestamp: Date(),
            publishedDate: publishedDate,
            status: status,
            severity: severity
        )
    }
}
