import Cocoa

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    
    var mainWindow: NSWindow?
    var statusBarItem: NSStatusBarButton?
    let apiService = APIService()
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Create main window
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1200, height: 800),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        
        window.center()
        window.title = "Daur-AI v2.0"
        window.setFrameAutosaveName("MainWindow")
        
        // Create main view controller
        let mainViewController = MainViewController()
        window.contentViewController = mainViewController
        
        window.makeKeyAndOrderFront(nil)
        self.mainWindow = window
        
        // Setup status bar icon
        setupStatusBar()
        
        // Start API connection
        apiService.connect(host: "localhost", port: 8000)
    }
    
    func applicationWillTerminate(_ aNotification: Notification) {
        apiService.disconnect()
    }
    
    private func setupStatusBar() {
        let statusBar = NSStatusBar.system
        let statusBarItem = statusBar.statusItem(withLength: NSStatusBarItem.variableLength)
        
        if let button = statusBarItem.button {
            button.image = NSImage(systemSymbolName: "brain.head.profile", accessibilityDescription: "Daur-AI")
            button.action = #selector(toggleWindow)
            button.target = self
        }
        
        self.statusBarItem = statusBarItem.button
    }
    
    @objc func toggleWindow() {
        if let window = mainWindow {
            if window.isVisible {
                window.orderOut(nil)
            } else {
                window.makeKeyAndOrderFront(nil)
            }
        }
    }
}

