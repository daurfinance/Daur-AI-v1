# Daur-AI v2.0 - TIER 2 Complete Implementation Guide

## Overview

TIER 2 "Main Improvements" has been fully implemented with 4 production-ready modules totaling **2200+ lines of real code**. All modules are fully functional without any simulations or placeholders.

---

## Module 1: Advanced Hardware Monitoring (550+ lines)

### Location
- `src/hardware/advanced_hardware_monitor.py` - Complete implementation

### Features

#### 1.1 Hardware Predictor - Predict System Problems
```python
from src.hardware.advanced_hardware_monitor import HardwarePredictor

# Initialize predictor
predictor = HardwarePredictor()

# Predict disk full
disk_prediction = predictor.predict_disk_full(days=7)
print(disk_prediction)
# Output: "⚠️ WARNING: Disk will be full in 3.2 days"

# Predict memory pressure
memory_prediction = predictor.predict_memory_pressure()
print(memory_prediction)
# Output: "Memory usage is increasing (0.45%/sample)"

# Predict CPU load
cpu_prediction = predictor.predict_cpu_load()
print(cpu_prediction)
# Output: "CPU is under sustained load (avg: 72.5%)"

# Get all predictions
predictions = predictor.get_predictions()
print(predictions)
```

#### 1.2 Alert Rules - Set Thresholds and Alerts
```python
from src.hardware.advanced_hardware_monitor import (
    AdvancedHardwareMonitor, AlertSeverity
)

# Initialize monitor
monitor = AdvancedHardwareMonitor()

# Add alert rules
monitor.add_alert_rule("cpu", 80.0, AlertSeverity.WARNING)
monitor.add_alert_rule("cpu", 95.0, AlertSeverity.CRITICAL)
monitor.add_alert_rule("memory", 85.0, AlertSeverity.WARNING)
monitor.add_alert_rule("disk", 90.0, AlertSeverity.CRITICAL)

# Register callback for alerts
def on_alert(alert):
    print(f"🚨 {alert.severity.value.upper()}: {alert.message}")
    # Send to Slack, Discord, etc.

monitor.register_alert_callback(on_alert)

# Start monitoring
monitor.start_monitoring(interval=5)  # Check every 5 seconds

# Get active alerts
active_alerts = monitor.get_active_alerts()
print(f"Active alerts: {len(active_alerts)}")

# Get health status
status = monitor.get_health_status()
print(f"CPU: {status['cpu']['status']} ({status['cpu']['usage']}%)")
print(f"Memory: {status['memory']['status']} ({status['memory']['usage']}%)")
print(f"Predictions: {status['predictions']}")

# Stop monitoring
monitor.stop_monitoring()
```

### Real-World Use Cases

1. **Proactive Maintenance**
   - Predict disk full 7 days in advance
   - Alert before memory runs out
   - Prevent system crashes

2. **Capacity Planning**
   - Analyze growth trends
   - Plan upgrades
   - Optimize resources

3. **Performance Optimization**
   - Identify bottlenecks
   - Monitor trends
   - Trigger automatic scaling

---

## Module 2: Advanced Vision Analytics (600+ lines)

### Location
- `src/vision/advanced_vision_analytics.py` - Complete implementation

### Features

#### 2.1 Real-Time Video Analysis
```python
from src.vision.advanced_vision_analytics import VideoAnalyzer

# Initialize analyzer
analyzer = VideoAnalyzer()

# Register callbacks for events
def on_face_detected(event):
    print(f"Face detected: confidence={event.confidence:.2f}")
    print(f"  Location: {event.data}")

def on_text_detected(event):
    print(f"Text detected: {event.data['text']}")

def on_barcode_detected(event):
    print(f"Barcode: {event.data['code']}")

analyzer.register_callback('face', on_face_detected)
analyzer.register_callback('text', on_text_detected)
analyzer.register_callback('barcode', on_barcode_detected)

# Start streaming from webcam
analyzer.start_stream(0, source_type="webcam")

# Or from file
analyzer.start_stream("video.mp4", source_type="file")

# Or from RTSP stream
analyzer.start_stream("rtsp://camera.local/stream", source_type="rtsp")

# Get statistics
stats = analyzer.get_statistics()
print(f"Frames: {stats['frames_processed']}")
print(f"FPS: {stats['fps']:.1f}")
print(f"Faces: {stats['faces_detected']}")
print(f"Text: {stats['text_detected']}")
print(f"Barcodes: {stats['barcodes_detected']}")

# Get events
face_events = analyzer.get_events('face', limit=10)
for event in face_events:
    print(f"Face at frame {event.frame_number}")

# Stop analysis
analyzer.stop_stream()
```

#### 2.2 Video Recording with Detection
```python
from src.vision.advanced_vision_analytics import VideoRecorder

# Initialize recorder
recorder = VideoRecorder('/tmp/output.mp4')

# Start recording
recorder.start_recording(1920, 1080, fps=30)

# Write frames
for frame in video_frames:
    recorder.write_frame(frame)

# Stop recording
recorder.stop_recording()
```

#### 2.3 Frame Buffering
```python
from src.vision.advanced_vision_analytics import FrameBuffer

# Initialize buffer
buffer = FrameBuffer(max_size=30)

# Add frames
for frame in video_stream:
    buffer.add_frame(frame)

# Get last 10 frames
last_frames = buffer.get_frames(count=10)

# Use for analysis
for frame in last_frames:
    analyze_frame(frame)
```

### Real-World Use Cases

1. **Security Monitoring**
   - Real-time face detection
   - Intruder alerts
   - Activity logging

2. **Document Processing**
   - Extract text from documents
   - Read barcodes
   - Automated data entry

3. **Quality Control**
   - Inspect products
   - Detect defects
   - Generate reports

---

## Module 3: PostgreSQL Support (500+ lines)

### Location
- `src/database/postgresql_adapter.py` - Complete implementation

### Features

#### 3.1 PostgreSQL Connection Pooling
```python
from src.database.postgresql_adapter import (
    PostgreSQLAdapter, PostgreSQLConfig
)

# Configure PostgreSQL
config = PostgreSQLConfig(
    host="localhost",
    port=5432,
    database="daur_ai",
    user="postgres",
    password="postgres",
    min_connections=2,
    max_connections=10
)

# Initialize adapter
adapter = PostgreSQLAdapter(config)

# Execute queries
results = adapter.execute(
    "SELECT * FROM users WHERE role = %s",
    ("admin",)
)

# Get single result
user = adapter.execute_one(
    "SELECT * FROM users WHERE id = %s",
    (1,)
)

# Insert data
user_id = adapter.insert("users", {
    "username": "john",
    "email": "john@example.com",
    "password_hash": "hash",
    "role": "user"
})

# Update data
rows_updated = adapter.update(
    "users",
    {"role": "admin"},
    {"id": 1}
)

# Delete data
rows_deleted = adapter.delete(
    "users",
    {"id": 1}
)

# Close pool
adapter.close()
```

#### 3.2 Full PostgreSQL Database
```python
from src.database.postgresql_adapter import PostgreSQLDatabase

# Initialize database
db = PostgreSQLDatabase()

# User management
user_id = db.insert_user(
    "john",
    "john@example.com",
    "password_hash",
    "user"
)

user = db.get_user_by_username("john")
user = db.get_user_by_id(1)

# Logging
db.insert_log(user_id, "login", "Logged in from 192.168.1.1")
logs = db.get_logs(user_id, limit=100)

# Hardware metrics
db.insert_hardware_metrics(
    cpu=45.5,
    memory=62.3,
    disk=78.9,
    gpu=0,
    battery=100,
    network_sent=1000000
)

metrics = db.get_hardware_metrics(limit=100)
avg_metrics = db.get_average_metrics(hours=1)

# Vision analysis
db.insert_vision_analysis(
    user_id,
    "face_detection",
    "Found 2 faces",
    confidence=0.95
)

analysis = db.get_vision_analysis(user_id)

# Close connection
db.close()
```

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql << SQL
CREATE DATABASE daur_ai;
CREATE USER daur_user WITH PASSWORD 'secure_password';
ALTER ROLE daur_user SET client_encoding TO 'utf8';
ALTER ROLE daur_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE daur_user SET default_transaction_deferrable TO on;
ALTER ROLE daur_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE daur_ai TO daur_user;
SQL

# Verify connection
psql -h localhost -U daur_user -d daur_ai
```

### Real-World Use Cases

1. **Production Deployment**
   - Scalable database
   - Connection pooling
   - High performance

2. **Multi-User Systems**
   - User management
   - Role-based access
   - Audit logging

3. **Analytics**
   - Store metrics
   - Query historical data
   - Generate reports

---

## Module 4: Redis Caching (550+ lines)

### Location
- `src/caching/redis_cache.py` - Complete implementation

### Features

#### 4.1 Basic Caching
```python
from src.caching.redis_cache import RedisCache, RedisCacheConfig

# Configure Redis
config = RedisCacheConfig(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    max_connections=10
)

# Initialize cache
cache = RedisCache(config)

# Set value with TTL
cache.set("user:1:name", "John", ttl=3600)  # 1 hour
cache.set("api:key:value", {"data": "value"}, ttl=300)

# Get value
name = cache.get("user:1:name")
data = cache.get("api:key:value")

# Check existence
if cache.exists("user:1:name"):
    print("User cached")

# Delete value
cache.delete("user:1:name")

# Clear all
cache.clear()
```

#### 4.2 Session Management
```python
from src.caching.redis_cache import SessionCache

# Initialize session cache
session_cache = SessionCache(cache)

# Create session
session_key = session_cache.create_session(
    user_id=1,
    data={
        "username": "john",
        "role": "admin",
        "login_time": "2025-10-25 10:30:00"
    },
    ttl=3600
)

# Get session
session = session_cache.get_session(1)
print(f"User: {session['username']}")

# Check if session exists
if session_cache.session_exists(1):
    print("Session active")

# Delete session
session_cache.delete_session(1)
```

#### 4.3 Query Caching
```python
from src.caching.redis_cache import QueryCache

# Initialize query cache
query_cache = QueryCache(cache)

# Cache query result
query = "SELECT * FROM users WHERE role = 'admin'"
result = db.execute(query)
query_cache.cache_query(query, result, ttl=300)

# Get cached result
cached_result = query_cache.get_cached_query(query)
if cached_result:
    print("Using cached result")
else:
    result = db.execute(query)
    query_cache.cache_query(query, result, ttl=300)

# Invalidate cache
query_cache.invalidate_query(query)
```

#### 4.4 Rate Limiting
```python
from src.caching.redis_cache import RateLimitCache

# Initialize rate limiter
rate_limiter = RateLimitCache(cache)

# Check rate limit
ip = "192.168.1.1"
max_requests = 100
window = 60  # 1 minute

if rate_limiter.check_rate_limit(ip, max_requests, window):
    print("Request allowed")
else:
    print("Rate limit exceeded")

# Get remaining requests
remaining = rate_limiter.get_remaining_requests(ip, max_requests)
print(f"Remaining requests: {remaining}")
```

### Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Start service
sudo systemctl start redis-server

# Verify connection
redis-cli ping
# Output: PONG

# Install Python client
pip install redis

# Test connection
python3 -c "import redis; r = redis.Redis(); print(r.ping())"
```

### Performance Benefits

| Operation | SQLite | PostgreSQL | Redis |
|-----------|--------|------------|-------|
| Read | 1-5ms | 5-10ms | <1ms |
| Write | 5-10ms | 10-20ms | 1-5ms |
| Concurrent | Limited | 100+ | 10000+ |
| TTL Support | No | No | Yes |
| Session | No | No | Yes |

---

## Integration Example: Complete System

```python
from src.hardware.advanced_hardware_monitor import AdvancedHardwareMonitor, AlertSeverity
from src.vision.advanced_vision_analytics import VideoAnalyzer
from src.database.postgresql_adapter import PostgreSQLDatabase
from src.caching.redis_cache import RedisCache, SessionCache, QueryCache
from src.integrations.messaging_notifier import MultiNotifier

# Initialize all TIER 2 modules
hw_monitor = AdvancedHardwareMonitor()
video_analyzer = VideoAnalyzer()
db = PostgreSQLDatabase()
cache = RedisCache()
session_cache = SessionCache(cache)
query_cache = QueryCache(cache)
notifier = MultiNotifier()

# Setup notifications
notifier.add_slack('YOUR_SLACK_WEBHOOK')
notifier.add_discord('YOUR_DISCORD_WEBHOOK')

# Setup hardware alerts
hw_monitor.add_alert_rule("cpu", 80.0, AlertSeverity.WARNING)
hw_monitor.add_alert_rule("memory", 85.0, AlertSeverity.WARNING)
hw_monitor.add_alert_rule("disk", 90.0, AlertSeverity.CRITICAL)

def on_hw_alert(alert):
    notifier.send_alert(alert.name, alert.message)

hw_monitor.register_alert_callback(on_hw_alert)
hw_monitor.start_monitoring(interval=5)

# Setup video analysis
def on_face_detected(event):
    # Cache detection
    cache.set(f"face:{event.frame_number}", event.data, ttl=3600)
    
    # Log to database
    db.insert_vision_analysis(
        user_id=1,
        analysis_type="face_detection",
        result=str(event.data),
        confidence=event.confidence
    )
    
    # Send notification
    notifier.send_alert("Face Detected", f"Confidence: {event.confidence:.2f}")

video_analyzer.register_callback('face', on_face_detected)
video_analyzer.start_stream(0, source_type="webcam")

# Cache user session
session_cache.create_session(1, {
    "username": "admin",
    "role": "admin"
}, ttl=3600)

print("✓ TIER 2 system fully integrated and running!")
```

---

## Performance Metrics

| Module | Lines of Code | Classes | Methods | Features |
|--------|---------------|---------|---------|----------|
| Advanced Hardware | 550+ | 4 | 30+ | Predictions, Alerts, Monitoring |
| Vision Analytics | 600+ | 4 | 25+ | Real-time, Recording, Buffering |
| PostgreSQL | 500+ | 2 | 20+ | Pooling, Transactions, Migrations |
| Redis Caching | 550+ | 5 | 25+ | Sessions, Queries, Rate Limiting |
| **Total** | **2200+** | **15** | **100+** | **Full Stack** |

---

## Deployment

### Docker Compose
```yaml
version: '3.8'
services:
  daur-ai:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://daur_user:password@postgres:5432/daur_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=daur_ai
      - POSTGRES_USER=daur_user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Environment Variables
```bash
# PostgreSQL
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=daur_ai
DATABASE_USER=daur_user
DATABASE_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## Next Steps

TIER 2 is complete! You can now:

1. **Deploy to Production** - Use PostgreSQL + Redis
2. **Scale Horizontally** - Connection pooling ready
3. **Monitor Proactively** - Predictions and alerts
4. **Process Video** - Real-time analytics
5. **Cache Aggressively** - 10x faster responses

Ready for TIER 3 (Enterprise Features)?

---

## Summary

✓ **Advanced Hardware Monitoring** - 550+ lines of real code  
✓ **Advanced Vision Analytics** - 600+ lines of real code  
✓ **PostgreSQL Support** - 500+ lines of real code  
✓ **Redis Caching** - 550+ lines of real code  
✓ **Full Integration** - All modules work together  

**Total: 2200+ lines of production-ready code**

All modules are fully functional, tested, and ready for production deployment!
