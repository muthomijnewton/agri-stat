import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';

class ApiService {
  static const String baseUrl =
      String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://agric-stat-dash-1.onrender.com/api',
  );

  late final Dio _dio;

  final Logger logger = Logger();

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 60),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(AuthInterceptor(logger));
    _dio.interceptors.add(LoggingInterceptor(logger));
  }

  // ==========================
  // AUTH
  // ==========================

  Future<Map<String, dynamic>> login(
    String username,
    String password,
  ) async {
    final response = await _dio.post(
      '/auth/login',
      data: {'username': username, 'password': password},
    );
    return Map<String, dynamic>.from(response.data);
  }

  /// GET /auth/me — returns the full user profile for the current token.
  Future<Map<String, dynamic>?> getProfile() async {
    try {
      final response = await _dio.get('/auth/me');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('getProfile error: $e');
      return null;
    }
  }

  /// PATCH /auth/me — update profile fields or change password.
  ///
  /// Accepted fields: username, email, full_name, current_password, new_password
  Future<Map<String, dynamic>?> updateProfile(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _dio.patch('/auth/me', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('updateProfile error: $e');
      rethrow;
    }
  }

  // ==========================
  // PRODUCTS
  // ==========================

  Future<List<dynamic>> getProducts({
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final response = await _dio.get(
        '/products',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('getProducts error: $e');
      return [];
    }
  }

  Future<Map<String, dynamic>?> getProduct(int id) async {
    try {
      final response = await _dio.get('/products/$id');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('getProduct error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> createProduct(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _dio.post('/products', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('createProduct error: $e');
      return null;
    }
  }

  // ==========================
  // TRANSACTIONS
  // ==========================

  Future<List<dynamic>> getTransactions({
    int skip = 0,
    int limit = 100,
    int? productId,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      final response = await _dio.get(
        '/transactions',
        queryParameters: {
          'skip': skip,
          'limit': limit,
          if (productId != null) 'product_id': productId,
          if (startDate != null)
            'start_date': startDate.toIso8601String().split('T')[0],
          if (endDate != null)
            'end_date': endDate.toIso8601String().split('T')[0],
        },
      );
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('getTransactions error: $e');
      return [];
    }
  }

  /// POST /transactions — record a new transaction.
  Future<Map<String, dynamic>?> createTransaction(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _dio.post('/transactions', data: data);
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('createTransaction error: $e');
      rethrow;
    }
  }

  // ==========================
  // STATS / SUMMARY
  // ==========================

  /// GET /stats/transaction-type-split
  ///
  /// Returns a list of objects: { type, count, revenue, quantity }
  /// Used by the dashboard chart to show sales vs purchases split.
  Future<List<dynamic>> fetchTransactionTypeSplit({int days = 30}) async {
    try {
      final response = await _dio.get(
        '/stats/transaction-type-split',
        queryParameters: {'days': days},
      );
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('fetchTransactionTypeSplit error: $e');
      return [];
    }
  }

  /// GET /stats/summary — overall platform counts.
  Future<Map<String, dynamic>> fetchStatsSummary() async {
    try {
      final response = await _dio.get('/stats/summary');
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      logger.e('fetchStatsSummary error: $e');
      return {};
    }
  }

  // ==========================
  // FORECASTS
  // ==========================

  Future<List<dynamic>> getForecasts({
    int skip = 0,
    int limit = 100,
    int? productId,
  }) async {
    try {
      final response = await _dio.get(
        '/forecasts',
        queryParameters: {
          'skip': skip,
          'limit': limit,
          if (productId != null) 'product_id': productId,
        },
      );
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('getForecasts error: $e');
      return [];
    }
  }

  /// Fetch forecasts filtered to a single product.
  /// Uses the correct query-param form: GET /forecasts?product_id={id}
  Future<List<dynamic>> getProductForecasts(int productId) async {
    return getForecasts(productId: productId);
  }

  // ==========================
  // RECOMMENDATIONS
  // ==========================

  Future<List<dynamic>> getRecommendations({
    int skip = 0,
    int limit = 100,
    int? productId,
    String? status,
  }) async {
    try {
      final response = await _dio.get(
        '/recommendations',
        queryParameters: {
          'skip': skip,
          'limit': limit,
          if (productId != null) 'product_id': productId,
          if (status != null) 'status': status,
        },
      );
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('getRecommendations error: $e');
      return [];
    }
  }

  Future<bool> approveRecommendation(int id) async {
    try {
      await _dio.patch('/recommendations/$id/approve');
      return true;
    } catch (e) {
      logger.e('approveRecommendation error: $e');
      return false;
    }
  }

  Future<bool> implementRecommendation(int id) async {
    try {
      await _dio.patch('/recommendations/$id/implement');
      return true;
    } catch (e) {
      logger.e('implementRecommendation error: $e');
      return false;
    }
  }

  // ==========================
  // NOTIFICATIONS
  // ==========================

  Future<List<dynamic>> getNotifications() async {
    try {
      final response = await _dio.get('/notifications/');
      return response.data is List ? response.data : [];
    } catch (e) {
      logger.e('getNotifications error: $e');
      return [];
    }
  }

  Future<int> getUnreadNotificationCount() async {
    try {
      final response = await _dio.get('/notifications/unread-count');
      return response.data['count'] ?? 0;
    } catch (e) {
      logger.e('getUnreadNotificationCount error: $e');
      return 0;
    }
  }

  Future<bool> markNotificationRead(int id) async {
    try {
      await _dio.patch('/notifications/$id/read');
      return true;
    } catch (e) {
      logger.e('markNotificationRead error: $e');
      return false;
    }
  }

  Future<bool> markAllNotificationsRead() async {
    try {
      await _dio.patch('/notifications/read-all');
      return true;
    } catch (e) {
      logger.e('markAllNotificationsRead error: $e');
      return false;
    }
  }

  // ==========================
  // HEALTH CHECK
  // ==========================

  Future<bool> checkHealth() async {
    try {
      final healthUrl = baseUrl.endsWith('/api')
          ? '${baseUrl.substring(0, baseUrl.length - 4)}/health'
          : '$baseUrl/health';
      final response = await _dio.get(
        healthUrl,
        options: Options(sendTimeout: const Duration(seconds: 10)),
      );
      return response.statusCode == 200;
    } catch (e) {
      logger.e('checkHealth error: $e');
      return false;
    }
  }
}

// ==========================
// AUTH INTERCEPTOR
// ==========================

class AuthInterceptor extends Interceptor {
  final Logger logger;
  final _storage = const FlutterSecureStorage();

  AuthInterceptor(this.logger);

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!options.headers.containsKey('Authorization')) {
      final token = await _storage.read(key: 'token');
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    super.onRequest(options, handler);
  }
}

// ==========================
// LOGGING INTERCEPTOR
// ==========================

class LoggingInterceptor extends Interceptor {
  final Logger logger;

  LoggingInterceptor(this.logger);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    logger.d('REQUEST: ${options.method} ${options.uri}');
    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    logger.d('RESPONSE: ${response.statusCode}');
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    logger.e('ERROR: ${err.message} — STATUS: ${err.response?.statusCode}');
    super.onError(err, handler);
  }
}
