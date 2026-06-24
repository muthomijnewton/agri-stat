import 'api_service.dart';

class AppNotification {
  final int id;
  final String title;
  final String message;
  final String type;
  final bool read;
  final DateTime createdAt;

  AppNotification({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    required this.read,
    required this.createdAt,
  });

  factory AppNotification.fromJson(
    Map<String, dynamic> json,
  ) {
    return AppNotification(
      id: json['id'] ?? 0,

      title: json['title'] ?? '',

      message: json['message'] ?? '',

      type: json['type'] ?? 'info',

      read: json['read'] ?? false,

      createdAt: DateTime.parse(
        json['created_at'],
      ),
    );
  }
}

class NotificationService {
  final ApiService api = ApiService();

  Future<List<AppNotification>> getNotifications() async {
    try {
      final response =
          await api.getNotifications();

      return response
          .map<AppNotification>(
            (item) =>
                AppNotification.fromJson(item),
          )
          .toList();
    } catch (e) {
      return [];
    }
  }

  Future<int> getUnreadCount() async {
    try {
      return await api.getUnreadNotificationCount();
    } catch (e) {
      return 0;
    }
  }
}