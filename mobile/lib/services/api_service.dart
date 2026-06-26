import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

class ApiService {
  static const String baseUrl =
      'https://agric-stat-dash-1.onrender.com/api';

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

    _dio.interceptors.add(
      LoggingInterceptor(logger),
    );
  }

  // ==========================
  // AUTH
  // ==========================

  Future<Map<String, dynamic>> login(
    String username,
    String password,
  ) async {
    try {
      final response = await _dio.post(
        '/auth/login',

        data: {
          'username': username,
          'password': password,
        },
      );

      return Map<String, dynamic>.from(
        response.data,
      );
    } catch (e) {
      logger.e('Login failed: $e');

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

        queryParameters: {
          'skip': skip,
          'limit': limit,
        },
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Products error: $e',
      );

      return [];
    }
  }

  Future<Map<String, dynamic>?> getProduct(
    int id,
  ) async {
    try {
      final response =
          await _dio.get(
        '/products/$id',
      );

      return Map<String, dynamic>.from(
        response.data,
      );
    } catch (e) {
      logger.e(
        'Product error: $e',
      );

      return null;
    }
  }

  Future<Map<String, dynamic>?> createProduct(
    Map<String, dynamic> data,
  ) async {
    try {
      final response =
          await _dio.post(
        '/products',

        data: data,
      );

      return Map<String, dynamic>.from(
        response.data,
      );
    } catch (e) {
      logger.e(
        'Create product error: $e',
      );

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
      final response =
          await _dio.get(
        '/transactions',

        queryParameters: {
          'skip': skip,

          'limit': limit,

          if (productId != null)
            'product_id': productId,

          if (startDate != null)
            'start_date': startDate
                .toIso8601String()
                .split('T')[0],

          if (endDate != null)
            'end_date': endDate
                .toIso8601String()
                .split('T')[0],
        },
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Transactions error: $e',
      );

      return [];
    }
  }

  // ==========================
  // SUMMARY
  // ==========================

  Future<List<dynamic>>
      fetchSummary() async {
    try {
      final response =
          await _dio.get(
        '/transactions/summary',
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Summary error: $e',
      );

      return [];
    }
  }

  // ==========================
  // FORECASTS
  // ==========================

  Future<List<dynamic>> getForecasts({
    int skip = 0,

    int limit = 100,

    int? productId,

    DateTime? startDate,

    DateTime? endDate,
  }) async {
    try {
      final response =
          await _dio.get(
        '/forecasts',

        queryParameters: {
          'skip': skip,

          'limit': limit,

          if (productId != null)
            'product_id': productId,

          if (startDate != null)
            'start_date': startDate
                .toIso8601String()
                .split('T')[0],

          if (endDate != null)
            'end_date': endDate
                .toIso8601String()
                .split('T')[0],
        },
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Forecasts error: $e',
      );

      return [];
    }
  }

  Future<List<dynamic>>
      getProductForecasts(
    int productId,
  ) async {
    try {
      final response =
          await _dio.get(
        '/forecasts/product/$productId',
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Product forecasts error: $e',
      );

      return [];
    }
  }

  // ==========================
  // RECOMMENDATIONS
  // ==========================

  Future<List<dynamic>>
      getRecommendations({
    int skip = 0,

    int limit = 100,

    int? productId,

    String? status,
  }) async {
    try {
      final response =
          await _dio.get(
        '/recommendations',

        queryParameters: {
          'skip': skip,

          'limit': limit,

          if (productId != null)
            'product_id': productId,

          if (status != null)
            'status': status,
        },
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Recommendations error: $e',
      );

      return [];
    }
  }

  Future<bool>
      approveRecommendation(
    int id,
  ) async {
    try {
      await _dio.patch(
        '/recommendations/$id/approve',
      );

      return true;
    } catch (e) {
      logger.e(
        'Approve error: $e',
      );

      return false;
    }
  }

  Future<bool>
      implementRecommendation(
    int id,
  ) async {
    try {
      await _dio.patch(
        '/recommendations/$id/implement',
      );

      return true;
    } catch (e) {
      logger.e(
        'Implement error: $e',
      );

      return false;
    }
  }

  // ==========================
  // NOTIFICATIONS
  // ==========================

  Future<List<dynamic>>
      getNotifications() async {
    try {
      final response =
          await _dio.get(
        '/notifications',
      );

      return response.data is List
          ? response.data
          : [];
    } catch (e) {
      logger.e(
        'Notifications error: $e',
      );

      return [];
    }
  }

  Future<int>
      getUnreadNotificationCount() async {
    try {
      final response =
          await _dio.get(
        '/notifications/unread-count',
      );

      return response.data['count'] ?? 0;
    } catch (e) {
      logger.e(
        'Unread count error: $e',
      );

      return 0;
    }
  }

  Future<bool>
      markNotificationRead(
    int id,
  ) async {
    try {
      await _dio.patch(
        '/notifications/$id/read',
      );

      return true;
    } catch (e) {
      logger.e(
        'Mark read error: $e',
      );

      return false;
    }
  }

  Future<bool>
      markAllNotificationsRead() async {
    try {
      await _dio.patch(
        '/notifications/read-all',
      );

      return true;
    } catch (e) {
      logger.e(
        'Read all error: $e',
      );

      return false;
    }
  }

  // ==========================
  // HEALTH CHECK
  // ==========================

  Future<bool>
      checkHealth() async {
    try {
      final response =
          await _dio.get(
        '/health',
      );

      return response.statusCode ==
          200;
    } catch (e) {
      logger.e(
        'Health error: $e',
      );

      return false;
    }
  }
}

// ==========================
// LOGGER
// ==========================

class LoggingInterceptor
    extends Interceptor {
  final Logger logger;

  LoggingInterceptor(
    this.logger,
  );

  @override
  void onRequest(
    RequestOptions options,

    RequestInterceptorHandler
        handler,
  ) {
    logger.d(
      'REQUEST: ${options.method} ${options.uri}',
    );

    super.onRequest(
      options,
      handler,
    );
  }

  @override
  void onResponse(
    Response response,

    ResponseInterceptorHandler
        handler,
  ) {
    logger.d(
      'RESPONSE: ${response.statusCode}',
    );

    super.onResponse(
      response,
      handler,
    );
  }

  @override
  void onError(
    DioException err,

    ErrorInterceptorHandler
        handler,
  ) {
    logger.e(
      'ERROR: ${err.message}',
    );

    logger.e(
      'STATUS: ${err.response?.statusCode}',
    );

    super.onError(
      err,
      handler,
    );
  }
}