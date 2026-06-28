#!/bin/bash
# build-flutter.sh — Build Flutter APK from source directory

set -e

SOURCE_DIR="${1:-./source}"
BUILD_TYPE="${2:-release}"
SPLIT_ABI="${3:-true}"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    exit 1
fi

cd "$SOURCE_DIR"

echo "📦 Getting Flutter dependencies..."
flutter pub get

echo "🚀 Building APK ($BUILD_TYPE)..."
if [ "$SPLIT_ABI" = "true" ]; then
    flutter build apk --$BUILD_TYPE --split-per-abi
else
    flutter build apk --$BUILD_TYPE
fi

echo "✅ Build complete!"
ls -la ./build/app/outputs/flutter-apk/
