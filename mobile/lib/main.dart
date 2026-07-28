import 'package:flutter/material.dart';

import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

import 'services/auth_service.dart';

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
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            );
          }

          final loggedIn = snapshot.data ?? false;

          return loggedIn ? const HomeScreen() : const LoginScreen();
        },
      ),
    );
  }
}
