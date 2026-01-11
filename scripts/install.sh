#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/yourusername/shannon"
INSTALL_DIR="${HOME}/.shannon"

echo "🧠 Installing Shannon..."

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"
fi

# Clone or update repository
if [ -d "${INSTALL_DIR}" ]; then
    echo "🔄 Updating existing installation..."
    cd "${INSTALL_DIR}"
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone "${REPO_URL}" "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# Create virtual environment and install
echo "🐍 Setting up Python environment..."
uv venv
uv pip install -e .

# Initialize database
echo "🗄️ Initializing database..."
uv run shannon init

# Add to PATH
SHELL_RC="${HOME}/.bashrc"
if [[ "${SHELL}" == *"zsh"* ]]; then
    SHELL_RC="${HOME}/.zshrc"
fi

if ! grep -q "shannon" "${SHELL_RC}" 2>/dev/null; then
    echo 'export PATH="${HOME}/.shannon/.venv/bin:${PATH}"' >> "${SHELL_RC}"
    echo "✅ Added shannon to PATH in ${SHELL_RC}"
fi

echo ""
echo "✨ Shannon installed successfully!"
echo "   Run 'source ${SHELL_RC}' or restart your terminal"
echo "   Then run 'shannon' to start the TUI"