class AppNotification {
  final String title;
  final String message;
  final DateTime time;
  final NotificationLevel level;
  bool read;

  AppNotification({
    required this.title,
    required this.message,
    required this.time,
    this.level = NotificationLevel.info,
    this.read = false,
  });
}

/// SIMPLE TYPE SYSTEM (fixes your error)
enum NotificationLevel {
  info,
  success,
  warning,
  danger,
}

class NotificationService {
  final List<AppNotification> _notifications = [
    AppNotification(
      title: "Welcome",
      message: "AgriStat system started successfully",
      time: DateTime.now(),
      level: NotificationLevel.success,
    ),
  ];

  List<AppNotification> get notifications => _notifications;

  int getUnreadCount() {
    return _notifications.where((n) => !n.read).length;
  }

  void markAllRead() {
    for (var n in _notifications) {
      n.read = true;
    }
  }

  void addNotification(
    String title,
    String message, {
    NotificationLevel level = NotificationLevel.info,
  }) {
    _notifications.insert(
      0,
      AppNotification(
        title: title,
        message: message,
        time: DateTime.now(),
        level: level,
      ),
    );
  }
}