#!/bin/bash
#
# install.sh
#
# v1.1: This version is now self-aware and can be run from any directory.

# --- Style and Color Definitions ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper function for printing messages ---
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- THE CRITICAL FIX ---
# Find the absolute path to the directory where this script is located.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
info "Script located at: $SCRIPT_DIR"

# --- Main Installation Logic ---
info "Starting Homelab Dashboard installation..."

# Step 1: Check for essential system commands
info "Step 1: Checking for essential system commands..."
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not found. Please install Python 3 to continue."
    exit 1
fi

if ! command -v pip &> /dev/null; then
    if command -v apt &> /dev/null; then
        warn "pip is not found. Attempting to install 'python3-pip'..."
        sudo apt update
        sudo apt install -y python3-pip
        if ! command -v pip &> /dev/null; then
             error "Failed to install pip. Please install it manually."
             exit 1
        fi
    else
        error "pip is not found and 'apt' is not available. Please install pip manually."
        exit 1
    fi
fi
info "All essential commands found."

# Step 2: Install Python dependencies from requirements.txt
info "Step 2: Installing Python packages..."
# Now we use the full, absolute path to the requirements.txt file.
python3 -m pip install -r "${SCRIPT_DIR}/requirements.txt"
if [ $? -ne 0 ]; then
    error "Failed to install Python packages. Please check the output above for errors."
    exit 1
fi
info "Python packages installed successfully."

# Step 3: Final Manual Steps
info "Step 3: Final manual setup required."
echo
warn "The application requires a MySQL database and table to be created."
warn "If you have not done so already, please use a MySQL client to run the"
warn "commands in the 'dashboard_commands.sql' file included with this project."
echo
info "Installation complete!"
info "You can now run the dashboard with: python3 ${SCRIPT_DIR}/dashboard.py"
echo
