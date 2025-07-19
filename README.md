# MISC_SCRIPTS
Miscellaneous scripts I have used or created

# Network Ping Monitor for macOS

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
