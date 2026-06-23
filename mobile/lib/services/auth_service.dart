import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  // Create storage instance
  final _storage = const FlutterSecureStorage();

  // Keys for storage
  static const _keyUserId = 'user_id';
  static const _keyUsername = 'username';

  // Save user session
  Future<void> saveUserSession(String userId, String username) async {
    await _storage.write(key: _keyUserId, value: userId);
    await _storage.write(key: _keyUsername, value: username);
  }

  // Get saved username
  Future<String?> getUsername() async {
    return await _storage.read(key: _keyUsername);
  }

  // Check if user is logged in
  Future<bool> isLoggedIn() async {
    String? userId = await _storage.read(key: _keyUserId);
    return userId != null;
  }

  // Clear session (Logout)
  Future<void> logout() async {
    await _storage.deleteAll();
  }
}