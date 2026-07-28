import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../utils/type_safety.dart';
import 'login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ApiService _api = ApiService();
  final AuthService _auth = AuthService();

  bool _loading = true;
  bool _hasError = false;

  Map<String, dynamic> _profile = {};

  // Stats loaded in parallel
  int _productCount = 0;
  int _txnCount = 0;
  int _forecastCount = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  // ==========================
  // LOAD
  // ==========================

  Future<void> _load() async {
    try {
      setState(() { _loading = true; _hasError = false; });

      final results = await Future.wait([
        _api.getProfile(),
        _api.getProducts(),
        _api.getTransactions(limit: 1000),
        _api.getForecasts(),
      ]);

      final profile = results[0] as Map<String, dynamic>? ?? {};
      final products = results[1] as List;
      final txns = results[2] as List;
      final forecasts = results[3] as List;

      if (!mounted) return;
      setState(() {
        _profile = profile;
        _productCount = products.length;
        _txnCount = txns.length;
        _forecastCount = forecasts.length;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _loading = false; });
    }
  }

  // ==========================
  // LOGOUT
  // ==========================

  Future<void> _logout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to log out?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Logout'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;

    await _auth.logout();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  // ==========================
  // EDIT PROFILE DIALOG
  // ==========================

  Future<void> _openEditProfile() async {
    final emailCtrl = TextEditingController(text: _profile['email']?.toString() ?? '');
    final fullNameCtrl = TextEditingController(text: _profile['full_name']?.toString() ?? '');
    final phoneCtrl = TextEditingController(text: _profile['phone']?.toString() ?? '');
    final formKey = GlobalKey<FormState>();
    bool saving = false;

    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Edit Profile'),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Username (read-only — used as JWT subject)
                  TextFormField(
                    initialValue: _profile['username']?.toString() ?? '',
                    readOnly: true,
                    decoration: const InputDecoration(
                      labelText: 'Username',
                      helperText: 'Username cannot be changed',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: fullNameCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Full Name',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: emailCtrl,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(
                      labelText: 'Email *',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.trim().isEmpty) return 'Email is required';
                      if (!v.contains('@')) return 'Enter a valid email';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: phoneCtrl,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Phone',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: saving ? null : () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: saving
                  ? null
                  : () async {
                      if (!formKey.currentState!.validate()) return;
                      setLocal(() => saving = true);
                      try {
                        await _api.updateProfile({
                          'email': emailCtrl.text.trim(),
                          if (fullNameCtrl.text.trim().isNotEmpty)
                            'full_name': fullNameCtrl.text.trim(),
                          if (phoneCtrl.text.trim().isNotEmpty)
                            'phone': phoneCtrl.text.trim(),
                        });
                        if (!ctx.mounted) return;
                        Navigator.pop(ctx);
                        await _load();
                        if (!mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Profile updated')),
                        );
                      } catch (e) {
                        setLocal(() => saving = false);
                        if (!ctx.mounted) return;
                        ScaffoldMessenger.of(ctx).showSnackBar(
                          SnackBar(content: Text('Update failed: ${_friendlyError(e)}')),
                        );
                      }
                    },
              child: saving
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Save'),
            ),
          ],
        ),
      ),
    );

    emailCtrl.dispose();
    fullNameCtrl.dispose();
    phoneCtrl.dispose();
  }

  // ==========================
  // CHANGE PASSWORD DIALOG
  // ==========================

  Future<void> _openChangePassword() async {
    final currentCtrl = TextEditingController();
    final newCtrl = TextEditingController();
    final confirmCtrl = TextEditingController();
    final formKey = GlobalKey<FormState>();
    bool saving = false;
    bool showCurrent = false;
    bool showNew = false;

    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setLocal) => AlertDialog(
          title: const Text('Change Password'),
          content: SingleChildScrollView(
            child: Form(
              key: formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    controller: currentCtrl,
                    obscureText: !showCurrent,
                    decoration: InputDecoration(
                      labelText: 'Current Password *',
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: Icon(showCurrent ? Icons.visibility_off : Icons.visibility),
                        onPressed: () => setLocal(() => showCurrent = !showCurrent),
                      ),
                    ),
                    validator: (v) => (v == null || v.isEmpty) ? 'Required' : null,
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: newCtrl,
                    obscureText: !showNew,
                    decoration: InputDecoration(
                      labelText: 'New Password *',
                      border: const OutlineInputBorder(),
                      helperText: 'Minimum 6 characters',
                      suffixIcon: IconButton(
                        icon: Icon(showNew ? Icons.visibility_off : Icons.visibility),
                        onPressed: () => setLocal(() => showNew = !showNew),
                      ),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Required';
                      if (v.length < 6) return 'Minimum 6 characters';
                      return null;
                    },
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: confirmCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Confirm New Password *',
                      border: OutlineInputBorder(),
                    ),
                    validator: (v) {
                      if (v == null || v.isEmpty) return 'Required';
                      if (v != newCtrl.text) return 'Passwords do not match';
                      return null;
                    },
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: saving ? null : () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: saving
                  ? null
                  : () async {
                      if (!formKey.currentState!.validate()) return;
                      setLocal(() => saving = true);
                      try {
                        await _api.updateProfile({
                          'current_password': currentCtrl.text,
                          'new_password': newCtrl.text,
                        });
                        if (!ctx.mounted) return;
                        Navigator.pop(ctx);
                        if (!mounted) return;
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Password changed successfully')),
                        );
                      } catch (e) {
                        setLocal(() => saving = false);
                        if (!ctx.mounted) return;
                        ScaffoldMessenger.of(ctx).showSnackBar(
                          SnackBar(
                            content: Text('Failed: ${_friendlyError(e)}'),
                            backgroundColor: Colors.red.shade700,
                          ),
                        );
                      }
                    },
              child: saving
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Change'),
            ),
          ],
        ),
      ),
    );

    currentCtrl.dispose();
    newCtrl.dispose();
    confirmCtrl.dispose();
  }

  // ==========================
  // HELPERS
  // ==========================

  String _friendlyError(Object e) {
    final s = e.toString();
    final match = RegExp(r'"detail"\s*:\s*"([^"]+)"').firstMatch(s);
    return match?.group(1) ?? s;
  }

  String get _displayName {
    final full = _profile['full_name']?.toString() ?? '';
    return full.isNotEmpty ? full : (_profile['username']?.toString() ?? 'User');
  }

  String get _initials {
    final name = _displayName;
    final parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : 'U';
  }

  // ==========================
  // WIDGETS
  // ==========================

  Widget _statCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 4),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          children: [
            Icon(icon, color: color),
            const SizedBox(height: 8),
            Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            const SizedBox(height: 4),
            Text(title, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _infoTile(IconData icon, String label, String value) {
    if (value.isEmpty) return const SizedBox.shrink();
    return Card(
      elevation: 0,
      child: ListTile(
        leading: Icon(icon),
        title: Text(label),
        subtitle: Text(value),
      ),
    );
  }

  Widget _actionTile(IconData icon, String label, VoidCallback onTap) {
    return Card(
      elevation: 0,
      child: ListTile(
        leading: Icon(icon),
        title: Text(label),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
        onTap: onTap,
      ),
    );
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_hasError) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64),
              const SizedBox(height: 16),
              const Text('Unable to load profile'),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _load, child: const Text('Retry')),
            ],
          ),
        ),
      );
    }

    final email = _profile['email']?.toString() ?? '';
    final username = _profile['username']?.toString() ?? '';
    final isAdmin = _profile['is_admin'] == true;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _load,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Avatar card ──
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF2E7D32), Color(0xFF66BB6A)],
                ),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 45,
                    backgroundColor: Colors.white,
                    child: Text(
                      _initials,
                      style: const TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2E7D32),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _displayName,
                    style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    email.isNotEmpty ? email : username,
                    style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 14),
                  ),
                  if (isAdmin) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.25),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'Admin',
                        style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ],
              ),
            ),

            const SizedBox(height: 24),

            // ── Quick stats ──
            Row(
              children: [
                _statCard('Products', '$_productCount', Icons.inventory, Colors.green),
                _statCard('Sales', '$_txnCount', Icons.receipt_long, Colors.blue),
                _statCard('Forecasts', '$_forecastCount', Icons.show_chart, Colors.orange),
              ],
            ),

            const SizedBox(height: 24),

            // ── Account info ──
            Text('Account Information', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _infoTile(Icons.person, 'Username', username),
            _infoTile(Icons.email, 'Email', email),
            _infoTile(Icons.badge, 'Full Name', _profile['full_name']?.toString() ?? ''),
            _infoTile(Icons.phone, 'Phone', _profile['phone']?.toString() ?? ''),
            _infoTile(Icons.verified_user, 'Account Status', _profile['is_active'] == true ? 'Active' : 'Inactive'),

            const SizedBox(height: 24),

            // ── Settings ──
            Text('Settings', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 12),
            _actionTile(Icons.edit, 'Edit Profile', _openEditProfile),
            _actionTile(Icons.lock, 'Change Password', _openChangePassword),

            const SizedBox(height: 30),

            // ── Logout ──
            SizedBox(
              height: 52,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                onPressed: _logout,
                icon: const Icon(Icons.logout, color: Colors.white),
                label: const Text('Logout', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),

            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}
