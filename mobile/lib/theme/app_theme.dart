import 'package:flutter/material.dart';

class AppTheme {
  static const primary = Color(0xFF2E7D32);

  static final ThemeData light = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primary,
    colorScheme: const ColorScheme.light(
      primary: primary,
      secondary: Colors.green,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      centerTitle: true,
    ),
    cardTheme: const CardThemeData(
      elevation: 3,
      margin: EdgeInsets.all(8),
    ),
  );

  static final ThemeData dark = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primary,
    colorScheme: const ColorScheme.dark(
      primary: primary,
      secondary: Colors.green,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: primary,
      foregroundColor: Colors.white,
      centerTitle: true,
    ),
    cardTheme: const CardThemeData(
      elevation: 3,
      margin: EdgeInsets.all(8),
    ),
  );
}