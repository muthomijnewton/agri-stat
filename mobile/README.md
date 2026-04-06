# Flutter Mobile App - Agricultural Statistics Dashboard

A Flutter mobile application for the Agricultural Statistics Dashboard, enabling farmers and distributors to manage inventory and forecast demand on the go.

## Features

- **Dashboard** - Overview with key metrics
- **Products** - Browse and manage agricultural products
- **Transactions** - View transaction history
- **Forecasts** - See demand predictions
- **Recommendations** - Approve and implement inventory recommendations
- **Offline Support** - Works offline with local caching
- **Push Notifications** - Real-time alerts for recommendations

## Prerequisites

- Flutter 3.0+ (with Dart 3.0+)
- iOS 11.0+ or Android 5.0+ (API 21)
- Android Studio or Xcode for building

## Getting Started

### 1. Install Flutter
```bash
# macOS
brew install flutter

# Windows/Linux - Download from flutter.dev
```

### 2. Create/Setup Flutter Project
```bash
# If starting fresh
flutter create --org com.agricstat agric_stat_mobile

# Or use existing project
cd mobile
flutter pub get
```

### 3. Install Dependencies
```bash
flutter pub get
```

### 4. Run the App

#### iOS
```bash
flutter run -d iPhone
# Or specific device
flutter run -d "iPhone 14 Pro"
```

#### Android
```bash
flutter run -d emulator-5554
# Or Android phone
flutter run
```

#### Web (for testing)
```bash
flutter run -d chrome
```

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart              # App entry point
│   ├── screens/               # Full-page screens
│   │   ├── dashboard_screen.dart
│   │   ├── products_screen.dart
│   │   ├── transactions_screen.dart
│   │   ├── forecasts_screen.dart
│   │   └── recommendations_screen.dart
│   ├── widgets/               # Reusable widgets
│   │   ├── stat_card.dart
│   │   ├── product_card.dart
│   │   ├── transaction_list.dart
│   │   ├── forecast_chart.dart
│   │   └── recommendation_card.dart
│   ├── services/              # API & business logic
│   │   ├── api_service.dart   # HTTP client
│   │   ├── storage_service.dart # Local storage
│   │   └── notification_service.dart
│   └── models/                # Data models
│       ├── product_model.dart
│       ├── transaction_model.dart
│       ├── forecast_model.dart
│       └── recommendation_model.dart
├── test/                      # Unit tests
├── pubspec.yaml               # Dependencies
├── android/                   # Android project
└── ios/                       # iOS project
```

## Key Dependencies

- **dio** - HTTP client for API calls
- **provider** - State management
- **fl_chart** - Charts and graphs
- **sqflite** - Local SQLite database
- **shared_preferences** - Simple key-value storage
- **json_serializable** - JSON serialization
- **connectivity_plus** - Network status
- **logger** - Logging utility

## API Integration

The app connects to the FastAPI backend at `http://localhost:8000/api`.

All API calls are handled through `lib/services/api_service.dart`:
- **Products** - CRUD operations
- **Transactions** - View and record sales
- **Forecasts** - Get demand predictions
- **Recommendations** - Approval workflow

## Building for Production

### Android
```bash
# Build APK
flutter build apk

# Build App Bundle for Play Store
flutter build appbundle
```

### iOS
```bash
# Build for physical device
flutter build ios

# Build for App Store
flutter build ios --release
```

### Web
```bash
flutter build web
```

## Testing

```bash
# Run all tests
flutter test

# Run specific test
flutter test test/widgets/product_card_test.dart

# Run with coverage
flutter test --coverage
```

## Debugging

### Performance Profiling
```bash
flutter run --profile
```

### Debug Mode
```bash
flutter run -d emulator-5554 --debug
```

### Log Viewing
```bash
flutter logs
```

## Common Issues

### Connection Error to Backend
- Ensure backend is running on `http://localhost:8000`
- For emulator, use `http://10.0.2.2:8000` on Android
- For iOS simulator, use `http://localhost:8000`

### CocoaPods Issues (iOS)
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
flutter pub get
```

### Gradle Issues (Android)
```bash
flutter clean
flutter pub get
flutter pub get
flutter run
```

## State Management

The app uses Provider for state management. Key providers:

```dart
// Access API service
Provider.of<ApiService>(context, listen: false).getProducts()

// Access state
Consumer<ProductProvider>(
  builder: (context, productProvider, child) {
    return ListView(
      children: productProvider.products.map((p) => ProductCard(product: p)).toList(),
    );
  }
)
```

## Running Backend & Mobile Simultaneously

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2: Mobile (update API_URL for your device)
cd mobile
flutter run
```

## Contributing

1. Create a feature branch (`git checkout -b feature/new-feature`)
2. Commit changes (`git commit -am 'Add new feature'`)
3. Push to branch (`git push origin feature/new-feature`)
4. Create Pull Request

## License

University of Eastern Africa, Baraton - Senior Project
Student: Newton Jones Muthomi (SNEWJO2011)
