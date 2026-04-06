import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  
  late Dio _dio;
  final logger = Logger();

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
      contentType: 'application/json',
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // Add logging interceptor
    _dio.interceptors.add(
      LoggingInterceptor(logger),
    );
  }

  // Products API
  Future<List<dynamic>> getProducts({int skip = 0, int limit = 100}) async {
    try {
      final response = await _dio.get(
        '/products',
        queryParameters: {'skip': skip, 'limit': limit},
      );
      return response.data;
    } catch (e) {
      logger.e('Error fetching products: $e');
      rethrow;
    }
  }

  Future<dynamic> getProduct(int id) async {
    try {
      final response = await _dio.get('/products/$id');
      return response.data;
    } catch (e) {
      logger.e('Error fetching product: $e');
      rethrow;
    }
  }

  Future<dynamic> createProduct(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/products', data: data);
      return response.data;
    } catch (e) {
      logger.e('Error creating product: $e');
      rethrow;
    }
  }

  // Transactions API
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
          if (startDate != null) 'start_date': startDate.toString().split(' ')[0],
          if (endDate != null) 'end_date': endDate.toString().split(' ')[0],
        },
      );
      return response.data;
    } catch (e) {
      logger.e('Error fetching transactions: $e');
      rethrow;
    }
  }

  Future<dynamic> createTransaction(Map<String, dynamic> data) async {
    try {
      final response = await _dio.post('/transactions', data: data);
      return response.data;
    } catch (e) {
      logger.e('Error creating transaction: $e');
      rethrow;
    }
  }

  // Forecasts API
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
          if (startDate != null) 'start_date': startDate.toString().split(' ')[0],
          if (endDate != null) 'end_date': endDate.toString().split(' ')[0],
        },
      );
      return response.data;
    } catch (e) {
      logger.e('Error fetching forecasts: $e');
      rethrow;
    }
  }

  Future<List<dynamic>> getProductForecasts(int productId, {int days = 30}) async {
    try {
      final response = await _dio.get(
        '/forecasts/product/$productId',
        queryParameters: {'days': days},
      );
      return response.data;
    } catch (e) {
      logger.e('Error fetching product forecasts: $e');
      rethrow;
    }
  }

  // Recommendations API
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
      return response.data;
    } catch (e) {
      logger.e('Error fetching recommendations: $e');
      rethrow;
    }
  }

  Future<List<dynamic>> getProductRecommendations(int productId) async {
    try {
      final response = await _dio.get('/recommendations/product/$productId');
      return response.data;
    } catch (e) {
      logger.e('Error fetching product recommendations: $e');
      rethrow;
    }
  }

  Future<dynamic> approveRecommendation(int id) async {
    try {
      final response = await _dio.patch('/recommendations/$id/approve');
      return response.data;
    } catch (e) {
      logger.e('Error approving recommendation: $e');
      rethrow;
    }
  }

  Future<dynamic> implementRecommendation(int id) async {
    try {
      final response = await _dio.patch('/recommendations/$id/implement');
      return response.data;
    } catch (e) {
      logger.e('Error implementing recommendation: $e');
      rethrow;
    }
  }

  // Health check
  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      logger.e('Error checking health: $e');
      return false;
    }
  }
}

class LoggingInterceptor extends Interceptor {
  final Logger logger;

  LoggingInterceptor(this.logger);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    logger.d('REQUEST: ${options.method} ${options.path}');
    logger.d('HEADERS: ${options.headers}');
    if (options.data != null) {
      logger.d('DATA: ${options.data}');
    }
    super.onRequest(options, handler);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    logger.d('RESPONSE: ${response.statusCode} ${response.requestOptions.path}');
    logger.d('DATA: ${response.data}');
    super.onResponse(response, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    logger.e('ERROR: ${err.message}');
    logger.e('STATUS: ${err.response?.statusCode}');
    super.onError(err, handler);
  }
}
