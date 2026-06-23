import 'package:flutter/material.dart';
import '../services/notification_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final NotificationService service = NotificationService();

  Color _getColor(AppNotification n) {
    return n.read ? Colors.grey : Colors.orange;
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
              setState(() {
                service.markAllRead();
              });
            },
          ),
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
                    horizontal: 12,
                    vertical: 6,
                  ),
                  child: ListTile(
                    leading: Icon(
                      Icons.notifications,
                      color: _getColor(n),
                    ),

                    title: Text(
                      n.title,
                      style: TextStyle(
                        fontWeight:
                            n.read ? FontWeight.normal : FontWeight.bold,
                      ),
                    ),

                    subtitle: Text(n.message),

                    trailing: Icon(
                      n.read ? Icons.check : Icons.fiber_new,
                      color: n.read ? Colors.grey : Colors.orange,
                    ),

                    onTap: () {
                      setState(() {
                        n.read = true;
                      });
                    },
                  ),
                );
              },
            ),
    );
  }
}