#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
install_python_packages() {
    echo -e "${YELLOW}Installing Python packages...${NC}"
    
    local packages=("requests" "jsonschema" "tqdm")
    
    for package in "${packages[@]}"; do
        echo "Installing $package..."
        pip3 install "$package" --upgrade
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to install $package${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ All Python packages installed successfully${NC}"
}

# Verify installation
verify_installation() {
    echo -e "${YELLOW}Verifying installation...${NC}"
    
    local python_check_failed=0
    
    python3 -c "import requests; print('✓ requests version:', requests.__version__)" 2>/dev/null || python_check_failed=1
    python3 -c "import jsonschema; print('✓ jsonschema version:', jsonschema.__version__)" 2>/dev/null || python_check_failed=1
    python3 -c "import tqdm; print('✓ tqdm version:', tqdm.__version__)" 2>/dev/null || python_check_failed=1
    
    if [ $python_check_failed -eq 1 ]; then
        echo -e "${RED}Error: Package verification failed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}All dependencies installed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Main function
main() {
    echo "Starting dependency installation..."
    check_root
    check_python3
    check_pip3
    install_python_packages
    verify_installation
}

main
