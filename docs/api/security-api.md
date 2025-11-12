# Security and RBAC API

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Status**: Production Ready

---

## Overview

The Security API provides comprehensive security features including role-based access control (RBAC), authentication, authorization, encryption, and security auditing. This API ensures that Daur AI applications are secure, compliant, and protected against common vulnerabilities.

Security is implemented using **defense in depth** principles, with multiple layers of protection including authentication, authorization, encryption, and audit logging. The system follows industry best practices and compliance standards including GDPR, SOC 2, and OWASP guidelines.

---

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Authentication](#authentication)
3. [Authorization and RBAC](#authorization-and-rbac)
4. [User Management](#user-management)
5. [Permissions](#permissions)
6. [Encryption](#encryption)
7. [Security Auditing](#security-auditing)
8. [Rate Limiting](#rate-limiting)
9. [Security Best Practices](#security-best-practices)
10. [Examples](#examples)

---

## Core Concepts

### Security Architecture

The security system is built on several foundational concepts that work together to provide comprehensive protection:

**Authentication** verifies the identity of users through credentials such as passwords, API keys, or OAuth tokens. The system supports multiple authentication methods and enforces strong password policies.

**Authorization** determines what authenticated users are allowed to do through role-based access control (RBAC). Users are assigned roles, and roles are granted specific permissions.

**Encryption** protects sensitive data both at rest and in transit using industry-standard algorithms. All passwords are hashed using Argon2, and sensitive data is encrypted using AES-256.

**Audit Logging** records all security-relevant events for compliance and forensic analysis. Every authentication attempt, authorization decision, and data access is logged with timestamps and user information.

### Security Layers

| Layer | Purpose | Implementation |
|-------|---------|----------------|
| **Network** | Protect against network attacks | TLS/SSL, firewall rules, DDoS protection |
| **Application** | Secure application logic | Input validation, CSRF protection, XSS prevention |
| **Authentication** | Verify user identity | Password hashing, MFA, session management |
| **Authorization** | Control access | RBAC, permission checks, resource ownership |
| **Data** | Protect sensitive information | Encryption at rest, encryption in transit |
| **Audit** | Track security events | Comprehensive logging, alerting, monitoring |

---

## Authentication

### Class: AuthenticationManager

```python
from src.system.auth import AuthenticationManager

class AuthenticationManager:
    """
    Manages user authentication and session handling.
    
    Supports multiple authentication methods including:
    - Username/password authentication
    - API key authentication
    - OAuth 2.0 authentication
    - Multi-factor authentication (MFA)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize authentication manager.
        
        Args:
            config: Authentication configuration
        """
        pass
    
    def authenticate(self, 
                    username: str, 
                    password: str) -> Dict[str, Any]:
        """
        Authenticate user with username and password.
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            Dictionary containing authentication token and user info
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    def create_session(self, user_id: str) -> str:
        """
        Create a new session for authenticated user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session token
        """
        pass
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """
        Validate a session token.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User information if session valid
            
        Raises:
            SessionExpiredError: If session has expired
            InvalidSessionError: If session is invalid
        """
        pass
    
    def logout(self, session_token: str) -> bool:
        """
        Logout user and invalidate session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            True if logout successful
        """
        pass
```

### Basic Authentication

```python
from src.system.auth import AuthenticationManager

# Initialize authentication manager
auth = AuthenticationManager({
    "session_timeout": 3600,  # 1 hour
    "max_login_attempts": 5,
    "lockout_duration": 900  # 15 minutes
})

# Authenticate user
try:
    result = auth.authenticate(
        username="user@example.com",
        password="SecurePassword123!"
    )
    
    session_token = result['session_token']
    user_info = result['user']
    
    print(f"Authentication successful for {user_info['username']}")
    print(f"Session token: {session_token}")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Session Management

```python
# Create session
session_token = auth.create_session(user_id="user_123")

# Validate session
try:
    user_info = auth.validate_session(session_token)
    print(f"Session valid for user: {user_info['username']}")
except SessionExpiredError:
    print("Session has expired, please login again")
except InvalidSessionError:
    print("Invalid session token")

# Logout
auth.logout(session_token)
print("User logged out successfully")
```

### API Key Authentication

```python
from src.system.auth import APIKeyManager

# Initialize API key manager
api_keys = APIKeyManager()

# Generate API key
api_key = api_keys.generate_key(
    user_id="user_123",
    name="Production API Key",
    scopes=["read", "write"],
    expires_in_days=365
)

print(f"API Key: {api_key['key']}")
print(f"Expires: {api_key['expires_at']}")

# Validate API key
try:
    key_info = api_keys.validate_key(api_key['key'])
    print(f"API key valid for user: {key_info['user_id']}")
except InvalidAPIKeyError:
    print("Invalid API key")
```

### Multi-Factor Authentication

```python
from src.system.auth import MFAManager

# Initialize MFA manager
mfa = MFAManager()

# Enable MFA for user
secret = mfa.enable_mfa(user_id="user_123")
qr_code = mfa.generate_qr_code(secret)

print(f"Scan this QR code with your authenticator app:")
print(qr_code)

# Verify MFA code
try:
    mfa.verify_code(
        user_id="user_123",
        code="123456"
    )
    print("MFA verification successful")
except InvalidMFACodeError:
    print("Invalid MFA code")
```

---

## Authorization and RBAC

### Class: UserManager

```python
from src.system.user_manager import UserManager, UserRole

class UserManager:
    """
    Manages users, roles, and permissions with RBAC.
    """
    
    def create_user(self,
                   username: str,
                   email: str,
                   password: str,
                   role: UserRole = UserRole.USER) -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Unique username
            email: User's email address
            password: User's password (will be hashed)
            role: User's role (default: USER)
            
        Returns:
            Created user information
        """
        pass
    
    def assign_role(self, user_id: str, role: UserRole) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User identifier
            role: Role to assign
            
        Returns:
            True if role assigned successfully
        """
        pass
    
    def check_permission(self,
                        user_id: str,
                        permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User identifier
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        pass
```

### User Roles

```python
from src.system.user_manager import UserRole

# Available roles
roles = {
    UserRole.ADMIN: "Full system access",
    UserRole.MANAGER: "Manage users and content",
    UserRole.USER: "Standard user access",
    UserRole.GUEST: "Limited read-only access"
}

for role, description in roles.items():
    print(f"{role.value}: {description}")
```

### Role Assignment

```python
from src.system.user_manager import UserManager, UserRole
from pathlib import Path

# Initialize user manager
user_manager = UserManager(Path("./data/users"))

# Create user with specific role
user = user_manager.create_user(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123!",
    role=UserRole.USER
)

# Promote user to manager
user_manager.assign_role(user['user_id'], UserRole.MANAGER)
print(f"User promoted to {UserRole.MANAGER.value}")

# Check user's role
current_role = user_manager.get_user_role(user['user_id'])
print(f"Current role: {current_role.value}")
```

### Permission Checks

```python
from src.system.user_manager import Permission

# Check specific permission
if user_manager.check_permission(user_id, Permission.MANAGE_USERS):
    # User can manage other users
    print("Permission granted: Manage users")
else:
    print("Permission denied")

# Check multiple permissions
required_permissions = [
    Permission.MANAGE_USERS,
    Permission.MANAGE_ROLES,
    Permission.VIEW_AUDIT_LOGS
]

if user_manager.has_all_permissions(user_id, required_permissions):
    print("User has all required permissions")
```

---

## User Management

### Creating Users

```python
from src.system.user_manager import UserManager
from pathlib import Path

user_manager = UserManager(Path("./data/users"))

# Create standard user
user = user_manager.create_user(
    username="alice",
    email="alice@example.com",
    password="AliceSecure123!",
    role=UserRole.USER
)

print(f"User created: {user['username']}")
print(f"User ID: {user['user_id']}")
```

### Updating Users

```python
# Update user information
user_manager.update_user(
    user_id="user_123",
    email="newemail@example.com",
    display_name="Alice Johnson"
)

# Change password
user_manager.change_password(
    user_id="user_123",
    old_password="AliceSecure123!",
    new_password="NewSecurePass456!"
)

# Reset password (admin only)
if user_manager.check_permission(admin_id, Permission.MANAGE_USERS):
    new_password = user_manager.reset_password(user_id="user_123")
    print(f"Password reset. Temporary password: {new_password}")
```

### Deleting Users

```python
# Soft delete (deactivate)
user_manager.deactivate_user(user_id="user_123")
print("User deactivated")

# Hard delete (admin only)
if user_manager.check_permission(admin_id, Permission.DELETE_USERS):
    user_manager.delete_user(user_id="user_123")
    print("User permanently deleted")
```

---

## Permissions

### Permission System

```python
from src.system.user_manager import Permission

# Available permissions
permissions = {
    # User management
    Permission.MANAGE_USERS: "Create, update, delete users",
    Permission.MANAGE_ROLES: "Assign and modify user roles",
    Permission.VIEW_USERS: "View user information",
    
    # Content management
    Permission.CREATE_CONTENT: "Create new content",
    Permission.EDIT_CONTENT: "Edit existing content",
    Permission.DELETE_CONTENT: "Delete content",
    Permission.PUBLISH_CONTENT: "Publish content",
    
    # System administration
    Permission.MANAGE_SYSTEM: "Configure system settings",
    Permission.VIEW_AUDIT_LOGS: "View security audit logs",
    Permission.MANAGE_BILLING: "Manage billing and subscriptions",
    
    # API access
    Permission.API_ACCESS: "Access API endpoints",
    Permission.API_WRITE: "Write via API",
    Permission.API_ADMIN: "Administrative API access"
}
```

### Custom Permissions

```python
# Grant custom permission
user_manager.grant_permission(
    user_id="user_123",
    permission="custom.feature.access"
)

# Revoke permission
user_manager.revoke_permission(
    user_id="user_123",
    permission="custom.feature.access"
)

# List user permissions
permissions = user_manager.list_permissions(user_id="user_123")
for perm in permissions:
    print(f"  - {perm}")
```

### Role-Permission Mapping

```python
# Define role permissions
role_permissions = {
    UserRole.ADMIN: [
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.MANAGE_SYSTEM,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_BILLING
    ],
    UserRole.MANAGER: [
        Permission.VIEW_USERS,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.PUBLISH_CONTENT
    ],
    UserRole.USER: [
        Permission.VIEW_USERS,
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT
    ],
    UserRole.GUEST: [
        Permission.VIEW_USERS
    ]
}

# Apply role permissions
for role, perms in role_permissions.items():
    user_manager.set_role_permissions(role, perms)
```

---

## Encryption

### Password Hashing

```python
from src.system.password_utils import hasher

# Hash password
password_hash = hasher.hash("MySecurePassword123!")
print(f"Password hash: {password_hash}")

# Verify password
is_valid = hasher.verify("MySecurePassword123!", password_hash)
if is_valid:
    print("Password verified successfully")
else:
    print("Invalid password")

# Check if rehash needed (algorithm upgraded)
if hasher.check_needs_rehash(password_hash):
    new_hash = hasher.hash("MySecurePassword123!")
    # Update database with new hash
```

### Data Encryption

```python
from src.system.encryption import EncryptionManager

# Initialize encryption manager
encryption = EncryptionManager(key_file="/path/to/encryption.key")

# Encrypt sensitive data
encrypted = encryption.encrypt("Sensitive information")
print(f"Encrypted: {encrypted}")

# Decrypt data
decrypted = encryption.decrypt(encrypted)
print(f"Decrypted: {decrypted}")

# Encrypt file
encryption.encrypt_file(
    input_path="/path/to/sensitive.txt",
    output_path="/path/to/sensitive.txt.enc"
)

# Decrypt file
encryption.decrypt_file(
    input_path="/path/to/sensitive.txt.enc",
    output_path="/path/to/sensitive.txt"
)
```

### Secure Token Generation

```python
from src.system.security import TokenGenerator

# Initialize token generator
token_gen = TokenGenerator()

# Generate secure random token
token = token_gen.generate_token(length=32)
print(f"Token: {token}")

# Generate URL-safe token
url_token = token_gen.generate_url_safe_token(length=32)
print(f"URL-safe token: {url_token}")

# Generate UUID
uuid = token_gen.generate_uuid()
print(f"UUID: {uuid}")
```

---

## Security Auditing

### Audit Logging

```python
from src.system.audit import AuditLogger

# Initialize audit logger
audit = AuditLogger(log_dir="/var/log/daur_ai/audit")

# Log authentication event
audit.log_authentication(
    user_id="user_123",
    username="alice",
    success=True,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)

# Log authorization event
audit.log_authorization(
    user_id="user_123",
    resource="user_management",
    action="delete_user",
    granted=False,
    reason="Insufficient permissions"
)

# Log data access
audit.log_data_access(
    user_id="user_123",
    resource_type="user_profile",
    resource_id="user_456",
    action="read"
)

# Log security event
audit.log_security_event(
    event_type="suspicious_activity",
    severity="high",
    description="Multiple failed login attempts",
    user_id="user_123",
    ip_address="192.168.1.100"
)
```

### Audit Log Retrieval

```python
# Get audit logs for user
logs = audit.get_user_logs(
    user_id="user_123",
    start_date="2025-11-01",
    end_date="2025-11-12",
    event_types=["authentication", "authorization"]
)

for log in logs:
    print(f"{log['timestamp']}: {log['event_type']} - {log['description']}")

# Get security events
security_events = audit.get_security_events(
    severity="high",
    start_date="2025-11-01"
)

for event in security_events:
    print(f"[{event['severity'].upper()}] {event['description']}")
```

### Audit Reports

```python
# Generate audit report
report = audit.generate_report(
    start_date="2025-11-01",
    end_date="2025-11-12",
    format="pdf",
    output_path="/path/to/audit_report.pdf"
)

print(f"Audit report generated: {report['path']}")
print(f"Total events: {report['total_events']}")
print(f"Security incidents: {report['security_incidents']}")
```

---

## Rate Limiting

### Request Rate Limiting

```python
from src.system.rate_limiter import RateLimiter

# Initialize rate limiter
rate_limiter = RateLimiter({
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "requests_per_day": 10000
})

# Check rate limit
if rate_limiter.check_limit(user_id="user_123"):
    # Process request
    process_request()
else:
    # Rate limit exceeded
    return {"error": "Rate limit exceeded"}, 429
```

### Custom Rate Limits

```python
# Set custom rate limit for user
rate_limiter.set_user_limit(
    user_id="premium_user",
    requests_per_minute=120,
    requests_per_hour=5000
)

# Set rate limit by IP
rate_limiter.set_ip_limit(
    ip_address="192.168.1.100",
    requests_per_minute=30
)

# Get current usage
usage = rate_limiter.get_usage(user_id="user_123")
print(f"Requests this minute: {usage['minute']}")
print(f"Requests this hour: {usage['hour']}")
print(f"Requests today: {usage['day']}")
```

---

## Security Best Practices

### Password Policies

```python
from src.system.password_policy import PasswordPolicy

# Initialize password policy
policy = PasswordPolicy({
    "min_length": 12,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digits": True,
    "require_special": True,
    "prevent_common": True,
    "prevent_reuse": 5  # Prevent reusing last 5 passwords
})

# Validate password
is_valid, errors = policy.validate("WeakPass")
if not is_valid:
    print("Password does not meet requirements:")
    for error in errors:
        print(f"  - {error}")

# Generate strong password
strong_password = policy.generate_password(length=16)
print(f"Generated password: {strong_password}")
```

### Input Validation

```python
from src.system.validation import InputValidator

# Initialize validator
validator = InputValidator()

# Validate email
if validator.is_valid_email("user@example.com"):
    print("Valid email")

# Validate username
if validator.is_valid_username("alice_123"):
    print("Valid username")

# Sanitize input
clean_input = validator.sanitize(user_input)

# Prevent SQL injection
safe_query = validator.escape_sql(query_string)

# Prevent XSS
safe_html = validator.escape_html(html_content)
```

---

## Examples

### Complete Authentication Flow

```python
from src.system.auth import AuthenticationManager
from src.system.user_manager import UserManager, UserRole
from pathlib import Path

# Initialize managers
auth = AuthenticationManager()
user_manager = UserManager(Path("./data/users"))

# 1. Create user
user = user_manager.create_user(
    username="alice",
    email="alice@example.com",
    password="SecurePass123!",
    role=UserRole.USER
)

# 2. Authenticate
try:
    auth_result = auth.authenticate("alice", "SecurePass123!")
    session_token = auth_result['session_token']
    print("Authentication successful")
except AuthenticationError:
    print("Authentication failed")
    exit(1)

# 3. Validate session
try:
    user_info = auth.validate_session(session_token)
    print(f"Session valid for {user_info['username']}")
except SessionExpiredError:
    print("Session expired")
    exit(1)

# 4. Check permissions
if user_manager.check_permission(user['user_id'], Permission.CREATE_CONTENT):
    print("User can create content")
    # Perform action
else:
    print("Permission denied")

# 5. Logout
auth.logout(session_token)
print("Logged out successfully")
```

### Secure API Endpoint

```python
from flask import Flask, request, jsonify
from src.system.auth import AuthenticationManager
from src.system.rate_limiter import RateLimiter

app = Flask(__name__)
auth = AuthenticationManager()
rate_limiter = RateLimiter()

@app.route('/api/data', methods=['GET'])
def get_data():
    # 1. Validate API key
    api_key = request.headers.get('X-API-Key')
    try:
        user_info = auth.validate_api_key(api_key)
    except InvalidAPIKeyError:
        return jsonify({"error": "Invalid API key"}), 401
    
    # 2. Check rate limit
    if not rate_limiter.check_limit(user_info['user_id']):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    # 3. Check permissions
    if not user_manager.check_permission(user_info['user_id'], Permission.API_ACCESS):
        return jsonify({"error": "Permission denied"}), 403
    
    # 4. Process request
    data = get_user_data(user_info['user_id'])
    
    # 5. Log access
    audit.log_data_access(
        user_id=user_info['user_id'],
        resource_type="api_data",
        action="read"
    )
    
    return jsonify(data), 200
```

---

## See Also

- [User Management API](./user-api.md) - User account operations
- [Billing API](./billing-api.md) - Subscription and payment security
- [System API](./system-api.md) - System integration and monitoring

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

