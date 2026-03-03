# Library Management System - Load Testing Suite

Complete load testing suite for performance testing, stress testing, and spike testing.

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `locustfile_comprehensive.py` | Main test file with multiple user types (LibraryUser, AdminUser, ReadOnlyUser) |
| `locustfile_spike.py` | Dedicated spike test for sudden traffic bursts |
| `run_tests.py` | Quick start script with interactive menu |
| `performance_monitor.py` | Real-time system metrics monitoring |
| `LOAD_TESTING_GUIDE.md` | Detailed testing guide and best practices |

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install locust psutil requests
```

### 2. Start Your API Server
```bash
python -m uvicorn app.main:app --reload
```

### 3. Run Tests

**Option A: Interactive Menu (Recommended)**
```bash
python run_tests.py
```

**Option B: Command Line**
```bash
# Load test
python run_tests.py load

# Stress test
python run_tests.py stress

# Spike test
python run_tests.py spike

# Run all tests
python run_tests.py all
```

**Option C: Direct Locust Commands**
```bash
# Load test (50 users, 5 min)
locust -f locustfile_comprehensive.py --users 50 --spawn-rate 5 --run-time 5m --headless

# Stress test (200 users, 10 min)
locust -f locustfile_comprehensive.py --users 200 --spawn-rate 10 --run-time 10m --headless

# Spike test (500 users, 2 min)
locust -f locustfile_spike.py --users 500 --spawn-rate 50 --run-time 2m --headless
```

## 📊 Test Types Explained

### 1. Load Test (Normal Traffic)
- **Users**: 50 concurrent
- **Duration**: 5 minutes
- **Purpose**: Validate normal operation
- **Expected**: Response time < 200ms, Failure rate < 1%

### 2. Stress Test (Beyond Capacity)
- **Users**: 200 concurrent
- **Duration**: 10 minutes
- **Purpose**: Find breaking point
- **Expected**: Response time < 500ms, Failure rate < 5%

### 3. Spike Test (Sudden Burst)
- **Users**: 500 concurrent
- **Spawn Rate**: 50/second (burst in 10 seconds)
- **Duration**: 2 minutes
- **Purpose**: Test resilience to traffic spikes
- **Watch For**: Rate limiting, recovery time

## 🔍 Monitoring During Tests

Run this in a separate terminal while tests are running:

```bash
python performance_monitor.py
```

This will track:
- CPU usage
- Memory usage
- API response times
- Active connections
- Thread count

Output is saved to `performance_metrics_YYYYMMDD_HHMMSS.csv`

## 📈 Using the Web UI

For interactive testing with real-time charts:

```bash
locust -f locustfile_comprehensive.py
```

Then open: http://localhost:8089

**Benefits:**
- Real-time charts
- Adjust load during test
- Better visualization

## 🎯 Test Scenarios in Files

### locustfile_comprehensive.py

**LibraryUser** (Regular users - 10x weight)
- Browse books (10x frequency)
- View book details (5x)
- Check transaction history (3x)
- Borrow books (2x)
- Return books (1x)

**AdminUser** (Admins - 1x weight)
- View all transactions
- View all users
- Create books
- Update books

**ReadOnlyUser** (Public browsing - 3x weight)
- Browse books
- View details
- No authentication needed

### locustfile_spike.py

**SpikeUser** (Aggressive behavior)
- Very short wait times (0.1-0.5s)
- High request rate
- Tests rate limiting

## 📋 Prerequisites Checklist

Before running tests:

- [ ] FastAPI server is running (`http://localhost:8000`)
- [ ] Redis is running (for caching)
- [ ] Database has test data (users and books)
- [ ] Test users exist:
  ```python
  username: "admin", password: "admin"
  username: "testuser1", password: "password123"
  # etc.
  ```
- [ ] Locust is installed (`pip install locust`)

## 🔧 Creating Test Data

```python
# Create test users
import requests

BASE_URL = "http://localhost:8000/api"

for i in range(1, 11):
    requests.post(f"{BASE_URL}/register", json={
        "email": f"testuser{i}@example.com",
        "username": f"testuser{i}",
        "password": "password123",
        "full_name": f"Test User {i}"
    })
```

## 📊 Reading Results

After tests complete, check:

1. **HTML Reports**: Open `*_report.html` files
   - Response time distribution
   - Requests per second
   - Failure analysis

2. **Performance Metrics**: Open CSV files
   - CPU/Memory trends
   - Connection counts
   - Response time correlation

3. **Console Output**: Real-time statistics
   - Request counts
   - Failure rates
   - Response times

## 🎯 Key Metrics to Watch

### Response Times
- **Excellent**: < 100ms
- **Good**: 100-300ms
- **Acceptable**: 300-500ms
- **Poor**: 500-1000ms
- **Critical**: > 1000ms

### Failure Rates
- **Excellent**: < 0.1%
- **Good**: 0.1-1%
- **Acceptable**: 1-5%
- **Critical**: > 5%

### Resource Usage
- **CPU**: Should stay < 80%
- **Memory**: Should not grow continuously
- **Connections**: Should not exceed pool size

## 🛠️ Troubleshooting

### High Failure Rate
```bash
# Check rate limiting settings
# Increase database connection pool
# Review application logs
```

### Slow Response Times
```bash
# Verify Redis cache is working
redis-cli MONITOR

# Check database queries
# Profile the application
```

### Connection Errors
```bash
# Increase file descriptor limit
ulimit -n 10000

# Check TIME_WAIT connections
netstat -an | grep TIME_WAIT | wc -l
```

## 📚 Advanced Usage

### Test Specific User Types Only

```bash
# Only read-only users
locust -f locustfile_comprehensive.py --class ReadOnlyUser --users 100 --spawn-rate 10

# Only authenticated users
locust -f locustfile_comprehensive.py --class LibraryUser --users 50 --spawn-rate 5
```

### Distributed Load Testing

For very high load across multiple machines:

```bash
# On master machine
locust -f locustfile_comprehensive.py --master

# On worker machines
locust -f locustfile_comprehensive.py --worker --master-host=192.168.1.100
```

### Custom Test Duration

```bash
# 30 minute endurance test
locust -f locustfile_comprehensive.py --users 100 --spawn-rate 5 --run-time 30m

# 2 hour soak test
locust -f locustfile_comprehensive.py --users 50 --spawn-rate 2 --run-time 2h
```

## 🎓 Best Practices

1. **Start Small**: Begin with 10-20 users
2. **Gradually Increase**: Add 10-20 users at a time
3. **Monitor Resources**: Watch CPU, memory, connections
4. **Test Regularly**: Part of CI/CD pipeline
5. **Document Results**: Keep historical data
6. **Realistic Data**: Match production patterns
7. **Test in Stages**: Load → Stress → Spike → Endurance

## 📞 Support

For issues or questions:
- Check `LOAD_TESTING_GUIDE.md` for detailed information
- Review Locust docs: https://docs.locust.io
- Check FastAPI performance: https://fastapi.tiangolo.com/deployment/

## 📝 Sample Commands

```bash
# Quick 1-minute test
locust -f locustfile_comprehensive.py --users 20 --spawn-rate 5 --run-time 1m --headless

# Medium 5-minute test with report
locust -f locustfile_comprehensive.py --users 50 --spawn-rate 5 --run-time 5m --html report.html --headless

# Full 10-minute stress test
locust -f locustfile_comprehensive.py --users 200 --spawn-rate 10 --run-time 10m --html stress_report.html --headless

# Extreme spike test
locust -f locustfile_spike.py --users 1000 --spawn-rate 100 --run-time 3m --html spike_report.html --headless
```

## 🎉 Success Criteria

Your system is performing well if:
- ✅ 95th percentile response time < 200ms under load
- ✅ Failure rate < 1%
- ✅ CPU usage < 80%
- ✅ Memory stable (no continuous growth)
- ✅ Recovers quickly after spike
- ✅ Rate limiting prevents system overload

---

**Ready to test?** Run `python run_tests.py` to get started! 🚀