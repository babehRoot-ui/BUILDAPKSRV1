#!/usr/bin/env python3
# web2apk.py — Generate Android WebView APK project from URL

import os
import sys
import argparse
import subprocess
import shutil
import json
from pathlib import Path
from jinja2 import Template
from PIL import Image
import urllib.request
import base64
import hashlib

TEMPLATES = {
    'AndroidManifest.xml': '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{{ package_name }}">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{{ app_name }}"
        android:theme="@style/Theme.AppCompat.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>''',

    'MainActivity.java': '''package {{ package_name }};

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }
        });

        webView.setWebChromeClient(new WebChromeClient());
        webView.loadUrl("{{ web_url }}");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}''',

    'activity_main.xml': '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>''',

    'build.gradle': '''plugins {
    id 'com.android.application'
}

android {
    namespace '{{ package_name }}'
    compileSdk 34

    defaultConfig {
        applicationId '{{ package_name }}'
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName '1.0'
    }

    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
        }
    }
}

dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}''',

    'settings.gradle': '''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "{{ app_name }}"
include ':app' ''',

    'gradle-wrapper.properties': '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists''',
}


def generate_icon(icon_url, output_dir, size=192):
    """Download or create icon"""
    icon_path = Path(output_dir) / 'app' / 'src' / 'main' / 'res' / 'mipmap-hdpi' / 'ic_launcher.png'
    icon_path.parent.mkdir(parents=True, exist_ok=True)

    if icon_url:
        try:
            urllib.request.urlretrieve(icon_url, icon_path)
            # Resize if needed
            img = Image.open(icon_path)
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            img.save(icon_path)
            return
        except Exception as e:
            print(f"⚠️ Failed to download icon: {e}")

    # Create default icon
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (size, size), color='#3B82F6')
    draw = ImageDraw.Draw(img)
    draw.text((size//2, size//2), 'W', fill='white', anchor='mm')
    img.save(icon_path)


def generate_project(web_url, app_name, package_name, icon_url, splash_color, output_dir):
    """Generate full Android project structure"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    app_dir = output_path / 'app' / 'src' / 'main'
    java_dir = app_dir / 'java' / package_name.replace('.', '/')
    res_dir = app_dir / 'res'
    layout_dir = res_dir / 'layout'
    values_dir = res_dir / 'values'

    for d in [java_dir, layout_dir, values_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Generate files
    context = {
        'web_url': web_url,
        'app_name': app_name,
        'package_name': package_name,
        'splash_color': splash_color,
    }

    for filename, content in TEMPLATES.items():
        template = Template(content)
        rendered = template.render(**context)
        if filename == 'build.gradle':
            dest = output_path / 'app' / filename
        elif filename == 'settings.gradle':
            dest = output_path / filename
        elif filename == 'gradle-wrapper.properties':
            dest = output_path / 'gradle' / 'wrapper' / filename
        elif filename == 'AndroidManifest.xml':
            dest = app_dir / filename
        elif filename == 'MainActivity.java':
            dest = java_dir / filename
        elif filename == 'activity_main.xml':
            dest = layout_dir / filename
        else:
            dest = output_path / filename

        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, 'w') as f:
            f.write(rendered)
        print(f"✅ Generated: {dest}")

    # Generate icon
    generate_icon(icon_url, str(output_path))

    # Generate gradlew wrapper
    gradle_wrapper = output_path / 'gradlew'
    gradle_wrapper.write_text('''#!/bin/sh
exec java -cp "gradle/wrapper/gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain "$@"
''')
    gradle_wrapper.chmod(0o755)

    print(f"✅ Web2Apk project generated at: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate WebView APK project')
    parser.add_argument('--url', required=True, help='Website URL')
    parser.add_argument('--name', required=True, help='App name')
    parser.add_argument('--package', default='com.web2apk.app', help='Package name')
    parser.add_argument('--icon', help='Icon URL')
    parser.add_argument('--splash', default='#FFFFFF', help='Splash color')
    parser.add_argument('--output', default='./output', help='Output directory')

    args = parser.parse_args()
    generate_project(args.url, args.name, args.package, args.icon, args.splash, args.output)


if __name__ == '__main__':
    main()
