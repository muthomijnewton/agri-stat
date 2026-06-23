import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final _storage = const FlutterSecureStorage();

  static const _keyUserId = 'user_id';
  static const _keyUsername = 'username';
  static const _keyToken = 'token';

  /// =========================
  /// SAVE SESSION (UPDATED)
  /// =========================
  Future<void> saveUserSession(
    String userId,
    String username,
    String token,
  ) async {
    await _storage.write(key: _keyUserId, value: userId);
    await _storage.write(key: _keyUsername, value: username);
    await _storage.write(key: _keyToken, value: token);
  }

  /// Get token (IMPORTANT for API AUTH)
  Future<String?> getToken() async {
    return await _storage.read(key: _keyToken);
  }

  Future<String?> getUsername() async {
    return await _storage.read(key: _keyUsername);
  }

  Future<String?> getUserId() async {
    return await _storage.read(key: _keyUserId);
  }

  Future<bool> isLoggedIn() async {
    final userId = await _storage.read(key: _keyUserId);
    return userId != null;
  }

  Future<void> logout() async {
    await _storage.deleteAll();
  }
}