import 'package:dio/dio.dart';
import 'package:logger/logger.dart';
import '../utils/type_safety.dart';

class ApiService {
  static const String baseUrl =
      'https://agric-stat-dash-1.onrender.com/api';

  late final Dio _dio;
  final Logger logger = Logger();

  ApiService() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(LoggingInterceptor(logger));
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
        options: Options(
          contentType: Headers.jsonContentType,
        ),
      );

      return Map<String, dynamic>.from(response.data);
    } on DioException catch (e) {
      logger.e('Login failed: ${e.response?.data}');
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
        '/products/',
        queryParameters: {'skip': skip, 'limit': limit},
      );

      final data = response.data;
      return data is List ? data : [];
    } catch (e) {
      logger.e('Error fetching products: $e');
      return [];
    }
  }

  Future<dynamic> getProduct(int id) async {
    try {
      final response = await _dio.get('/products/$id');
      return response.data;
    } catch (e) {
      logger.e('Error fetching product: $e');
      return null;
    }
  }

  Future<dynamic> createProduct(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/products', data: data);
      return response.data;
    } catch (e) {
      logger.e('Error creating product: $e');
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

      final data = response.data;
      return data is List ? data : [];
    } catch (e) {
      logger.e('Error fetching transactions: $e');
      return [];
    }
  }

  // ==========================
  // SUMMARY (IMPORTANT FIXED)
  // ==========================

  Future<List<dynamic>> fetchSummary() async {
    try {
      final response = await _dio.get('/transactions/summary');

      final data = response.data;
      return data is List ? data : [];
    } catch (e) {
      logger.e('Error fetching summary: $e');
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
      final response = await _dio.get(
        '/forecasts',
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

      final data = response.data;
      return data is List ? data : [];
    } catch (e) {
      logger.e('Error fetching forecasts: $e');
      return [];
    }
  }
  Future<List<dynamic>> getProductForecasts(int productId) async {
  try {
    final response = await _dio.get('/forecasts/product/$productId');

    final data = response.data;
    if (data is List) return data;

    return [];
  } catch (e) {
    logger.e('Error fetching product forecasts: $e');
    rethrow;
  }
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

      final data = response.data;
      return data is List ? data : [];
    } catch (e) {
      logger.e('Error fetching recommendations: $e');
      return [];
    }
  }

  Future<dynamic> approveRecommendation(int id) async {
    try {
      final response = await _dio.patch('/recommendations/$id/approve');
      return response.data;
    } catch (e) {
      logger.e('Error approving recommendation: $e');
      return null;
    }
  }

  Future<dynamic> implementRecommendation(int id) async {
    try {
      final response = await _dio.patch('/recommendations/$id/implement');
      return response.data;
    } catch (e) {
      logger.e('Error implementing recommendation: $e');
      return null;
    }
  }

  // ==========================
  // HEALTH CHECK
  // ==========================

  Future<bool> checkHealth() async {
    try {
      final response =
          await Dio().get('https://agric-stat-dash-1.onrender.com/health');

      return response.statusCode == 200;
    } catch (e) {
      logger.e('Health check error: $e');
      return false;
    }
  }
}

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
    logger.e('ERROR: ${err.response?.data ?? err.message}');
    logger.e('STATUS: ${err.response?.statusCode}');
    super.onError(err, handler);
  }
}