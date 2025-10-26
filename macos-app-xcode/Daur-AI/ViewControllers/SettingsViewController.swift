import Cocoa

class SettingsViewController: NSViewController {
    
    private let apiService = APIService.shared
    
    // MARK: - UI Elements
    private let hostTextField = NSTextField()
    private let portTextField = NSTextField()
    private let usernameTextField = NSTextField()
    private let passwordTextField = NSSecureTextField()
    private let statusLabel = NSTextField()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadSettings()
    }
    
    private func setupUI() {
        view.wantsLayer = true
        view.layer?.backgroundColor = NSColor.white.cgColor
        
        // Title
        let titleLabel = NSTextField()
        titleLabel.stringValue = "Settings"
        titleLabel.font = NSFont.systemFont(ofSize: 24, weight: .bold)
        titleLabel.isEditable = false
        titleLabel.isBordered = false
        titleLabel.drawsBackground = false
        titleLabel.frame = NSRect(x: 20, y: view.bounds.height - 50, width: 400, height: 30)
        view.addSubview(titleLabel)
        
        // API Settings Section
        let apiLabel = NSTextField()
        apiLabel.stringValue = "API Connection"
        apiLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        apiLabel.isEditable = false
        apiLabel.isBordered = false
        apiLabel.drawsBackground = false
        apiLabel.frame = NSRect(x: 20, y: view.bounds.height - 100, width: 200, height: 20)
        view.addSubview(apiLabel)
        
        // Host
        let hostLabelField = NSTextField()
        hostLabelField.stringValue = "Host:"
        hostLabelField.font = NSFont.systemFont(ofSize: 12)
        hostLabelField.isEditable = false
        hostLabelField.isBordered = false
        hostLabelField.drawsBackground = false
        hostLabelField.frame = NSRect(x: 20, y: view.bounds.height - 140, width: 100, height: 20)
        view.addSubview(hostLabelField)
        
        hostTextField.stringValue = "localhost"
        hostTextField.frame = NSRect(x: 130, y: view.bounds.height - 140, width: 200, height: 25)
        hostTextField.isBordered = true
        view.addSubview(hostTextField)
        
        // Port
        let portLabelField = NSTextField()
        portLabelField.stringValue = "Port:"
        portLabelField.font = NSFont.systemFont(ofSize: 12)
        portLabelField.isEditable = false
        portLabelField.isBordered = false
        portLabelField.drawsBackground = false
        portLabelField.frame = NSRect(x: 20, y: view.bounds.height - 180, width: 100, height: 20)
        view.addSubview(portLabelField)
        
        portTextField.stringValue = "8000"
        portTextField.frame = NSRect(x: 130, y: view.bounds.height - 180, width: 200, height: 25)
        portTextField.isBordered = true
        view.addSubview(portTextField)
        
        // Authentication Section
        let authLabel = NSTextField()
        authLabel.stringValue = "Authentication"
        authLabel.font = NSFont.systemFont(ofSize: 14, weight: .semibold)
        authLabel.isEditable = false
        authLabel.isBordered = false
        authLabel.drawsBackground = false
        authLabel.frame = NSRect(x: 20, y: view.bounds.height - 240, width: 200, height: 20)
        view.addSubview(authLabel)
        
        // Username
        let usernameLabelField = NSTextField()
        usernameLabelField.stringValue = "Username:"
        usernameLabelField.font = NSFont.systemFont(ofSize: 12)
        usernameLabelField.isEditable = false
        usernameLabelField.isBordered = false
        usernameLabelField.drawsBackground = false
        usernameLabelField.frame = NSRect(x: 20, y: view.bounds.height - 280, width: 100, height: 20)
        view.addSubview(usernameLabelField)
        
        usernameTextField.frame = NSRect(x: 130, y: view.bounds.height - 280, width: 200, height: 25)
        usernameTextField.isBordered = true
        view.addSubview(usernameTextField)
        
        // Password
        let passwordLabelField = NSTextField()
        passwordLabelField.stringValue = "Password:"
        passwordLabelField.font = NSFont.systemFont(ofSize: 12)
        passwordLabelField.isEditable = false
        passwordLabelField.isBordered = false
        passwordLabelField.drawsBackground = false
        passwordLabelField.frame = NSRect(x: 20, y: view.bounds.height - 320, width: 100, height: 20)
        view.addSubview(passwordLabelField)
        
        passwordTextField.frame = NSRect(x: 130, y: view.bounds.height - 320, width: 200, height: 25)
        passwordTextField.isBordered = true
        view.addSubview(passwordTextField)
        
        // Status
        statusLabel.stringValue = "Status: Not connected"
        statusLabel.font = NSFont.systemFont(ofSize: 12)
        statusLabel.isEditable = false
        statusLabel.isBordered = false
        statusLabel.drawsBackground = false
        statusLabel.frame = NSRect(x: 20, y: view.bounds.height - 370, width: 400, height: 20)
        view.addSubview(statusLabel)
        
        // Buttons
        let connectButton = NSButton()
        connectButton.title = "Connect"
        connectButton.bezelStyle = .rounded
        connectButton.frame = NSRect(x: 20, y: view.bounds.height - 420, width: 100, height: 40)
        connectButton.target = self
        connectButton.action = #selector(connect)
        view.addSubview(connectButton)
        
        let loginButton = NSButton()
        loginButton.title = "Login"
        loginButton.bezelStyle = .rounded
        loginButton.frame = NSRect(x: 130, y: view.bounds.height - 420, width: 100, height: 40)
        loginButton.target = self
        loginButton.action = #selector(login)
        view.addSubview(loginButton)
    }
    
    private func loadSettings() {
        if let host = UserDefaults.standard.string(forKey: "APIHost") {
            hostTextField.stringValue = host
        }
        if let port = UserDefaults.standard.string(forKey: "APIPort") {
            portTextField.stringValue = port
        }
    }
    
    @objc private func connect() {
        let host = hostTextField.stringValue
        let port = Int(portTextField.stringValue) ?? 8000
        
        UserDefaults.standard.set(host, forKey: "APIHost")
        UserDefaults.standard.set(String(port), forKey: "APIPort")
        
        apiService.connect(host: host, port: port)
        statusLabel.stringValue = "Status: Connecting..."
    }
    
    @objc private func login() {
        let username = usernameTextField.stringValue
        let password = passwordTextField.stringValue
        
        guard !username.isEmpty && !password.isEmpty else {
            statusLabel.stringValue = "Status: Please enter username and password"
            return
        }
        
        apiService.login(username: username, password: password) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self?.statusLabel.stringValue = "Status: Logged in ✅"
                case .failure(let error):
                    self?.statusLabel.stringValue = "Status: Login failed - \(error.localizedDescription)"
                }
            }
        }
    }
}

