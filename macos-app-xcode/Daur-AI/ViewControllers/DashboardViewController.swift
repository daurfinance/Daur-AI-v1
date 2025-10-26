import Cocoa

class DashboardViewController: NSViewController {
    
    private let apiService = APIService.shared
    private var updateTimer: Timer?
    
    // MARK: - UI Elements
    private let statusLabel = NSTextField()
    private let cpuLabel = NSTextField()
    private let memoryLabel = NSTextField()
    private let diskLabel = NSTextField()
    private let cpuProgressBar = NSProgressIndicator()
    private let memoryProgressBar = NSProgressIndicator()
    private let diskProgressBar = NSProgressIndicator()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        startMonitoring()
    }
    
    override func viewWillDisappear() {
        super.viewWillDisappear()
        stopMonitoring()
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.white.cgColor
        
        // Title
        let titleLabel = NSTextField()
        titleLabel.stringValue = "System Dashboard"
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.isEditable = false
        titleLabel.isBordered = false
        titleLabel.drawsBackground = false
        titleLabel.frame = NSRect(x: 20, y: view.bounds.height - 50, width: 400, height: 30)
        view.addSubview(titleLabel)
        
        // Status
        statusLabel.stringValue = "Status: Connecting..."
        statusLabel.font = NSFont.systemFont(ofSize: 14)
        statusLabel.isEditable = false
        statusLabel.isBordered = false
        statusLabel.drawsBackground = false
        statusLabel.frame = NSRect(x: 20, y: view.bounds.height - 90, width: 400, height: 20)
        view.addSubview(statusLabel)
        
        // CPU Section
        let cpuTitleLabel = NSTextField()
        cpuTitleLabel.stringValue = "CPU Usage"
        cpuTitleLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        cpuTitleLabel.isEditable = false
        cpuTitleLabel.isBordered = false
        cpuTitleLabel.drawsBackground = false
        cpuTitleLabel.frame = NSRect(x: 20, y: view.bounds.height - 140, width: 200, height: 20)
        view.addSubview(cpuTitleLabel)
        
        cpuLabel.stringValue = "CPU: 0%"
        cpuLabel.font = NSFont.systemFont(ofSize: 12)
        cpuLabel.isEditable = false
        cpuLabel.isBordered = false
        cpuLabel.drawsBackground = false
        cpuLabel.frame = NSRect(x: 20, y: view.bounds.height - 165, width: 200, height: 20)
        view.addSubview(cpuLabel)
        
        cpuProgressBar.style = .bar
        cpuProgressBar.minValue = 0
        cpuProgressBar.maxValue = 100
        cpuProgressBar.frame = NSRect(x: 20, y: view.bounds.height - 190, width: 300, height: 20)
        view.addSubview(cpuProgressBar)
        
        // Memory Section
        let memoryTitleLabel = NSTextField()
        memoryTitleLabel.stringValue = "Memory Usage"
        memoryTitleLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        memoryTitleLabel.isEditable = false
        memoryTitleLabel.isBordered = false
        memoryTitleLabel.drawsBackground = false
        memoryTitleLabel.frame = NSRect(x: 20, y: view.bounds.height - 240, width: 200, height: 20)
        view.addSubview(memoryTitleLabel)
        
        memoryLabel.stringValue = "Memory: 0%"
        memoryLabel.font = NSFont.systemFont(ofSize: 12)
        memoryLabel.isEditable = false
        memoryLabel.isBordered = false
        memoryLabel.drawsBackground = false
        memoryLabel.frame = NSRect(x: 20, y: view.bounds.height - 265, width: 200, height: 20)
        view.addSubview(memoryLabel)
        
        memoryProgressBar.style = .bar
        memoryProgressBar.minValue = 0
        memoryProgressBar.maxValue = 100
        memoryProgressBar.frame = NSRect(x: 20, y: view.bounds.height - 290, width: 300, height: 20)
        view.addSubview(memoryProgressBar)
        
        // Disk Section
        let diskTitleLabel = NSTextField()
        diskTitleLabel.stringValue = "Disk Usage"
        diskTitleLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        diskTitleLabel.isEditable = false
        diskTitleLabel.isBordered = false
        diskTitleLabel.drawsBackground = false
        diskTitleLabel.frame = NSRect(x: 20, y: view.bounds.height - 340, width: 200, height: 20)
        view.addSubview(diskTitleLabel)
        
        diskLabel.stringValue = "Disk: 0%"
        diskLabel.font = NSFont.systemFont(ofSize: 12)
        diskLabel.isEditable = false
        diskLabel.isBordered = false
        diskLabel.drawsBackground = false
        diskLabel.frame = NSRect(x: 20, y: view.bounds.height - 365, width: 200, height: 20)
        view.addSubview(diskLabel)
        
        diskProgressBar.style = .bar
        diskProgressBar.minValue = 0
        diskProgressBar.maxValue = 100
        diskProgressBar.frame = NSRect(x: 20, y: view.bounds.height - 390, width: 300, height: 20)
        view.addSubview(diskProgressBar)
    }
    
    private func startMonitoring() {
        updateMetrics()
        updateTimer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] _ in
            self?.updateMetrics()
        }
    }
    
    private func stopMonitoring() {
        updateTimer?.invalidate()
        updateTimer = nil
    }
    
    private func updateMetrics() {
        apiService.getCPUMetrics { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let metrics):
                    self?.cpuLabel.stringValue = String(format: "CPU: %.1f%%", metrics.percent)
                    self?.cpuProgressBar.doubleValue = metrics.percent
                    self?.statusLabel.stringValue = "Status: Connected ✅"
                case .failure:
                    self?.statusLabel.stringValue = "Status: Disconnected ❌"
                }
            }
        }
        
        apiService.getMemoryMetrics { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let metrics):
                    self?.memoryLabel.stringValue = String(format: "Memory: %.1f%%", metrics.percent)
                    self?.memoryProgressBar.doubleValue = metrics.percent
                case .failure:
                    break
                }
            }
        }
        
        apiService.getDiskMetrics { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let metrics):
                    self?.diskLabel.stringValue = String(format: "Disk: %.1f%%", metrics.percent)
                    self?.diskProgressBar.doubleValue = metrics.percent
                case .failure:
                    break
                }
            }
        }
    }
}

