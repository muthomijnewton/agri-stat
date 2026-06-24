import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary =
      Color(0xFF2E7D32);

  static const Color secondary =
      Color(0xFF4CAF50);

  static const Color background =
      Color(0xFFF5F7FA);

  // ======================
  // LIGHT THEME
  // ======================

  static final ThemeData light =
      ThemeData(
    useMaterial3: true,

    brightness: Brightness.light,

    scaffoldBackgroundColor:
        background,

    primaryColor: primary,

    colorScheme:
        const ColorScheme.light(
      primary: primary,

      secondary: secondary,

      surface: Colors.white,
    ),

    appBarTheme:
        const AppBarTheme(
      elevation: 0,

      centerTitle: true,

      backgroundColor:
          primary,

      foregroundColor:
          Colors.white,
    ),

    cardTheme:
        CardThemeData(
      elevation: 4,

      margin:
          const EdgeInsets.all(
        8,
      ),

      shape:
          RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(
          16,
        ),
      ),
    ),

    navigationBarTheme:
        NavigationBarThemeData(
      backgroundColor:
          Colors.white,

      indicatorColor:
          primary.withValues(
        alpha: 0.15,
      ),

      labelTextStyle:
          WidgetStateProperty.all(
        const TextStyle(
          fontWeight:
              FontWeight.w600,
        ),
      ),
    ),

    elevatedButtonTheme:
        ElevatedButtonThemeData(
      style:
          ElevatedButton.styleFrom(
        backgroundColor:
            primary,

        foregroundColor:
            Colors.white,

        elevation: 2,

        shape:
            RoundedRectangleBorder(
          borderRadius:
              BorderRadius.circular(
            12,
          ),
        ),
      ),
    ),

    inputDecorationTheme:
        InputDecorationTheme(
      filled: true,

      fillColor: Colors.white,

      border:
          OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(
          12,
        ),
      ),

      enabledBorder:
          OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(
          12,
        ),

        borderSide:
            BorderSide(
          color:
              Colors.grey.shade300,
        ),
      ),

      focusedBorder:
          const OutlineInputBorder(
        borderSide:
            BorderSide(
          color: primary,

          width: 2,
        ),
      ),
    ),

    snackBarTheme:
        const SnackBarThemeData(
      behavior:
          SnackBarBehavior.floating,
    ),
  );

  // ======================
  // DARK THEME
  // ======================

  static final ThemeData dark =
      ThemeData(
    useMaterial3: true,

    brightness: Brightness.dark,

    scaffoldBackgroundColor:
        const Color(
      0xFF121212,
    ),

    primaryColor: primary,

    colorScheme:
        const ColorScheme.dark(
      primary: primary,

      secondary: secondary,

      surface: Color(
        0xFF1E1E1E,
      ),
    ),

    appBarTheme:
        const AppBarTheme(
      elevation: 0,

      centerTitle: true,

      backgroundColor:
          primary,

      foregroundColor:
          Colors.white,
    ),

    cardTheme:
        CardThemeData(
      elevation: 4,

      margin:
          const EdgeInsets.all(
        8,
      ),

      shape:
          RoundedRectangleBorder(
        borderRadius:
            BorderRadius.circular(
          16,
        ),
      ),
    ),

    navigationBarTheme:
        NavigationBarThemeData(
      backgroundColor:
          const Color(
        0xFF1E1E1E,
      ),

      indicatorColor:
          primary.withValues(
        alpha: 0.25,
      ),

      labelTextStyle:
          WidgetStateProperty.all(
        const TextStyle(
          fontWeight:
              FontWeight.w600,
        ),
      ),
    ),

    elevatedButtonTheme:
        ElevatedButtonThemeData(
      style:
          ElevatedButton.styleFrom(
        backgroundColor:
            primary,

        foregroundColor:
            Colors.white,

        shape:
            RoundedRectangleBorder(
          borderRadius:
              BorderRadius.circular(
            12,
          ),
        ),
      ),
    ),

    inputDecorationTheme:
        InputDecorationTheme(
      filled: true,

      fillColor:
          const Color(
        0xFF1E1E1E,
      ),

      border:
          OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(
          12,
        ),
      ),

      enabledBorder:
          OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(
          12,
        ),

        borderSide:
            BorderSide(
          color:
              Colors.grey.shade700,
        ),
      ),

      focusedBorder:
          const OutlineInputBorder(
        borderSide:
            BorderSide(
          color: primary,

          width: 2,
        ),
      ),
    ),

    snackBarTheme:
        const SnackBarThemeData(
      behavior:
          SnackBarBehavior.floating,
    ),
  );
}