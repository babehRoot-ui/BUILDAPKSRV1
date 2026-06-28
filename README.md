# 🚀 Android Build Server — GitHub Actions

Build server otomatis untuk Flutter, Android Native, dan Web2Apk.

## 📋 Fitur
- Build Flutter APK dari source ZIP
- Build Android Studio project dari source ZIP  
- Generate WebView APK dari URL website
- Output artifact siap download

## 🔧 Workflow

### Flutter Build
Trigger via API:
```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/workflows/build-flutter.yml/dispatches \
  -d '{"ref":"main","inputs":{"zip_url":"...","tag":"v1.0.0"}}'
