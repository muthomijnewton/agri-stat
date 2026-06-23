class AppNotification {
  final String title;
  final String message;
  final NotificationType type;
  final DateTime time;

  AppNotification({
    required this.title,
    required this.message,
    required this.type,
    required this.time,
  });
}

enum NotificationType {
  info,
  warning,
  danger,
  success,
}