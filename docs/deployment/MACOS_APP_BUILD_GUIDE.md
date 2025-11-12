# Daur-AI macOS Native Application - Build Guide

## 📱 Overview

This guide explains how to build and run the native Swift macOS application for Daur-AI v2.0.

The application is a professional macOS app with:
- ✅ Dashboard with real-time metrics
- ✅ Hardware monitoring (CPU, Memory, Disk)
- ✅ Vision system integration
- ✅ User authentication
- ✅ Settings management
- ✅ Status bar integration

## 🛠️ Requirements

- **macOS 10.15+** (Catalina or later)
- **Xcode 12.0+** (with Swift 5.3+)
- **Daur-AI API running** (on localhost:8000)

## 📦 Source Files

All Swift source files are located in `/macos-app/Daur-AI/`:

```
macos-app/Daur-AI/
├── AppDelegate.swift              # Application entry point
├── MainViewController.swift        # Main window controller
├── Services/
│   └── APIService.swift           # API communication
├── ViewControllers/
│   ├── DashboardViewController.swift
│   ├── HardwareViewController.swift
│   ├── VisionViewController.swift
│   └── SettingsViewController.swift
└── Info.plist                     # Application metadata
```

## 🔨 Building the Application

### Step 1: Open Xcode

1. Open Xcode on your MacBook
2. Go to **File** → **New** → **Project**
3. Select **macOS** → **App**
4. Click **Next**

### Step 2: Configure Project

**Project Settings:**
- Product Name: `Daur-AI`
- Team: (select your team or skip)
- Organization Identifier: `com.daur`
- Bundle Identifier: `com.daur.ai`
- Language: **Swift**
- User Interface: **Cocoa**

Click **Next** and create the project.

### Step 3: Add Source Files

1. In Xcode, right-click on the project folder
2. Select **Add Files to "Daur-AI"**
3. Navigate to `/macos-app/Daur-AI/`
4. Select all `.swift` files
5. Click **Add**

### Step 4: Configure Info.plist

1. Select `Info.plist` in the project
2. Copy content from `/macos-app/Daur-AI/Info.plist`
3. Replace the default content

### Step 5: Build the App

1. Select **Product** → **Build** (or press Cmd+B)
2. Wait for the build to complete
3. You should see "Build Succeeded"

### Step 6: Run the App

1. Select **Product** → **Run** (or press Cmd+R)
2. The Daur-AI application will launch

## 🚀 Running the Application

### Prerequisites

Before running the app, ensure the Daur-AI API is running:

```bash
# In a Terminal window
docker run -p 8000:8000 daur-ai:latest
```

### Launch the App

**From Xcode:**
- Press **Cmd+R** or select **Product** → **Run**

**From Applications:**
1. Open Finder
2. Go to **Applications**
3. Find **Daur-AI**
4. Double-click to launch

### First Time Setup

1. Go to **Settings** tab
2. Verify Host: `localhost`
3. Verify Port: `8000`
4. Click **Connect**
5. You should see "Status: Connected ✅"

## 📊 Features

### Dashboard Tab
- Real-time CPU usage
- Real-time memory usage
- Real-time disk usage
- System status indicator

### Hardware Tab
- Detailed system information
- CPU specifications
- Memory details
- Disk information

### Vision Tab
- Computer vision features
- Image upload capability
- OCR, face detection, barcode recognition

### Settings Tab
- API connection settings
- User authentication
- Username/password login
- Connection status

## 🔧 Customization

### Change API Server

Edit `AppDelegate.swift`:

```swift
// Change this line:
apiService.connect(host: "localhost", port: 8000)

// To your server:
apiService.connect(host: "your-server.com", port: 8000)
```

### Change App Icon

1. Create a 1024x1024 PNG image
2. In Xcode, select **Assets.xcassets**
3. Drag your image to **AppIcon**

### Change App Name

1. Select the project in Xcode
2. Go to **General** tab
3. Change **Product Name**

## 📦 Creating an Installer

### Option 1: Direct Distribution

1. Select **Product** → **Archive**
2. Click **Distribute App**
3. Select **Direct Distribution**
4. Follow the wizard

### Option 2: Create DMG Installer

1. Build the app: **Product** → **Build**
2. Find the app in: `DerivedData/Daur-AI/Build/Products/Release/`
3. Create a DMG file using Disk Utility
4. Drag the app into the DMG
5. Distribute the DMG file

### Option 3: Mac App Store

1. Enroll in Apple Developer Program
2. Create App ID in App Store Connect
3. Configure signing certificates
4. Submit for review

## 🔐 Code Signing

For distribution, you need to sign the app:

1. Select the project in Xcode
2. Go to **Signing & Capabilities**
3. Select your team
4. Xcode will automatically manage signing

## 🐛 Troubleshooting

### "Cannot connect to API"
- Ensure Docker container is running
- Check host and port in Settings
- Verify firewall allows localhost:8000

### "Build failed"
- Clean build: **Cmd+Shift+K**
- Delete Xcode cache: `rm -rf ~/Library/Developer/Xcode/DerivedData/`
- Restart Xcode

### "App won't launch"
- Check Console for error messages
- Verify Info.plist is correct
- Ensure all Swift files are added to target

## 📱 System Requirements

| Feature | Requirement |
|---------|-------------|
| macOS Version | 10.15+ |
| Architecture | Intel or Apple Silicon |
| Memory | 4GB minimum |
| Storage | 100MB |
| Network | Local network access |

## 🎯 Next Steps

1. **Build the app** following the steps above
2. **Run the app** and test all features
3. **Customize** the app for your needs
4. **Distribute** to users

## 📚 Additional Resources

- [Apple Swift Documentation](https://developer.apple.com/swift/)
- [Xcode Help](https://help.apple.com/xcode/)
- [macOS App Development](https://developer.apple.com/macos/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review Xcode build logs
3. Check the API server is running
4. Verify network connectivity

---

**Version:** 2.0.0  
**Last Updated:** October 25, 2025  
**Status:** Production Ready

