#!/bin/bash
#
# install.sh
#
# v1.2: This version is self-aware of its location and provides clearer instructions.

# --- Style and Color Definitions ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Helper functions ---
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Get the script's own directory ---
# This makes the script location-independent.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# --- Main Installation Logic ---
info "Starting Homelab Dashboard installation from: $SCRIPT_DIR"

# Step 1: Check for essential system commands
info "Step 1: Checking for essential tools (python3, pip)..."
if ! command -v python3 &> /dev/null || ! command -v pip &> /dev/null; then
    error "Python 3 and/or pip are not found. They are required to continue."
    warn "On Debian/Ubuntu, you can install them with: sudo apt install python3 python3-pip"
    exit 1
fi
info "Essential tools found."

# Step 2: Install Python dependencies from requirements.txt
info "Step 2: Installing Python packages from requirements.txt..."
python3 -m pip install -r "${SCRIPT_DIR}/requirements.txt"
if [ $? -ne 0 ]; then
    error "Failed to install Python packages. Please check the pip output above for errors."
    exit 1
fi
info "Python packages installed successfully."

# Step 3: Final Manual Steps
info "Step 3: Final manual setup required."
echo
warn "The application requires a MySQL database and table to be created."
warn "Please use the included 'dashboard_commands.sql' file to set up your database."
warn "Example: mysql -u your_user -p your_database < ${SCRIPT_DIR}/dashboard_commands.sql"
echo
info "Installation complete!"
info "You can now run the dashboard with: python3 ${SCRIPT_DIR}/dashboard.py"
echo
