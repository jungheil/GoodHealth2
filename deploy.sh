#! /bin/bash

function check_download() {
    if [ $1 -ne 0 ]; then
        echo "[ DEPLOY ] Download \"$2\" failed! Please check your network and try again."
        exit 3
    fi
}

function check_sudo() {
    sudo echo "[ DEPLOY ] Install for $1" || {
        echo "[ DEPLOY ] sudo not found"
        exit 1
    }
}

function Debian() {
    DEBIAN_FRONTEND=noninteractive
    sudo apt-get update &&
        sudo apt-get install -y firefox wget || {
        echo "[ DEPLOY ] apt-install failed"
        exit 2
    }
    #install Xvfb
    if [ $TERMINAL -eq 1 ]; then
        sudo apt-get install -y xvfb &&
            Xvfb :99 -ac &&
            export DISPLAY=:99 || {
            echo "[ DEPLOY ] apt-install failed"
            exit 2
        }
    fi
}

function ArchLinux() {
    sudo pacman -S --noconfirm --needed --quiet firefox wget || {
        echo "[ DEPLOY ] pacman install failed"
        exit 2
    }
    if [ $TERMINAL -eq 1 ]; then
        sudo pacman -S --noconfirm --needed --quiet xorg-server-xvfb &&
            Xvfb :99 -ac &&
            export DISPLAY=:99 || {
            echo "[ DEPLOY ] pacman install failed"
            exit 2
        }
    fi
}

TERMINAL=0
while [ -n "$1" ]; do
    case $1 in
    --terminal | -t)
        TERMINAL=1
        ;;
    *)
        echo -e "\033[31mcommand not found: $1\033[0m"
        exit 1
        ;;
    esac
    shift
done

if [ $(uname) == "Linux" ]; then
    if cat /etc/*release | grep ^ID_LIKE | grep debian 1>/dev/null 2>&1; then
        check_sudo "Debian"
        Debian
    elif cat /etc/*release | grep ^ID_LIKE | grep arch 1>/dev/null 2>&1; then
        check_sudo "ArchLinux"
        ArchLinux
    else
        echo "[ DEPLOY ] OS not support, exiting installation!"
        exit 3
    fi
else
    echo "[ DEPLOY ] Unknown OS $(uname), exiting installation!"
    exit 3
fi

pip install -r requirements.txt

wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz &&
    tar -zxvf geckodriver-v0.31.0-linux64.tar.gz &&
    rm geckodriver-v0.31.0-linux64.tar.gz || {
    echo "[ DEPLOY ] geckodriver download failed."
    exit 2
}

echo "[ DEPLOY ] install Finish!"
