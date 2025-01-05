# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rich",
# ]
# ///
import os
import platform
import socket
import sys
import time
from functools import lru_cache

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()

def format_bytes(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"

@lru_cache(maxsize=1)
def get_network_info():
    """Get network information with error handling and caching."""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        fqdn = socket.getfqdn()
        return {
            'hostname': hostname,
            'ip_address': ip_address,
            'fqdn': fqdn if fqdn != hostname else None
        }
    except socket.error:
        return {
            'hostname': None,
            'ip_address': None,
            'fqdn': None
        }

def get_filesystem_info():
    """Get filesystem information with proper error handling."""
    if os.name == "posix":
        try:
            statvfs = os.statvfs(".")
            total = statvfs.f_frsize * statvfs.f_blocks
            available = statvfs.f_frsize * statvfs.f_bavail
            used = total - available
            return {
                'total': format_bytes(total),
                'available': format_bytes(available),
                'used': format_bytes(used),
                'type': statvfs.f_flag
            }
        except (FileNotFoundError, OSError):
            return None
    elif os.name == "nt":
        try:
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            total_free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(os.getcwd()),
                ctypes.byref(free_bytes),
                ctypes.byref(total_bytes),
                ctypes.byref(total_free_bytes)
            )
            return {
                'total': format_bytes(total_bytes.value),
                'available': format_bytes(free_bytes.value),
                'used': format_bytes(total_bytes.value - free_bytes.value)
            }
        except (AttributeError, OSError):
            return None
    return None

def main():
    """Prints a comprehensive overview of the system information."""
    
    console.print(Panel.fit("System Information", style="bold blue"))

    # Operating System Details
    os_tree = Tree("🖥️ Operating System")
    os_tree.add(f"Name: {platform.system()}")
    os_tree.add(f"Release: {platform.release()}")
    os_tree.add(f"Version: {platform.version()}")
    os_tree.add(f"Platform: {platform.platform()}")
    os_tree.add(f"Architecture: {platform.architecture()}")
    os_tree.add(f"Machine: {platform.machine()}")
    os_tree.add(f"Processor: {platform.processor()}")
    if os.name == "nt":  # Windows-specific
        os_tree.add(f"Windows Edition: {platform.win32_edition()}")
    console.print(os_tree)

    # Python Environment Details
    python_table = Table(title="🐍 Python Environment", box=box.ROUNDED)
    python_table.add_column("Property", style="cyan")
    python_table.add_column("Value", style="green")
    
    python_info = [
        ("Version", platform.python_version()),
        ("Compiler", platform.python_compiler()),
        ("Implementation", platform.python_implementation()),
        ("Executable", sys.executable),
        ("API Version", sys.api_version)
    ]
    
    for prop, value in python_info:
        python_table.add_row(prop, str(value))
    
    console.print(python_table)

    # Network Information
    net_info = get_network_info()
    network_panel = Panel(
        f"""[cyan]Hostname:[/cyan] {net_info['hostname'] or '[red]Could not be determined[/red]'}
[cyan]IP Address:[/cyan] {net_info['ip_address'] or '[red]Could not be determined[/red]'}
[cyan]FQDN:[/cyan] {net_info['fqdn'] or '[red]Could not be determined[/red]'}""",
        title="🌐 Network Information",
        border_style="blue"
    )
    console.print(network_panel)

    # Filesystem Information
    fs_info = get_filesystem_info()
    if fs_info:
        fs_table = Table(title="💾 Filesystem Information", box=box.ROUNDED)
        fs_table.add_column("Metric", style="cyan")
        fs_table.add_column("Value", style="green")
        
        fs_table.add_row("Total Size", fs_info['total'])
        fs_table.add_row("Available Space", fs_info['available'])
        fs_table.add_row("Used Space", fs_info['used'])
        if 'type' in fs_info:
            fs_table.add_row("Filesystem Type", str(fs_info['type']))
        
        console.print(fs_table)
    else:
        console.print("[red]Could not get filesystem information[/red]")

    # Time Information
    time_panel = Panel(
        f"""[cyan]Current Time (UTC):[/cyan] {time.asctime(time.gmtime())}
[cyan]Current Time (Local):[/cyan] {time.asctime(time.localtime())}
[cyan]Current Timezone:[/cyan] {time.tzname}""",
        title="⏰ Time Information",
        border_style="blue"
    )
    console.print(time_panel)


if __name__ == "__main__":
    if os.name == "nt":  # Windows, needs ctypes for disk space
        import ctypes
    main()
