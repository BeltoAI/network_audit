import nmap
import subprocess
import re
import threading
import time
import sys
import platform
import requests
import statistics

class NetworkScanner:
    def __init__(self):
        """Initializes scanner settings."""
        self.loading_done = False
        self.progress = 0
        self.total_hosts = 0
        self.loading_frames = ["(＞﹏＜)", "(◕‿◕✿)", "(¬‿¬)", "(≧◡≦)", "(✿◕‿◕)", "(≖‿≖)", "(⌐■_■)", "(˵ ͡° ͜ʖ ͡°˵)"]

    def anime_loading(self):
        """Anime-style loading animation with live progress updates."""
        while not self.loading_done:
            for frame in self.loading_frames:
                sys.stdout.write(f"\rScanning and Pinging... {frame} | {self.progress}/{self.total_hosts} completed ")
                sys.stdout.flush()
                time.sleep(0.3)
                if self.loading_done:
                    break
        sys.stdout.write("\rDone! (⌐■_■)       \n")  # Clear the animation

    def get_gateway_ip(self):
        """
        Automatically detects the default gateway IP for the current system.
        Works on Windows, Linux, and macOS.
        """
        try:
            # Check if internet connection is active
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code != 200:
                raise Exception("No network connection detected")

            system_platform = platform.system()

            # Windows: Use "route print" to extract gateway
            if system_platform == "Windows":
                result = subprocess.run("route print 0.0.0.0", shell=True, capture_output=True, text=True)
                match = re.search(r"0.0.0.0\s+0.0.0.0\s+([\d.]+)", result.stdout)

            # Linux & macOS: Use "ip route" or "netstat -nr"
            elif system_platform in ["Linux", "Darwin"]:
                result = subprocess.run("ip route show default", shell=True, capture_output=True, text=True)
                match = re.search(r"default via ([\d.]+)", result.stdout)

                # macOS Fallback if needed
                if not match and system_platform == "Darwin":
                    result = subprocess.run("netstat -nr | grep default", shell=True, capture_output=True, text=True)
                    match = re.search(r"default\s+([\d.]+)", result.stdout)

            else:
                raise Exception(f"Unsupported platform: {system_platform}")

            if match:
                return match.group(1)
            else:
                raise Exception("Could not detect default gateway")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    def get_live_hosts(self, network_range):
        """Scan the local network to find live hosts using nmap."""
        nm = nmap.PortScanner()
        nm.scan(hosts=network_range, arguments='-sn')  # Ping scan
        return [host for host in nm.all_hosts() if nm[host].state() == "up"]

    def ping_sweep(self, ip, count=10):
        """Perform a ping sweep and extract min, avg, max, range, median, std dev, and variance."""
        try:
            ping_command = ["ping", "-c", str(count), ip]
            result = subprocess.run(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Extract all ping times from the output
            ping_times = [float(match) for match in re.findall(r"time=([\d.]+)", result.stdout)]
            
            if len(ping_times) > 0:
                min_ping = min(ping_times)
                avg_ping = sum(ping_times) / len(ping_times)
                max_ping = max(ping_times)
                range_ping = max_ping - min_ping
                median_ping = statistics.median(ping_times)
                std_dev_ping = statistics.stdev(ping_times) if len(ping_times) > 1 else 0
                variance_ping = statistics.variance(ping_times) if len(ping_times) > 1 else 0

                return {
                    "IP": ip,
                    "Min Ping": min_ping,
                    "Avg Ping": avg_ping,
                    "Max Ping": max_ping,
                    "Range": range_ping,
                    "Median Ping": median_ping,
                    "Std Dev Ping": std_dev_ping,
                    "Variance Ping": variance_ping
                }
        except Exception:
            pass
        return None

    def format_results_html(self, results):
        """Formats scan results as an HTML table."""
        html_body = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                table { width: 100%%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
            </style>
        </head>
        <body>
            <h2>📡 Network Scan Results</h2>
            <table>
                <tr>
                    <th>IP Address</th>
                    <th>Min Ping (ms)</th>
                    <th>Avg Ping (ms)</th>
                    <th>Max Ping (ms)</th>
                    <th>Range (ms)</th>
                    <th>Median Ping (ms)</th>
                    <th>Std Dev Ping (ms)</th>
                    <th>Variance Ping (ms)</th>
                </tr>
        """

        for res in results:
            html_body += f"""
                <tr>
                    <td>{res['IP']}</td>
                    <td>{res['Min Ping']}</td>
                    <td>{res['Avg Ping']}</td>
                    <td>{res['Max Ping']}</td>
                    <td>{res['Range']}</td>
                    <td>{res['Median Ping']}</td>
                    <td>{res['Std Dev Ping']}</td>
                    <td>{res['Variance Ping']}</td>
                </tr>
            """

        html_body += """
            </table>
        </body>
        </html>
        """

        return html_body

    def run_scan(self):
        """Runs the network scan and returns the results."""
        print("🔍 Detecting default gateway...")
        gateway_ip = self.get_gateway_ip()
        print(f"🌍 Default Gateway: {gateway_ip}")

        # Convert gateway IP into a subnet (e.g., 192.168.1.1 → 192.168.1.0/24)
        subnet = ".".join(gateway_ip.split(".")[:3]) + ".0/24"
        print(f"📡 Scanning subnet: {subnet}")

        # Start loading animation in a separate thread
        loading_thread = threading.Thread(target=self.anime_loading)
        loading_thread.start()

        # Scan network
        live_hosts = self.get_live_hosts(subnet)
        self.total_hosts = len(live_hosts)

        # Ping sweep all devices
        results = []
        for ip in live_hosts:
            result = self.ping_sweep(ip)
            if result:
                results.append(result)
            self.progress += 1  # Update progress dynamically

        # Stop animation
        self.loading_done = True
        loading_thread.join()

        return results
