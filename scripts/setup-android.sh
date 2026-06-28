#!/bin/bash
# setup-android.sh — Install Android SDK dependencies

set -e

echo "🔧 Setting up Android SDK..."

# Install base packages
sudo apt update
sudo apt install -y \
    openjdk-17-jdk \
    android-sdk \
    android-sdk-platform-tools \
    android-sdk-build-tools \
    unzip \
    wget \
    curl

# Set environment
export ANDROID_HOME=/usr/lib/android-sdk
export PATH=$PATH:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools

# Accept licenses (auto)
yes | sdkmanager --licenses > /dev/null 2>&1 || true

# Install specific components
sdkmanager "build-tools;34.0.0" \
           "platforms;android-34" \
           "platforms;android-33" \
           "ndk;26.1.10909125" \
           "cmake;3.22.1" > /dev/null 2>&1 || true

echo "✅ Android SDK setup complete"
echo "ANDROID_HOME=$ANDROID_HOME"
