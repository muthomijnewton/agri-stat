import 'package:flutter/material.dart';

import '../services/auth_service.dart';
import '../screens/login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() =>
      _ProfileScreenState();
}

class _ProfileScreenState
    extends State<ProfileScreen> {
  final AuthService _authService =
      AuthService();

  String username = "";
  String userId = "";

  bool loading = true;

  @override
  void initState() {
    super.initState();
    loadUser();
  }

  Future<void> loadUser() async {
    username =
        await _authService.getUsername() ??
            "Unknown User";

    userId =
        await _authService.getUserId() ??
            "N/A";

    setState(() {
      loading = false;
    });
  }

  Future<void> logout() async {
    await _authService.logout();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) =>
            const LoginScreen(),
      ),
      (route) => false,
    );
  }

  Widget statCard(
    String title,
    String value,
    IconData icon,
    Color color,
  ) {
    return Expanded(
      child: Container(
        margin:
            const EdgeInsets.symmetric(
          horizontal: 4,
        ),
        padding:
            const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color.withValues(
            alpha: 0.12,
          ),
          borderRadius:
              BorderRadius.circular(16),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: color,
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style:
                  const TextStyle(
                fontWeight:
                    FontWeight.bold,
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              textAlign:
                  TextAlign.center,
              style:
                  const TextStyle(
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget profileTile(
    IconData icon,
    String title,
    String subtitle,
  ) {
    return Card(
      elevation: 0,
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }

  @override
  Widget build(
    BuildContext context,
  ) {
    if (loading) {
      return const Center(
        child:
            CircularProgressIndicator(),
      );
    }

    return SingleChildScrollView(
      padding:
          const EdgeInsets.all(20),
      child: Column(
        children: [
          // ===================
          // PROFILE HEADER
          // ===================

          Container(
            width: double.infinity,
            padding:
                const EdgeInsets.all(
              24,
            ),
            decoration: BoxDecoration(
              gradient:
                  const LinearGradient(
                colors: [
                  Color(0xFF2E7D32),
                  Color(0xFF66BB6A),
                ],
              ),
              borderRadius:
                  BorderRadius.circular(
                24,
              ),
            ),
            child: Column(
              children: [
                CircleAvatar(
                  radius: 45,
                  backgroundColor:
                      Colors.white,
                  child: Text(
                    username
                            .isNotEmpty
                        ? username[0]
                            .toUpperCase()
                        : "U",
                    style:
                        const TextStyle(
                      fontSize: 32,
                      fontWeight:
                          FontWeight.bold,
                      color:
                          Color(0xFF2E7D32),
                    ),
                  ),
                ),

                const SizedBox(
                  height: 16,
                ),

                Text(
                  username,
                  style:
                      const TextStyle(
                    color:
                        Colors.white,
                    fontSize: 24,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

                const SizedBox(
                  height: 6,
                ),

                Text(
                  "AgriStat User",
                  style:
                      TextStyle(
                    color:
                        Colors.white
                            .withValues(
                      alpha: 0.9,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // ===================
          // QUICK STATS
          // ===================

          Row(
            children: [
              statCard(
                "Products",
                "0",
                Icons.inventory,
                Colors.green,
              ),
              statCard(
                "Sales",
                "0",
                Icons.receipt_long,
                Colors.blue,
              ),
              statCard(
                "Forecasts",
                "0",
                Icons.show_chart,
                Colors.orange,
              ),
            ],
          ),

          const SizedBox(height: 24),

          // ===================
          // ACCOUNT INFO
          // ===================

          Align(
            alignment:
                Alignment.centerLeft,
            child: Text(
              "Account Information",
              style:
                  Theme.of(context)
                      .textTheme
                      .titleLarge,
            ),
          ),

          const SizedBox(height: 12),

          profileTile(
            Icons.person,
            "Username",
            username,
          ),

          profileTile(
            Icons.badge,
            "User ID",
            userId,
          ),

          profileTile(
            Icons.verified_user,
            "Account Status",
            "Active",
          ),

          const SizedBox(height: 20),

          // ===================
          // SETTINGS
          // ===================

          Align(
            alignment:
                Alignment.centerLeft,
            child: Text(
              "Settings",
              style:
                  Theme.of(context)
                      .textTheme
                      .titleLarge,
            ),
          ),

          const SizedBox(height: 12),

          Card(
            child: ListTile(
              leading: const Icon(
                Icons.edit,
              ),
              title:
                  const Text(
                "Edit Profile",
              ),
              trailing:
                  const Icon(
                Icons
                    .arrow_forward_ios,
                size: 16,
              ),
              onTap: () {},
            ),
          ),

          Card(
            child: ListTile(
              leading: const Icon(
                Icons.lock,
              ),
              title:
                  const Text(
                "Change Password",
              ),
              trailing:
                  const Icon(
                Icons
                    .arrow_forward_ios,
                size: 16,
              ),
              onTap: () {},
            ),
          ),

          Card(
            child: ListTile(
              leading: const Icon(
                Icons.notifications,
              ),
              title:
                  const Text(
                "Notifications",
              ),
              trailing:
                  const Icon(
                Icons
                    .arrow_forward_ios,
                size: 16,
              ),
              onTap: () {},
            ),
          ),

          const SizedBox(height: 30),

          // ===================
          // LOGOUT
          // ===================

          SizedBox(
            width: double.infinity,
            height: 55,
            child:
                ElevatedButton.icon(
              style:
                  ElevatedButton.styleFrom(
                backgroundColor:
                    Colors.red,
              ),
              onPressed: logout,
              icon: const Icon(
                Icons.logout,
                color:
                    Colors.white,
              ),
              label: const Text(
                "Logout",
                style:
                    TextStyle(
                  color:
                      Colors.white,
                  fontWeight:
                      FontWeight.bold,
                ),
              ),
            ),
          ),

          const SizedBox(height: 20),
        ],
      ),
    );
  }
}