import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/auth_service.dart';

import '../main.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() =>
      _LoginScreenState();
}

class _LoginScreenState
    extends State<LoginScreen> {
  final ApiService _apiService =
      ApiService();

  final AuthService _authService =
      AuthService();

  final _formKey =
      GlobalKey<FormState>();

  final _usernameController =
      TextEditingController();

  final _passwordController =
      TextEditingController();

  bool _isLoading = false;

  bool _obscurePassword = true;

  // ==========================
  // LOGIN
  // ==========================

  Future<void> _handleLogin() async {
    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!
        .validate()) {
      return;
    }

    try {
      setState(() {
        _isLoading = true;
      });

      final response =
          await _apiService.login(
        _usernameController.text
            .trim(),

        _passwordController.text
            .trim(),
      );

      await _authService
          .saveUserSession(
        response['id']
            .toString(),

        response['username']
            .toString(),

        response['access_token'] ??
            '',
      );

      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Welcome ${response['username']}',
          ),

          backgroundColor:
              Colors.green,
        ),
      );

      Navigator.pushReplacement(
        context,

        MaterialPageRoute(
          builder: (_) =>
              const HomeScreen(),
        ),
      );
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Login failed.\n$e',
          ),

          backgroundColor:
              Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(
    BuildContext context,
  ) {
    final isDark =
        Theme.of(context)
                .brightness ==
            Brightness.dark;

    return Scaffold(
      backgroundColor: isDark
          ? Colors.black
          : Colors.grey[100],

      body: SafeArea(
        child: Center(
          child:
              SingleChildScrollView(
            padding:
                const EdgeInsets.all(
              24,
            ),

            child: ConstrainedBox(
              constraints:
                  const BoxConstraints(
                maxWidth: 450,
              ),

              child: Card(
                elevation: 8,

                shape:
                    RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(
                    20,
                  ),
                ),

                child: Padding(
                  padding:
                      const EdgeInsets.all(
                    30,
                  ),

                  child: Form(
                    key: _formKey,

                    child: Column(
                      mainAxisSize:
                          MainAxisSize.min,

                      children: [
                        const Icon(
                          Icons.agriculture,

                          size: 80,

                          color: Color(
                            0xFF2E7D32,
                          ),
                        ),

                        const SizedBox(
                          height: 16,
                        ),

                        const Text(
                          'AgriStat Dashboard',

                          style:
                              TextStyle(
                            fontSize: 28,

                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        const SizedBox(
                          height: 6,
                        ),

                        Text(
                          'Agricultural Analytics Platform',

                          style:
                              TextStyle(
                            color:
                                Colors.grey[
                                    600],
                          ),
                        ),

                        const SizedBox(
                          height: 30,
                        ),

                        // USERNAME

                        TextFormField(
                          controller:
                              _usernameController,

                          decoration:
                              const InputDecoration(
                            labelText:
                                'Username',

                            prefixIcon:
                                Icon(
                              Icons.person,
                            ),

                            border:
                                OutlineInputBorder(),
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .trim()
                                    .isEmpty) {
                              return 'Username required';
                            }

                            return null;
                          },
                        ),

                        const SizedBox(
                          height: 18,
                        ),

                        // PASSWORD

                        TextFormField(
                          controller:
                              _passwordController,

                          obscureText:
                              _obscurePassword,

                          decoration:
                              InputDecoration(
                            labelText:
                                'Password',

                            prefixIcon:
                                const Icon(
                              Icons.lock,
                            ),

                            suffixIcon:
                                IconButton(
                              onPressed:
                                  () {
                                setState(
                                  () {
                                    _obscurePassword =
                                        !_obscurePassword;
                                  },
                                );
                              },

                              icon:
                                  Icon(
                                _obscurePassword
                                    ? Icons.visibility

                                    : Icons.visibility_off,
                              ),
                            ),

                            border:
                                const OutlineInputBorder(),
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .isEmpty) {
                              return 'Password required';
                            }

                            if (value
                                    .length <
                                4) {
                              return 'Password too short';
                            }

                            return null;
                          },

                          onFieldSubmitted:
                              (_) {
                            _handleLogin();
                          },
                        ),

                        const SizedBox(
                          height: 30,
                        ),

                        SizedBox(
                          width:
                              double.infinity,

                          height: 52,

                          child:
                              ElevatedButton(
                            onPressed:
                                _isLoading

                                    ? null

                                    : _handleLogin,

                            style:
                                ElevatedButton.styleFrom(
                              backgroundColor:
                                  const Color(
                                0xFF2E7D32,
                              ),

                              shape:
                                  RoundedRectangleBorder(
                                borderRadius:
                                    BorderRadius.circular(
                                  12,
                                ),
                              ),
                            ),

                            child:
                                _isLoading

                                    ? const SizedBox(
                                        height:
                                            25,

                                        width:
                                            25,

                                        child:
                                            CircularProgressIndicator(
                                          color:
                                              Colors.white,
                                        ),
                                      )

                                    : const Text(
                                        'LOGIN',

                                        style:
                                            TextStyle(
                                          fontSize:
                                              16,

                                          color:
                                              Colors.white,

                                          fontWeight:
                                              FontWeight.bold,
                                        ),
                                      ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();

    _passwordController.dispose();

    super.dispose();
  }
}