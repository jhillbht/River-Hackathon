import UIKit
import MapKit

class MainViewController: UIViewController, MKMapViewDelegate {
    
    // MARK: - UI Elements
    
    private let mapView = MKMapView()
    private let statusLabel = UILabel()
    private let toggleButton = UIButton(type: .system)
    private let settingsButton = UIButton(type: .system)
    private let historyButton = UIButton(type: .system)
    
    // MARK: - Properties
    
    private var incidents: [TrafficIncident] = []
    private var annotations: [MKPointAnnotation] = []
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        setupUI()
        setupObservers()
        
        // Check if this is first launch
        if UserPreferences.shared.isFirstLaunch {
            presentSetupViewController()
        } else if UserPreferences.shared.alertsEnabled {
            // Start services if alerts are enabled
            startServices()
        }
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        
        // Refresh UI when view appears
        updateStatusLabel()
        updateToggleButton()
        loadIncidents()
    }
    
    // MARK: - UI Setup
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        
        // Map View
        mapView.translatesAutoresizingMaskIntoConstraints = false
        mapView.showsUserLocation = true
        mapView.delegate = self
        view.addSubview(mapView)
        
        // Status Label
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        statusLabel.textAlignment = .center
        statusLabel.font = .systemFont(ofSize: 14, weight: .medium)
        statusLabel.backgroundColor = .systemBackground.withAlphaComponent(0.8)
        statusLabel.layer.cornerRadius = 8
        statusLabel.layer.masksToBounds = true
        statusLabel.textColor = .label
        view.addSubview(statusLabel)
        
        // Toggle Button
        toggleButton.translatesAutoresizingMaskIntoConstraints = false
        toggleButton.setTitle("Start Monitoring", for: .normal)
        toggleButton.backgroundColor = .systemBlue
        toggleButton.setTitleColor(.white, for: .normal)
        toggleButton.layer.cornerRadius = 20
        toggleButton.addTarget(self, action: #selector(toggleMonitoring), for: .touchUpInside)
        view.addSubview(toggleButton)
        
        // Settings Button
        settingsButton.translatesAutoresizingMaskIntoConstraints = false
        settingsButton.setImage(UIImage(systemName: "gear"), for: .normal)
        settingsButton.backgroundColor = .systemBackground.withAlphaComponent(0.8)
        settingsButton.layer.cornerRadius = 20
        settingsButton.addTarget(self, action: #selector(openSettings), for: .touchUpInside)
        view.addSubview(settingsButton)
        
        // History Button
        historyButton.translatesAutoresizingMaskIntoConstraints = false
        historyButton.setImage(UIImage(systemName: "clock.arrow.circlepath"), for: .normal)
        historyButton.backgroundColor = .systemBackground.withAlphaComponent(0.8)
        historyButton.layer.cornerRadius = 20
        historyButton.addTarget(self, action: #selector(showHistory), for: .touchUpInside)
        view.addSubview(historyButton)
        
        // Layout Constraints
        NSLayoutConstraint.activate([
            // Map View
            mapView.topAnchor.constraint(equalTo: view.topAnchor),
            mapView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            mapView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            mapView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            // Status Label
            statusLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            statusLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            statusLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            statusLabel.heightAnchor.constraint(equalToConstant: 40),
            
            // Toggle Button
            toggleButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -20),
            toggleButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            toggleButton.widthAnchor.constraint(equalToConstant: 200),
            toggleButton.heightAnchor.constraint(equalToConstant: 50),
            
            // Settings Button
            settingsButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 60),
            settingsButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            settingsButton.widthAnchor.constraint(equalToConstant: 40),
            settingsButton.heightAnchor.constraint(equalToConstant: 40),
            
            // History Button
            historyButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 60),
            historyButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            historyButton.widthAnchor.constraint(equalToConstant: 40),
            historyButton.heightAnchor.constraint(equalToConstant: 40)
        ])
        
        // Update UI to reflect current state
        updateStatusLabel()
        updateToggleButton()
    }
    
    // MARK: - Observers and Actions (Partial Implementations for Sample)
    
    private func setupObservers() {
        // Observe driving status changes
        MotionService.shared.onDrivingStatusChanged = { [weak self] isDriving in
            DispatchQueue.main.async {
                self?.updateStatusLabel()
                self?.loadIncidents()
            }
        }
    }
    
    @objc private func toggleMonitoring() {
        UserPreferences.shared.alertsEnabled.toggle()
        
        if UserPreferences.shared.alertsEnabled {
            startServices()
        } else {
            stopServices()
        }
        
        updateStatusLabel()
        updateToggleButton()
    }
    
    @objc private func openSettings() {
        print("Open settings")
    }
    
    @objc private func showHistory() {
        print("Show history")
    }
    
    // MARK: - Helper Methods (Partial Implementations for Sample)
    
    private func startServices() {
        MotionService.shared.startMonitoring()
        // Other service activations would go here
    }
    
    private func stopServices() {
        MotionService.shared.stopMonitoring()
        // Other service deactivations would go here
    }
    
    private func updateStatusLabel() {
        // Sample implementation
        statusLabel.text = MotionService.shared.isDriving ? "Driving: Active" : "Monitoring: Standby"
    }
    
    private func updateToggleButton() {
        // Sample implementation
        toggleButton.setTitle(UserPreferences.shared.alertsEnabled ? "Stop Monitoring" : "Start Monitoring", for: .normal)
    }
    
    private func loadIncidents() {
        // Sample implementation that would be filled in fully
        print("Would load incidents here")
    }
    
    private func presentSetupViewController() {
        // Sample implementation that would be filled in fully
        print("Would present setup screen here")
    }
    
    // MARK: - MKMapViewDelegate
    
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        // This would be implemented to customize the appearance of incident markers
        return nil
    }
}
