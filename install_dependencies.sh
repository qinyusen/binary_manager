#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "Binary Manager - Dependency Installer"
echo "========================================"

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}Error: This script requires root privileges${NC}"
        echo "Please use: sudo ./install_dependencies.sh"
        exit 1
    fi
}

# Check Python3
check_python3() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python3 is not installed${NC}"
        echo "Please install Python3 first"
        exit 1
    fi
    echo -e "${GREEN}✓ Python3 is installed: $(python3 --version)${NC}"
}

# Check and install pip3
check_pip3() {
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}pip3 is not installed, installing...${NC}"
        apt-get update && apt-get install -y python3-pip
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ pip3 installed successfully${NC}"
        else
            echo -e "${RED}Error: Failed to install pip3${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✓ pip3 is installed${NC}"
    fi
}

# Install Python packages
install_packages() {
    echo -e "${YELLOW}Installing Binary Manager packages...${NC}"
    
    local packages=("urllib3" "requests")
    
    for package in "${packages[@]}"; do
        echo "Installing $package..."
        pip3 install "$package" --upgrade
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to install $package${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ Packages installed successfully${NC}"
}

# Verify installation
verify_installation() {
    echo -e "${YELLOW}Verifying installation...${NC}"
    
    python3 -c "import urllib3; print('✓ urllib3 version:', urllib3.__version__)" 2>/dev/null || echo -e "${RED}✗ urllib3 verification failed${NC}"
    python3 -c "import requests; print('✓ requests version:', requests.__version__)" 2>/dev/null || echo -e "${RED}✗ requests verification failed${NC}"
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Dependencies installed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Display usage
show_usage() {
    echo "Usage: sudo ./install_dependencies.sh"
    echo ""
    echo "This script will install all required dependencies for Binary Manager"
    echo ""
    echo "Dependencies:"
    echo "  - urllib3 (HTTP client)"
    echo "  - requests (HTTP library)"
    exit 1
}

# Main function
main() {
    # Parse arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_usage
    fi
    
    echo "Starting dependency installation..."
    check_root
    check_python3
    check_pip3
    install_packages
    verify_installation
    
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  - Test: python3 test_v2_complete.py"
    echo "  - Publish: python3 -m binary_manager_v2.cli.main publish --source ./my_project --package-name my_app --version 1.0.0"
    echo "  - Quick start: See V2_QUICKSTART.md"
}

main "$@"
