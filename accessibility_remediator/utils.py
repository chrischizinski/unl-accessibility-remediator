"""
Utility functions for the accessibility remediator.
"""

import socket
import logging
from typing import Optional


def find_available_port(start_port: int = 8000, max_attempts: int = 20) -> Optional[int]:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: Port to start checking from
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number or None if none found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None


def is_port_available(port: int) -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False


def get_service_url(port: int) -> str:
    """Get the service URL for the given port."""
    return f"http://localhost:{port}"


def print_startup_banner(port: int, service_name: str = "UNL Accessibility Remediator"):
    """Print a helpful startup banner with connection info."""
    url = get_service_url(port)
    
    print("\n" + "="*60)
    print(f"🎯 {service_name}")
    print("="*60)
    print(f"✅ Server running on: {url}")
    print(f"🌐 Web Interface: {url}")
    print(f"📋 Health Check: {url}/health")
    print("="*60)
    print("📝 Usage:")
    print(f"   • Open {url} in your browser")
    print("   • Upload .pptx or .html slide decks")
    print("   • Get WCAG 2.1 Level AA compliance reports")
    print("="*60)
    print("⚠️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")