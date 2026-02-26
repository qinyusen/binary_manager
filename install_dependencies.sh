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

# Install Python packages for V1
install_v1_packages() {
    echo -e "${YELLOW}Installing V1 packages...${NC}"
    
    local packages=("requests" "jsonschema" "tqdm")
    
    for package in "${packages[@]}"; do
        echo "Installing $package..."
        pip3 install "$package" --upgrade
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to install $package${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ V1 packages installed successfully${NC}"
}

# Install Python packages for V2
install_v2_packages() {
    echo -e "${YELLOW}Installing V2 packages...${NC}"
    
    local packages=("urllib3" "requests")
    
    for package in "${packages[@]}"; do
        echo "Installing $package..."
        pip3 install "$package" --upgrade
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to install $package${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ V2 packages installed successfully${NC}"
}

# Verify installation
verify_installation() {
    echo -e "${YELLOW}Verifying installation...${NC}"
    
    if [ "$INSTALL_VERSION" = "v1" ]; then
        python3 -c "import requests; print('✓ requests version:', requests.__version__)" 2>/dev/null || echo -e "${RED}✗ requests verification failed${NC}"
        python3 -c "import jsonschema; print('✓ jsonschema version:', jsonschema.__version__)" 2>/dev/null || echo -e "${RED}✗ jsonschema verification failed${NC}"
        python3 -c "import tqdm; print('✓ tqdm version:', tqdm.__version__)" 2>/dev/null || echo -e "${RED}✗ tqdm verification failed${NC}"
    else
        python3 -c "import urllib3; print('✓ urllib3 version:', urllib3.__version__)" 2>/dev/null || echo -e "${RED}✗ urllib3 verification failed${NC}"
        python3 -c "import requests; print('✓ requests version:', requests.__version__)" 2>/dev/null || echo -e "${RED}✗ requests verification failed${NC}"
    fi
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Dependencies installed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# Display usage
show_usage() {
    echo "Usage: sudo ./install_dependencies.sh [v1|v2]"
    echo ""
    echo "Arguments:"
    echo "  v1    Install dependencies for Binary Manager V1 (default)"
    echo "  v2    Install dependencies for Binary Manager V2 (recommended)"
    echo ""
    echo "Examples:"
    echo "  sudo ./install_dependencies.sh v1"
    echo "  sudo ./install_dependencies.sh v2"
    exit 1
}

# Main function
main() {
    # Parse arguments
    INSTALL_VERSION="v1"
    
    if [ $# -gt 0 ]; then
        case "$1" in
            v1|V1)
                INSTALL_VERSION="v1"
                ;;
            v2|V2)
                INSTALL_VERSION="v2"
                ;;
            *)
                show_usage
                ;;
        esac
    fi
    
    echo "Starting dependency installation for ${INSTALL_VERSION}..."
    check_root
    check_python3
    check_pip3
    
    if [ "$INSTALL_VERSION" = "v1" ]; then
        install_v1_packages
    else
        install_v2_packages
    fi
    
    verify_installation
    
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    if [ "$INSTALL_VERSION" = "v1" ]; then
        echo "  - Test V1: python3 test.py"
        echo "  - Publish: python3 binary_manager/publisher/main.py --source ./examples/my_app --name my_app --version 1.0.0"
    else
        echo "  - Test V2: python3 test_v2_complete.py"
        echo "  - Publish: python3 -m binary_manager_v2.cli.main publish --source ./examples/simple_app --package-name simple_calculator --version 1.0.0"
    fi
}

main "$@"
