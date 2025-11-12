import Cocoa

class HardwareViewController: NSViewController {
    
    private let apiService = APIService.shared
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadHardwareInfo()
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.white.cgColor
        
        let titleLabel = NSTextField()
        titleLabel.stringValue = "Hardware Information"
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.isEditable = false
        titleLabel.isBordered = false
        titleLabel.drawsBackground = false
        titleLabel.frame = NSRect(x: 20, y: view.bounds.height - 50, width: 400, height: 30)
        view.addSubview(titleLabel)
        
        let infoLabel = NSTextField()
        infoLabel.stringValue = "Loading hardware information..."
        infoLabel.font = NSFont.systemFont(ofSize: 14)
        infoLabel.isEditable = false
        infoLabel.isBordered = false
        infoLabel.drawsBackground = false
        infoLabel.frame = NSRect(x: 20, y: view.bounds.height - 100, width: 600, height: 400)
        infoLabel.tag = 100
        view.addSubview(infoLabel)
    }
    
    private func loadHardwareInfo() {
        apiService.getSystemInfo { [weak self] result in
            DispatchQueue.main.async {
                if let infoLabel = self?.view.viewWithTag(100) as? NSTextField {
                    switch result {
                    case .success(let info):
                        var text = "Hardware Information:\n\n"
                        for (key, value) in info {
                            text += "\(key): \(value)\n"
                        }
                        infoLabel.stringValue = text
                    case .failure(let error):
                        infoLabel.stringValue = "Error loading hardware info: \(error.localizedDescription)"
                    }
                }
            }
        }
    }
}

