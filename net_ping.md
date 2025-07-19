## Network Ping-monitor for MacOS [file](https://github.com/skaboy71/MISC_SCRIPTS/blob/main/python/ping_monitor.py)
A comprehensive network monitoring tool specifically designed for macOS that provides real-time ping monitoring with automatic network adapter detection and flexible configuration options.

## Features

### 🌐 **Automatic Network Detection**
- **Native macOS Integration**: Uses `ipconfig getiflist` and `ipconfig getsummary` commands for reliable network adapter detection
- **Complete Network Info**: Displays interface names, local IPs, gateways, subnet masks, and connection status
- **Smart Fallback**: Automatically falls back to `ifconfig`/`netstat` parsing if needed
- **Clean Output**: Debug information only appears when troubleshooting is needed

### 📊 **Flexible Ping Monitoring**
- **Multiple Input Formats**: Support for JSON files, command-line hosts, or default DNS servers
- **Concurrent Pinging**: Multi-threaded execution for fast results across multiple hosts
- **Real-time Results**: Live response times with clear up/down status indicators
- **Customizable Parameters**: Adjustable timeout, packet count, and thread count

### ⏱️ **Continuous Monitoring**
- **Background Monitoring**: Continuous ping tests with configurable intervals
- **Summary Statistics**: Optional statistical summaries with success rates and average response times
- **Quiet Mode**: Show only failed hosts for focused troubleshooting
- **Export Results**: Save results to JSON or text files for analysis

### 🎯 **Smart Host Management**
- **Auto-Gateway Detection**: Automatically include detected gateways in ping tests
- **JSON Configuration**: Clean JSON format for host lists with labels
- **Default Fallbacks**: Sensible defaults (Google DNS, Cloudflare, etc.) when no hosts specified
- **Profile Name Support**: Clear labeling for easy identification

## Installation

### Requirements
- **macOS Sonoma or newer** (optimized for modern macOS versions)
- **Python 3.6+**
- **Required Package**: `tabulate` for formatted output

```bash
pip install tabulate
```

## Usage Examples

### Basic Usage

bash

```bash
# Show network info and ping default hosts
python3 ping_monitor.py

# Ping specific hosts with labels
python3 ping_monitor.py --hosts "Router:192.168.1.1" "Google:8.8.8.8" "Work:10.0.0.100"
```

### Continuous Monitoring

bash

```bash
# Monitor every 30 seconds with summary stats
python3 ping_monitor.py --continuous --summary

# Custom interval - check every 2 minutes
python3 ping_monitor.py --continuous --interval 120

# Monitor with host file, save results
python3 ping_monitor.py -f hosts.json --continuous --save results.json
```

### Advanced Options

bash

```bash
# Include all detected gateways in ping tests
python3 ping_monitor.py --include-gateways --summary

# Quiet mode - only show failures
python3 ping_monitor.py --continuous --quiet --interval 60

# Custom timeout and packet count
python3 ping_monitor.py --timeout 5 --count 3 --threads 20
```

## Configuration

### Host File Format (JSON)

json

```json
{
  "Home Router": "192.168.1.1",
  "Google DNS": "8.8.8.8",
  "Cloudflare DNS": "1.1.1.1",
  "Work Server": "10.0.0.100",
  "NAS Server": "192.168.1.50"
}
```

### Sample Output

```
🌐 Network Adapter Information:
============================================================
+------------+----------------+----------------+--------------+--------+
| Interface  | Local IP       | Gateway        | Subnet Mask  | Status |
+============+================+================+==============+========+
| en0        | 192.168.87.139 | 192.168.87.1   | 255.255.255.0| UP     |
+------------+----------------+----------------+--------------+--------+

Pinging 5 hosts with timeout=3s, count=1
============================================================

--- Ping Test at 2024-07-19 15:24:16 ---
+----------------+---------------+----------+-----------------+---------+
| Label          | IP Address    | Status   | Response Time   | Error   |
+================+===============+==========+=================+=========+
| Google DNS     | 8.8.8.8       | ✅ UP     | 12.3ms          |         |
| Home Router    | 192.168.87.1  | ✅ UP     | 2.1ms           |         |
| Work Server    | 10.0.0.100    | ❌ DOWN   | N/A             | Timeout |
+----------------+---------------+----------+-----------------+---------+

📊 Summary:
  Total hosts: 3
  Up: 2 (66.7%)
  Down: 1 (33.3%)
  Average response time: 7.2ms
```

## Command Line Options

```
OptionDescription
--hostsSpace-separated list of IP addresses or label:ip pairs
--file, -fJSON/CSV/text file containing hosts to ping
--timeout, -tPing timeout in seconds (default: 3)
--count, -cNumber of ping packets per host (default: 1)
--threadsNumber of concurrent threads (default: 10)
--continuousRun continuously until Ctrl+C
--interval, -iSeconds between continuous pings (default: 30)
--summaryShow summary statistics
--quiet, -qOnly show failed pings
--include-gatewaysAutomatically add detected gateways to ping list
--save, -sSave results to file (JSON or text format)
```

## Use Cases

- **Network Diagnostics**: Quickly identify connectivity issues across your network
- **Infrastructure Monitoring**: Continuous monitoring of critical servers and services
- **Home Network Health**: Monitor router, switches, and connected devices
- **Remote Work Setup**: Verify VPN and corporate network connectivity
- **ISP Performance**: Track internet connectivity and DNS response times
- **IoT Device Monitoring**: Keep tabs on smart home devices and sensors

## Why This Tool?

While there are many network monitoring solutions, this tool is specifically designed for:

- **macOS Optimization**: Native integration with macOS networking commands
- **Simplicity**: No complex setup or configuration files required
- **Flexibility**: Works for both quick diagnostics and long-term monitoring
- **Visibility**: Always shows your current network configuration alongside results
- **Portability**: Single Python script with minimal dependencies

Perfect for system administrators, network engineers, developers, and power users who need reliable network monitoring on macOS.

Built for macOS users who need reliable, simple network monitoring without the complexity of enterprise tools.*
