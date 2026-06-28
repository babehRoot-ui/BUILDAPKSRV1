#!/bin/bash
# build-android.sh — Build Android Studio project

set -e

PROJECT_DIR="${1:-./project}"
VARIANT="${2:-release}"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

if [ ! -f "gradlew" ]; then
    echo "❌ gradlew not found!"
    exit 1
fi

chmod +x gradlew

echo "🚀 Building Android APK ($VARIANT)..."
./gradlew assemble${VARIANT^}

echo "✅ Build complete!"
find ./app/build/outputs/apk -name "*.apk" -type f
