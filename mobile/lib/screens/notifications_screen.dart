import 'package:flutter/material.dart';
import '../services/notification_service.dart';

class NotificationsScreen extends StatelessWidget {
  final NotificationService service;

  const NotificationsScreen({
    super.key,
    required this.service,
  });

  Color _color(String title) {
    final t = title.toLowerCase();

    if (t.contains("error") || t.contains("fail")) {
      return Colors.red;
    } else if (t.contains("warning")) {
      return Colors.orange;
    } else if (t.contains("success") || t.contains("done")) {
      return Colors.green;
    }
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    final notifications = service.notifications;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Notifications"),
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all),
            onPressed: () {
              service.markAllRead();
              (context as Element).markNeedsBuild();
            },
          )
        ],
      ),
      body: notifications.isEmpty
          ? const Center(
              child: Text(
                "No notifications",
                style: TextStyle(fontSize: 16),
              ),
            )
          : ListView.builder(
              itemCount: notifications.length,
              itemBuilder: (context, index) {
                final n = notifications[index];

                return Card(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  child: ListTile(
                    leading: Icon(
                      Icons.notifications,
                      color: _color(n.title),
                    ),
                    title: Text(
                      n.title,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(n.message),
                    trailing: Text(
                      "${n.time.hour}:${n.time.minute}",
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                );
              },
            ),
    );
  }
}