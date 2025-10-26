import Cocoa

class MainViewController: NSViewController {
    
    // MARK: - UI Elements
    private let tabViewController = NSTabViewController()
    private let apiService = APIService.shared
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        setupUI()
        setupTabs()
        loadSystemStatus()
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor(red: 0.95, green: 0.95, blue: 0.97, alpha: 1.0).cgColor
    }
    
    private func setupTabs() {
        tabViewController.view.frame = view.bounds
        addChild(tabViewController)
        view.addSubview(tabViewController.view)
        
        // Dashboard Tab
        let dashboardVC = DashboardViewController()
        let dashboardTab = NSTabViewItem(viewController: dashboardVC)
        dashboardTab.label = "Dashboard"
        dashboardTab.image = NSImage(systemSymbolName: "chart.bar.fill", accessibilityDescription: "Dashboard")
        tabViewController.addTabViewItem(dashboardTab)
        
        // Hardware Tab
        let hardwareVC = HardwareViewController()
        let hardwareTab = NSTabViewItem(viewController: hardwareVC)
        hardwareTab.label = "Hardware"
        hardwareTab.image = NSImage(systemSymbolName: "cpu", accessibilityDescription: "Hardware")
        tabViewController.addTabViewItem(hardwareTab)
        
        // Vision Tab
        let visionVC = VisionViewController()
        let visionTab = NSTabViewItem(viewController: visionVC)
        visionTab.label = "Vision"
        visionTab.image = NSImage(systemSymbolName: "eye.fill", accessibilityDescription: "Vision")
        tabViewController.addTabViewItem(visionTab)
        
        // Settings Tab
        let settingsVC = SettingsViewController()
        let settingsTab = NSTabViewItem(viewController: settingsVC)
        settingsTab.label = "Settings"
        settingsTab.image = NSImage(systemSymbolName: "gear", accessibilityDescription: "Settings")
        tabViewController.addTabViewItem(settingsTab)
    }
    
    private func loadSystemStatus() {
        apiService.getSystemInfo { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let info):
                    print("System Info: \(info)")
                case .failure(let error):
                    print("Error loading system info: \(error)")
                }
            }
        }
    }
}

