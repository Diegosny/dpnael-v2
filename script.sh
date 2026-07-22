#!/usr/bin/env bash
set -e

REPO="Diegosny/dpnael-v2"
INSTALL_DIR="/usr/local/bin"
BINARY_NAME="dpnael"

echo "🔍 Detectando o sistema operacional e arquitetura..."

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)
        if grep -q Microsoft /proc/version 2>/dev/null; then
            echo "🐧 Ambiente detectado: WSL (Windows Subsystem for Linux)"
        else
            echo "🐧 Ambiente detectado: Linux"
        fi
        BIN_SUFFIX="linux"
        ;;
    Darwin*)
        echo "🍎 Ambiente detectado: macOS"
        BIN_SUFFIX="macos"
        ;;
    *)
        echo "❌ Sistema operacional não suportado: $OS"
        exit 1
        ;;
esac

ASSET_NAME="dpnael-${BIN_SUFFIX}-${ARCH}"

echo "📥 Buscando a versão mais recente no GitHub..."
DOWNLOAD_URL=$(curl -s https://api.github.com/repos/$REPO/releases/latest | grep "browser_download_url" | grep "$ASSET_NAME" | cut -d '"' -f 4)

if [ -z "$DOWNLOAD_URL" ]; then
    DOWNLOAD_URL=$(curl -s https://api.github.com/repos/$REPO/releases/latest | grep "browser_download_url" | grep -v "tar.gz" | grep -v "zip" | head -n 1 | cut -d '"' -f 4)
fi

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Erro: Não foi possível encontrar um binário compatível para o seu sistema nas Releases do GitHub."
    exit 1
fi

echo "⬇️ Baixando DPNAEL..."
sudo mkdir -p "$INSTALL_DIR"
sudo curl -L -o "$INSTALL_DIR/$BINARY_NAME" "$DOWNLOAD_URL"

echo "⚙️ Configurando permissões de execução..."
sudo chmod +x "$INSTALL_DIR/$BINARY_NAME"

echo "✔ DPNAEL instalado com sucesso!"
echo "✨ Digite 'dpnael' em qualquer terminal para iniciar."