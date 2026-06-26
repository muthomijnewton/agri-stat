import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/products_screen.dart';
import 'screens/transactions_screen.dart';
import 'screens/forecasts_screen.dart';
import 'screens/recommendations_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/profile_screen.dart';

import 'services/auth_service.dart';
import 'services/api_service.dart';

import 'theme/app_theme.dart';

void main() {
  runApp(const AgriculturalStatApp());
}

class AgriculturalStatApp extends StatelessWidget {
  const AgriculturalStatApp({super.key});

  @override
  Widget build(BuildContext context) {
    final authService = AuthService();

    return MaterialApp(
      title: 'AgriStat Dashboard',

      debugShowCheckedModeBanner: false,

      theme: AppTheme.light,

      darkTheme: AppTheme.dark,

      themeMode: ThemeMode.system,

      home: FutureBuilder<bool>(
        future: authService.isLoggedIn(),

        builder: (context, snapshot) {
          if (snapshot.connectionState ==
              ConnectionState.waiting) {
            return const Scaffold(
              body: Center(
                child:
                    CircularProgressIndicator(),
              ),
            );
          }

          final loggedIn =
              snapshot.data ?? false;

          return loggedIn
              ? const HomeScreen()
              : const LoginScreen();
        },
      ),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState
    extends State<HomeScreen> {
  final ApiService _apiService =
      ApiService();

  int _selectedIndex = 0;

  int _unreadCount = 0;

  final List<String> _titles =
    const [
  'Dashboard',
  'Products',
  'Transactions',
  'Forecasts',
  'Insights',
  'Notifications',
];

  late final List<Widget> _screens;

  @override
  void initState() {
    super.initState();

    _screens = const [
  DashboardScreen(),
  ProductsScreen(),
  TransactionsScreen(),
  ForecastsScreen(),
  RecommendationsScreen(),
  NotificationsScreen(),
];

    _loadNotifications();
  }

  // ======================
  // NOTIFICATIONS
  // ======================

  Future<void>
      _loadNotifications() async {
    try {
      final count =
          await _apiService
              .getUnreadNotificationCount();

      if (!mounted) return;

      setState(() {
        _unreadCount = count;
      });
    } catch (_) {}
  }

  // ======================
  // REFRESH
  // ======================

  Future<void> _refresh() async {
    await _loadNotifications();

    if (!mounted) return;

    setState(() {});
  }

  // ======================
  // OPEN NOTIFICATIONS
  // ======================

  Future<void>
      _openNotifications() async {
    setState(() {
      _selectedIndex = 5;
    });

    await _loadNotifications();
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    final isDark =
        Theme.of(context)
                .brightness ==
            Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          '🌾 ${_titles[_selectedIndex]}',
        ),

        actions: [
  IconButton(
    icon: const Icon(
      Icons.refresh,
    ),
    onPressed: _refresh,
  ),

  Stack(
    children: [
      IconButton(
        icon: const Icon(
          Icons.notifications_none,
        ),
        onPressed: _openNotifications,
      ),

      if (_unreadCount > 0)
        Positioned(
          right: 6,
          top: 6,
          child: Container(
            padding: const EdgeInsets.all(5),
            decoration: const BoxDecoration(
              color: Colors.red,
              shape: BoxShape.circle,
            ),
            child: Text(
              _unreadCount > 9
                  ? '9+'
                  : '$_unreadCount',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
    ],
  ),

  IconButton(
    icon: const Icon(
      Icons.person_outline,
    ),
    onPressed: () {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) =>
              const ProfileScreen(),
        ),
      );
    },
  ),
],
      ),
    );
  }
}