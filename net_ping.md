# Network Ping Monitor for macOS

A comprehensive network monitoring tool specifically designed for macOS that provides real-time ping monitoring with automatic network adapter detection, DNS server discovery, and flexible output options including auto-refreshing HTML dashboards.

## Features

### 🌐 **Automatic Network Detection**
- **Native macOS Integration**: Uses `ipconfig getiflist` and `ipconfig getsummary` commands for reliable network adapter detection
- **Complete Network Info**: Displays interface names, local IPs, gateways, subnet masks, and connection status
- **Smart Fallback**: Automatically falls back to `ifconfig`/`netstat` parsing if needed
- **Clean Output**: Debug information only appears when troubleshooting is needed

### 🔍 **Automatic DNS Discovery**
- **Built-in DNS Detection**: Uses `scutil --dns` to automatically detect and monitor configured DNS servers
- **Smart DNS Labeling**: Automatically labels system DNS servers (e.g., "System-DNS-8.8.8.8")
- **No Configuration Required**: DNS servers are included automatically in all ping tests
- **VPN & Corporate Friendly**: Automatically detects DNS changes when connecting to VPNs or corporate networks

### 📊 **Flexible Ping Monitoring**
- **Multiple Input Formats**: Support for JSON files, command-line hosts, or intelligent defaults
- **Concurrent Pinging**: Multi-threaded execution for fast results across multiple hosts
- **Real-time Results**: Live response times with clear up/down status indicators
- **Customizable Parameters**: Adjustable timeout, packet count, and thread count
- **Duplicate Prevention**: Automatically prevents duplicate hosts in ping lists

### ⏱️ **Continuous Monitoring**
- **Background Monitoring**: Continuous ping tests with configurable intervals (default: 30 seconds)
- **Summary Statistics**: Optional statistical summaries with success rates and average response times
- **Quiet Mode**: Show only failed hosts for focused troubleshooting
- **Auto-refresh HTML**: Generate web dashboards that update every 5 seconds
- **Export Results**: Save results to JSON, text, or HTML files for analysis

### 🎯 **Smart Host Management**
- **Auto-Gateway Detection**: Optionally include detected gateways in ping tests
- **JSON Configuration**: Clean JSON format for host lists with descriptive labels
- **Intelligent Defaults**: Sensible fallbacks (Google DNS, Cloudflare, OpenDNS) when no hosts specified
- **Profile Name Support**: Clear labeling for easy identification of network components

### 📱 **Modern Web Dashboard**
- **Auto-refreshing HTML**: Beautiful web interface that updates every 5 seconds in continuous mode
- **Responsive Design**: Mobile-friendly layout with modern CSS and gradients
- **Real-time Status**: Color-coded status indicators and live response time updates
- **Network Topology View**: Complete network adapter information displayed alongside ping results

## Installation

### Requirements
- **macOS Sonoma or newer** (optimized for modern macOS versions)
- **Python 3.6+**
- **Required Package**: `tabulate` for formatted output

```bash
pip install tabulate
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/network-ping-monitor.git
cd network-ping-monitor

# Install dependencies
pip install tabulate

# Run with default settings (includes automatic DNS detection)
python3 ping_monitor.py
```

## Usage Examples

### Basic Usage
```bash
# Show network info, ping default hosts + auto-detected DNS servers
python3 ping_monitor.py

# Ping specific hosts with labels (DNS servers still auto-added)
python3 ping_monitor.py --hosts "Router:192.168.1.1" "Work:10.0.0.100"

# Include gateways along with DNS servers
python3 ping_monitor.py --include-gateways --summary
```

### Continuous Monitoring
```bash
# Monitor every 30 seconds with summary stats and HTML output
python3 ping_monitor.py --continuous --summary --save dashboard.html

# Custom interval - check every 2 minutes
python3 ping_monitor.py --continuous --interval 120

# Monitor with host file, include gateways, save to auto-refreshing HTML
python3 ping_monitor.py -f hosts.json --include-gateways --continuous --save monitor.html
```

### Advanced Options
```bash
# Quiet mode - only show failures with custom timeout
python3 ping_monitor.py --continuous --quiet --timeout 5 --interval 60

# High-frequency monitoring with custom packet count
python3 ping_monitor.py --timeout 2 --count 3 --threads 20 --summary

# Generate one-time HTML report
python3 ping_monitor.py --include-gateways --save network-report.html
```

## Configuration

### Host File Format (JSON)
```json
{
  "Home Router": "192.168.1.1",
  "Work Server": "10.0.0.100",
  "NAS Server": "192.168.1.50",
  "Printer": "192.168.1.200",
  "Smart TV": "192.168.1.150"
}
```

### Sample Console Output
```
🌐 Network Adapter Information:
============================================================
+------------+----------------+----------------+--------------+--------+
| Interface  | Local IP       | Gateway        | Subnet Mask  | Status |
+============+================+================+==============+========+
| en0        | 192.168.87.139 | 192.168.87.1   | 255.255.255.0| UP     |
+------------+----------------+----------------+--------------+--------+

Debug: Found 2 DNS servers: ['8.8.8.8', '8.8.4.4']
Added DNS server: System-DNS-8.8.8.8 (8.8.8.8)
Added DNS server: System-DNS-8.8.4.4 (8.8.4.4)
Added gateway: en0-Gateway (192.168.87.1)
Pinging 8 hosts with timeout=3s, count=1
============================================================

--- Ping Test at 2024-07-19 15:24:16 ---
+--------------------+---------------+----------+-----------------+---------+
| Label              | IP Address    | Status   | Response Time   | Error   |
+====================+===============+==========+=================+=========+
| Google DNS         | 8.8.8.8       | ✅ UP     | 12.3ms          |         |
| Cloudflare DNS     | 1.1.1.1       | ✅ UP     | 8.7ms           |         |
| System-DNS-8.8.8.8 | 8.8.8.8       | ✅ UP     | 11.9ms          |         |
| System-DNS-8.8.4.4 | 8.8.4.4       | ✅ UP     | 15.2ms          |         |
| en0-Gateway        | 192.168.87.1  | ✅ UP     | 2.1ms           |         |
| Work Server        | 10.0.0.100    | ❌ DOWN   | N/A             | Timeout |
+--------------------+---------------+----------+-----------------+---------+

📊 Summary:
  Total hosts: 6
  Up: 5 (83.3%)
  Down: 1 (16.7%)
  Average response time: 10.0ms
```

### HTML Dashboard Features
- **Auto-refresh every 5 seconds** in continuous mode
- **Network adapter cards** with complete interface information
- **Color-coded ping results** with real-time status updates
- **Summary statistics** with visual progress indicators
- **Mobile-responsive design** for monitoring on any device
- **Modern UI** with gradients, shadows, and smooth animations

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--hosts` | | Space-separated list of IP addresses or `label:ip` pairs | None |
| `--file` | `-f` | JSON/CSV/text file containing hosts to ping | None |
| `--timeout` | `-t` | Ping timeout in seconds | 3 |
| `--count` | `-c` | Number of ping packets per host | 1 |
| `--threads` | | Number of concurrent threads | 10 |
| `--continuous` | | Run continuously until Ctrl+C | False |
| `--interval` | `-i` | Seconds between continuous pings | 30 |
| `--summary` | | Show summary statistics | False |
| `--quiet` | `-q` | Only show failed pings | False |
| `--include-gateways` | | Automatically add detected gateways to ping list | False |
| `--save` | `-s` | Save results to file (JSON, text, or HTML format) | None |

### Output Formats

| Extension | Format | Features |
|-----------|--------|----------|
| `.html` | Auto-refreshing web dashboard | Real-time updates, responsive design, summary cards |
| `.json` | Machine-readable JSON | Includes network adapters, timestamps, full results |
| `.txt` | Plain text report | Human-readable format with network info |

## What Gets Monitored Automatically

### Always Included:
- **DNS Servers**: Automatically detected via `scutil --dns`
- **Default External DNS**: Google DNS (8.8.8.8), Cloudflare (1.1.1.1), OpenDNS (208.67.222.222)

### Optionally Included:
- **Network Gateways**: Add with `--include-gateways` flag
- **Custom Hosts**: From JSON files or command line
- **Corporate Infrastructure**: When using host files

## Use Cases

- **Network Diagnostics**: Quickly identify connectivity issues across your entire network stack
- **DNS Troubleshooting**: Monitor DNS server response times and availability
- **Infrastructure Monitoring**: Continuous monitoring of critical servers and services  
- **Home Network Health**: Monitor router, switches, DNS, and connected devices
- **Remote Work Setup**: Verify VPN and corporate network connectivity
- **ISP Performance**: Track internet connectivity and DNS response times
- **Corporate IT**: Monitor company DNS servers and gateways automatically
- **NOC Dashboards**: Auto-refreshing HTML displays for network operations centers

## Advanced Features

### DNS Detection Intelligence
- Automatically detects system DNS servers using `scutil --dns`
- Identifies VPN DNS servers when connected
- Monitors corporate DNS servers in enterprise environments
- Falls back to `networksetup` commands if needed
- Prevents duplicate DNS entries

### Network Adapter Detection
- Uses native macOS `ipconfig` commands for reliability
- Automatically detects Wi-Fi, Ethernet, and VPN interfaces
- Shows complete network topology with IPs, gateways, and subnet masks
- Smart fallback to `ifconfig` parsing for compatibility

### Intelligent Host Management
- Prevents duplicate hosts across all sources (DNS, gateways, files, command line)
- Smart labeling system for automatic identification
- Preserves custom host labels from JSON files
- Automatically handles IP validation and localhost filtering

## Why This Tool?

While there are many network monitoring solutions, this tool is specifically designed for:

- **macOS Optimization**: Native integration with macOS networking commands
- **Zero Configuration**: Works perfectly out of the box with intelligent defaults
- **Complete Visibility**: Shows your entire network stack (adapters, DNS, gateways)
- **Modern Interface**: Beautiful HTML dashboards alongside traditional console output
- **Flexibility**: Works for quick diagnostics, continuous monitoring, and team dashboards
- **Portability**: Single Python script with minimal dependencies

Perfect for system administrators, network engineers, developers, IT professionals, and power users who need comprehensive, reliable network monitoring on macOS without complex setup or configuration.

## Building Standalone Executable

Create a portable executable that runs on any macOS system:

```bash
# Install PyInstaller
pip install pyinstaller

# Create standalone executable
pyinstaller --onefile --name "netmon" ping_monitor.py

# Distribute the executable from ./dist/netmon
```

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

MIT License - feel free to use and modify as needed.

---

*Built for macOS users who need comprehensive, intelligent network monitoring without the complexity of enterprise tools.*