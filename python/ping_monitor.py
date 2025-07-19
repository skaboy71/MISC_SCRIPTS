#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import json
import os
import socket
from datetime import datetime
from tabulate import tabulate
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class NetworkAdapter:
    def __init__(self, name, ip_address, gateway, subnet_mask=None, status="Unknown"):
        self.name = name
        self.ip_address = ip_address
        self.gateway = gateway
        self.subnet_mask = subnet_mask
        self.status = status
    
    def __str__(self):
        return f"{self.name}: {self.ip_address} -> {self.gateway}"

class PingResult:
    def __init__(self, label, ip, status, response_time=None, error=None):
        self.label = label
        self.ip = ip
        self.status = status  # 'up' or 'down'
        self.response_time = response_time  # in milliseconds
        self.error = error
        self.timestamp = datetime.now()
    
    def __str__(self):
        if self.status == 'up':
            return f"{self.label} ({self.ip}): ✅ UP ({self.response_time:.1f}ms)"
        else:
            return f"{self.label} ({self.ip}): ❌ DOWN"

def parse_ipconfig_summary(summary_text):
    """Parse the complex dictionary output from ipconfig getsummary"""
    ip_address = None
    subnet_mask = None
    router = None
    is_active = False
    
    try:
        # Look for key indicators in the text
        lines = summary_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if interface is active
            if 'LinkStatusActive : TRUE' in line:
                is_active = True
            
            # Look for IP address in Addresses array
            if 'Addresses : <array>' in line:
                # Look for the IP address in the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    addr_line = lines[j].strip()
                    if ':' in addr_line and not addr_line.startswith('<'):
                        # Extract IP address - format like "0 : 192.168.87.139"
                        parts = addr_line.split(':')
                        if len(parts) >= 2:
                            potential_ip = parts[1].strip()
                            # Basic IP validation
                            if potential_ip.count('.') == 3 and not potential_ip.startswith('169.254'):
                                ip_address = potential_ip
                                break
            
            # Look for Router
            elif 'Router :' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    router = parts[1].strip()
            
            # Look for SubnetMasks
            elif 'SubnetMasks : <array>' in line:
                # Look for subnet mask in the next few lines
                for j in range(i + 1, min(i + 5, len(lines))):
                    mask_line = lines[j].strip()
                    if ':' in mask_line and not mask_line.startswith('<'):
                        parts = mask_line.split(':')
                        if len(parts) >= 2:
                            potential_mask = parts[1].strip()
                            if potential_mask.count('.') == 3:
                                subnet_mask = potential_mask
                                break
        
        # For WiFi interfaces, if we have an IP and Router, consider it active
        if ip_address and router and not is_active:
            # Check if DHCP state is BOUND or similar active states
            if 'State : BOUND' in summary_text or 'IsPublished : TRUE' in summary_text:
                is_active = True
    
    except Exception as e:
        print(f"Error parsing summary: {e}")
    
    return ip_address, subnet_mask, router, is_active

def get_network_adapters():
    """Get information about all connected network adapters on macOS using ipconfig commands"""
    adapters = []
    debug_output = []  # Store debug messages
    
    try:
        # Get list of all network interfaces
        result = subprocess.run(['ipconfig', 'getiflist'], capture_output=True, text=True)
        if result.returncode != 0:
            debug_output.append("Error: ipconfig getiflist failed")
            return adapters
        
        interface_list = result.stdout.strip().split()
        debug_output.append(f"Debug: Found interfaces: {interface_list}")
        
        # Get details for each interface
        active_interfaces = {}
        for interface in interface_list:
            if interface.strip():  # Skip empty strings
                # Get summary for this interface
                result = subprocess.run(['ipconfig', 'getsummary', interface], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    summary = result.stdout.strip()
                    debug_output.append(f"Debug: {interface} summary: {summary[:200]}...")  # Show first 200 chars
                    
                    # Parse the complex dictionary format
                    ip_address, subnet_mask, router, is_active = parse_ipconfig_summary(summary)
                    
                    debug_output.append(f"Debug: {interface} parsed - IP: {ip_address}, Router: {router}, Active: {is_active}")
                    
                    # Store interface info if it has an IP address and appears active
                    if ip_address and (is_active or router):
                        active_interfaces[interface] = {
                            'ip': ip_address,
                            'netmask': subnet_mask,
                            'gateway': router,
                            'status': 'up' if (is_active or router) else 'down'
                        }
        
        debug_output.append(f"Debug: Active interfaces with IPs: {active_interfaces}")
        
        # If we didn't get gateways from ipconfig, try netstat as backup
        backup_gateways = {}
        if not any(info.get('gateway') for info in active_interfaces.values()):
            debug_output.append("Debug: No gateways found in ipconfig, trying netstat backup...")
            result = subprocess.run(['netstat', '-rn', '-f', 'inet'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    parts = line.split()
                    if len(parts) >= 6 and (parts[0] == 'default' or parts[0] == '0.0.0.0'):
                        gateway = parts[1]
                        interface = parts[5] if len(parts) > 5 else parts[4]
                        backup_gateways[interface] = gateway
                debug_output.append(f"Debug: Backup gateways from netstat: {backup_gateways}")
        
        # Create NetworkAdapter objects
        for interface, info in active_interfaces.items():
            gateway = info.get('gateway') or backup_gateways.get(interface, "No Gateway")
            
            adapters.append(NetworkAdapter(
                interface,
                info['ip'],
                gateway,
                info.get('netmask'),
                info['status']
            ))
        
        debug_output.append(f"Debug: Created {len(adapters)} network adapters")
        
        # Only show debug output if no adapters found OR if adapters found but none have gateways
        has_adapter_with_gateway = any(adapter.gateway != "No Gateway" for adapter in adapters)
        
        if not adapters or not has_adapter_with_gateway:
            print("\n".join(debug_output))
        
    except Exception as e:
        print(f"Error getting network adapters with ipconfig: {e}")
        # Fallback to original method if ipconfig fails
        print("Falling back to ifconfig method...")
        return get_network_adapters_fallback()
    
    return adapters

def get_network_adapters_fallback():
    """Fallback method using ifconfig if ipconfig fails"""
    adapters = []
    
    try:
        # Get network interfaces and their IPs
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        if result.returncode == 0:
            interfaces = {}
            current_interface = None
            
            for line in result.stdout.split('\n'):
                # New interface - starts without indentation and has a colon
                if line and not line.startswith('\t') and not line.startswith(' ') and ':' in line:
                    current_interface = line.split(':')[0].strip()
                    interfaces[current_interface] = {
                        'ip': None, 
                        'status': 'down', 
                        'netmask': None
                    }
                
                # Check if interface has UP flag
                elif current_interface and 'flags=' in line:
                    if 'UP' in line and not current_interface.startswith('lo'):
                        interfaces[current_interface]['status'] = 'up'
                
                # Get IPv4 address
                elif current_interface and line.strip().startswith('inet '):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_addr = parts[1]
                        if not ip_addr.startswith('127.') and not ip_addr.startswith('169.254.'):
                            interfaces[current_interface]['ip'] = ip_addr
                            
                            # Extract netmask
                            if 'netmask' in line:
                                try:
                                    netmask_idx = parts.index('netmask')
                                    if netmask_idx + 1 < len(parts):
                                        netmask_hex = parts[netmask_idx + 1]
                                        if netmask_hex.startswith('0x'):
                                            hex_val = int(netmask_hex, 16)
                                            netmask = '.'.join([
                                                str((hex_val >> 24) & 0xff),
                                                str((hex_val >> 16) & 0xff),
                                                str((hex_val >> 8) & 0xff),
                                                str(hex_val & 0xff)
                                            ])
                                            interfaces[current_interface]['netmask'] = netmask
                                except (ValueError, IndexError):
                                    pass
            
            # Get gateways
            gateways = {}
            result = subprocess.run(['netstat', '-rn', '-f', 'inet'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    parts = line.split()
                    if len(parts) >= 6 and (parts[0] == 'default' or parts[0] == '0.0.0.0'):
                        gateway = parts[1]
                        interface = parts[5] if len(parts) > 5 else parts[4]
                        gateways[interface] = gateway
            
            # Create adapters
            for interface, info in interfaces.items():
                if info['ip']:
                    gateway = gateways.get(interface, "No Gateway")
                    adapters.append(NetworkAdapter(
                        interface,
                        info['ip'],
                        gateway,
                        info.get('netmask'),
                        'up'  # Force up if it has an IP
                    ))
        
    except Exception as e:
        print(f"Error in fallback method: {e}")
    
    return adapters

def display_network_info():
    """Display network adapter information"""
    adapters = get_network_adapters()
    
    print("🌐 Network Adapter Information:")
    print("=" * 60)
    
    if not adapters:
        print("No active network adapters found.")
    else:
        table_data = []
        for adapter in adapters:
            table_data.append([
                adapter.name,
                adapter.ip_address,
                adapter.gateway,
                adapter.subnet_mask or "N/A",
                adapter.status.upper() if adapter.status else "Unknown"
            ])
        
        print(tabulate(table_data, headers=[
            "Interface", "Local IP", "Gateway", "Subnet Mask", "Status"
        ], tablefmt="grid"))
    
    print()
    return adapters
    def __init__(self, label, ip, status, response_time=None, error=None):
        self.label = label
        self.ip = ip
        self.status = status  # 'up' or 'down'
        self.response_time = response_time  # in milliseconds
        self.error = error
        self.timestamp = datetime.now()
    
    def __str__(self):
        if self.status == 'up':
            return f"{self.label} ({self.ip}): ✅ UP ({self.response_time:.1f}ms)"
        else:
            return f"{self.label} ({self.ip}): ❌ DOWN"

def ping_host(ip, timeout=3, count=1):
    """
    Ping a single host and return the result
    Returns tuple: (success, response_time_ms, error_message)
    """
    try:
        # macOS ping command
        cmd = ['ping', '-c', str(count), '-W', str(timeout * 1000), ip]
        
        # Execute the ping command
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout + 2
        )
        
        if result.returncode == 0:
            # Parse response time from output
            output = result.stdout
            
            # macOS: look for "time=5.123 ms"
            import re
            time_match = re.search(r'time=(\d+(?:\.\d+)?)\s*ms', output, re.IGNORECASE)
            if time_match:
                response_time = float(time_match.group(1))
            else:
                # Try alternative format: "5.123ms"
                time_match = re.search(r'(\d+(?:\.\d+)?)\s*ms', output, re.IGNORECASE)
                if time_match:
                    response_time = float(time_match.group(1))
                else:
                    response_time = 0.0
            
            return True, response_time, None
        else:
            return False, None, result.stderr.strip() or "Host unreachable"
            
    except subprocess.TimeoutExpired:
        return False, None, "Timeout"
    except Exception as e:
        return False, None, str(e)

def ping_host_wrapper(host_info, timeout=3, count=1):
    """Wrapper function for threading"""
    label, ip = host_info
    success, response_time, error = ping_host(ip, timeout, count)
    
    if success:
        return PingResult(label, ip, 'up', response_time)
    else:
        return PingResult(label, ip, 'down', error=error)

def load_hosts_from_file(filename):
    """Load hosts from a file (JSON, CSV, or plain text format)"""
    hosts = []
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return hosts
    
    try:
        # Try to load as JSON first
        with open(filename, 'r') as f:
            if filename.endswith('.json'):
                data = json.load(f)
                if isinstance(data, dict):
                    hosts = [(label, ip) for label, ip in data.items()]
                elif isinstance(data, list):
                    hosts = [(item.get('label', item.get('name', f'Host-{i}')), 
                             item.get('ip', item.get('address', item))) 
                            for i, item in enumerate(data)]
            else:
                # Try to parse as plain text or CSV
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Try comma-separated format: label,ip
                    if ',' in line:
                        parts = [part.strip() for part in line.split(',')]
                        if len(parts) >= 2:
                            hosts.append((parts[0], parts[1]))
                    # Try space-separated format: label ip
                    elif ' ' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            hosts.append((parts[0], parts[1]))
                    # Just IP address
                    else:
                        hosts.append((f'Host-{line}', line))
                        
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
    
    return hosts

def save_results_to_file(results, filename):
    """Save ping results to a file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if filename.endswith('.json'):
            # Save as JSON
            data = {
                'timestamp': timestamp,
                'results': [
                    {
                        'label': r.label,
                        'ip': r.ip,
                        'status': r.status,
                        'response_time': r.response_time,
                        'error': r.error
                    }
                    for r in results
                ]
            }
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            # Save as text
            with open(filename, 'w') as f:
                f.write(f"Ping Results - {timestamp}\n")
                f.write("=" * 50 + "\n\n")
                for result in results:
                    f.write(f"{result}\n")
                
        print(f"Results saved to '{filename}'")
    except Exception as e:
        print(f"Error saving results to '{filename}': {e}")

def main():
    parser = argparse.ArgumentParser(description='Network Ping Monitor')
    parser.add_argument('--hosts', nargs='+', help='Space-separated list of IP addresses or host:ip pairs')
    parser.add_argument('--file', '-f', help='File containing hosts to ping (JSON, CSV, or text format)')
    parser.add_argument('--timeout', '-t', type=int, default=3, help='Ping timeout in seconds (default: 3)')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of ping packets to send (default: 1)')
    parser.add_argument('--threads', type=int, default=10, help='Number of concurrent threads (default: 10)')
    parser.add_argument('--continuous', action='store_true', help='Run continuously until Ctrl+C')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Interval between continuous pings in seconds (default: 30)')
    parser.add_argument('--save', '-s', help='Save results to file (JSON or text format)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show failed pings')
    parser.add_argument('--summary', action='store_true', help='Show summary statistics')
    parser.add_argument('--include-gateways', action='store_true', help='Automatically include gateways in ping list')
    
    args = parser.parse_args()
    
    # Always show network information first
    adapters = display_network_info()
    
    # Default hosts if none provided
    default_hosts = [
        ('Google DNS', '8.8.8.8'),
        ('Cloudflare DNS', '1.1.1.1'),
        ('OpenDNS', '208.67.222.222'),
        ('Local Router', '192.168.1.1'),
        ('Adobe DNS', '208.67.220.220')
    ]
    
    hosts = []
    
    # Load hosts from various sources
    if args.file:
        hosts = load_hosts_from_file(args.file)
        if not hosts:
            print("No valid hosts found in file.")
            return
    elif args.hosts:
        # Parse command line hosts
        for host in args.hosts:
            if ':' in host:
                # Format: label:ip
                label, ip = host.split(':', 1)
                hosts.append((label.strip(), ip.strip()))
            else:
                # Just IP address
                hosts.append((f'Host-{host}', host))
    else:
        # Use default hosts
        hosts = default_hosts
        print("No hosts specified. Using default hosts...")
    
    # Add gateways to ping list if requested
    if args.include_gateways and adapters:
        for adapter in adapters:
            gateway_label = f"{adapter.name}-Gateway"
            # Check if this gateway is already in the list
            if not any(host[1] == adapter.gateway for host in hosts):
                hosts.append((gateway_label, adapter.gateway))
                print(f"Added gateway: {gateway_label} ({adapter.gateway})")
    
    print(f"Pinging {len(hosts)} hosts with timeout={args.timeout}s, count={args.count}")
    print("=" * 60)
    
    def run_ping_test():
        """Run a single round of ping tests"""
        results = []
        
        # Use threading for concurrent pings
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Submit all ping tasks
            future_to_host = {
                executor.submit(ping_host_wrapper, host, args.timeout, args.count): host 
                for host in hosts
            }
            
            # Collect results in order
            host_results = {}
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    host_results[host] = result
                except Exception as e:
                    label, ip = host
                    host_results[host] = PingResult(label, ip, 'down', error=str(e))
            
            # Add results in original order
            for host in hosts:
                results.append(host_results[host])
        
        return results
    
    try:
        if args.continuous:
            print("Running in continuous mode. Press Ctrl+C to stop.")
            print()
            
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n--- Ping Test at {timestamp} ---")
                
                results = run_ping_test()
                
                # Display results
                if args.quiet:
                    # Only show failed pings
                    failed_results = [r for r in results if r.status == 'down']
                    if failed_results:
                        for result in failed_results:
                            print(result)
                    else:
                        print("All hosts are UP")
                else:
                    # Show all results in table format
                    table_data = []
                    for result in results:
                        status_icon = "✅" if result.status == 'up' else "❌"
                        response_time = f"{result.response_time:.1f}ms" if result.response_time is not None else "N/A"
                        error_msg = result.error if result.error else ""
                        
                        table_data.append([
                            result.label,
                            result.ip,
                            f"{status_icon} {result.status.upper()}",
                            response_time,
                            error_msg
                        ])
                    
                    print(tabulate(table_data, headers=["Label", "IP Address", "Status", "Response Time", "Error"], tablefmt="grid"))
                
                # Show summary if requested (even in continuous mode)
                if args.summary:
                    total_hosts = len(results)
                    up_hosts = len([r for r in results if r.status == 'up'])
                    down_hosts = total_hosts - up_hosts
                    
                    # Calculate average response time for hosts that are up
                    up_results_with_time = [r for r in results if r.status == 'up' and r.response_time is not None]
                    avg_response_time = sum(r.response_time for r in up_results_with_time) / max(len(up_results_with_time), 1) if up_results_with_time else 0
                    
                    print(f"\n📊 Summary:")
                    print(f"  Total hosts: {total_hosts}")
                    print(f"  Up: {up_hosts} ({up_hosts/total_hosts*100:.1f}%)")
                    print(f"  Down: {down_hosts} ({down_hosts/total_hosts*100:.1f}%)")
                    if up_results_with_time:
                        print(f"  Average response time: {avg_response_time:.1f}ms")
                
                # Save results if requested
                if args.save:
                    save_results_to_file(results, args.save)
                
                # Wait for next interval
                time.sleep(args.interval)
        else:
            # Single run
            results = run_ping_test()
            
            # Display results
            if args.quiet:
                # Only show failed pings
                failed_results = [r for r in results if r.status == 'down']
                if failed_results:
                    print("Failed hosts:")
                    for result in failed_results:
                        print(f"  {result}")
                else:
                    print("✅ All hosts are UP!")
            else:
                # Show all results in table format
                table_data = []
                for result in results:
                    status_icon = "✅" if result.status == 'up' else "❌"
                    response_time = f"{result.response_time:.1f}ms" if result.response_time is not None else "N/A"
                    error_msg = result.error if result.error else ""
                    
                    table_data.append([
                        result.label,
                        result.ip,
                        f"{status_icon} {result.status.upper()}",
                        response_time,
                        error_msg
                    ])
                
                print(tabulate(table_data, headers=["Label", "IP Address", "Status", "Response Time", "Error"], tablefmt="grid"))
            
            # Show summary if requested
            if args.summary:
                total_hosts = len(results)
                up_hosts = len([r for r in results if r.status == 'up'])
                down_hosts = total_hosts - up_hosts
                
                # Calculate average response time for hosts that are up
                up_results_with_time = [r for r in results if r.status == 'up' and r.response_time is not None]
                avg_response_time = sum(r.response_time for r in up_results_with_time) / max(len(up_results_with_time), 1) if up_results_with_time else 0
                
                print(f"\n📊 Summary:")
                print(f"  Total hosts: {total_hosts}")
                print(f"  Up: {up_hosts} ({up_hosts/total_hosts*100:.1f}%)")
                print(f"  Down: {down_hosts} ({down_hosts/total_hosts*100:.1f}%)")
                if up_results_with_time:
                    print(f"  Average response time: {avg_response_time:.1f}ms")
            
            # Save results if requested
            if args.save:
                save_results_to_file(results, args.save)
                
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
