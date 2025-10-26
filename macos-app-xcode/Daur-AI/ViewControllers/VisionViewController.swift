import Cocoa

class VisionViewController: NSViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.white.cgColor
        
        let titleLabel = NSTextField()
        titleLabel.stringValue = "Vision System"
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.isEditable = false
        titleLabel.isBordered = false
        titleLabel.drawsBackground = false
        titleLabel.frame = NSRect(x: 20, y: view.bounds.height - 50, width: 400, height: 30)
        view.addSubview(titleLabel)
        
        let descLabel = NSTextField()
        descLabel.stringValue = "Computer Vision Features:\n\n• OCR (Optical Character Recognition)\n• Face Detection\n• Barcode Recognition\n• Real-time Video Analysis"
        descLabel.font = NSFont.systemFont(ofSize: 14)
        descLabel.isEditable = false
        descLabel.isBordered = false
        descLabel.drawsBackground = false
        descLabel.frame = NSRect(x: 20, y: view.bounds.height - 200, width: 600, height: 150)
        view.addSubview(descLabel)
        
        let uploadButton = NSButton()
        uploadButton.title = "Upload Image"
        uploadButton.bezelStyle = .rounded
        uploadButton.frame = NSRect(x: 20, y: view.bounds.height - 250, width: 150, height: 40)
        uploadButton.target = self
        uploadButton.action = #selector(uploadImage)
        view.addSubview(uploadButton)
    }
    
    @objc private func uploadImage() {
        let openPanel = NSOpenPanel()
        openPanel.allowedFileTypes = ["jpg", "jpeg", "png", "gif"]
        openPanel.begin { [weak self] response in
            if response == .OK, let url = openPanel.url {
                print("Selected image: \(url.path)")
            }
        }
    }
}

