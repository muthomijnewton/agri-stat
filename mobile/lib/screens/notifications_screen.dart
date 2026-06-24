import 'package:flutter/material.dart';

import '../services/notification_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() =>
      _NotificationsScreenState();
}

class _NotificationsScreenState
    extends State<NotificationsScreen> {

  final NotificationService service =
      NotificationService();

  List<AppNotification> notifications = [];

  bool loading = true;

  @override
  void initState() {
    super.initState();

    loadNotifications();
  }

  Future<void> loadNotifications() async {
    final data =
        await service.getNotifications();

    if (!mounted) return;

    setState(() {
      notifications = data;

      loading = false;
    });
  }

  Color _getColor(AppNotification n) {
    switch (n.type) {
      case 'danger':
        return Colors.red;

      case 'warning':
        return Colors.orange;

      case 'success':
        return Colors.green;

      default:
        return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text('Notifications'),

        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),

            onPressed: loadNotifications,
          ),
        ],
      ),

      body: loading
          ? const Center(
              child:
                  CircularProgressIndicator(),
            )
          : notifications.isEmpty
              ? const Center(
                  child: Text(
                    'No notifications',
                  ),
                )
              : ListView.builder(
                  itemCount:
                      notifications.length,

                  itemBuilder:
                      (context, index) {

                    final n =
                        notifications[index];

                    return Card(
                      margin:
                          const EdgeInsets
                              .symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),

                      child: ListTile(
                        leading: Icon(
                          Icons.notifications,

                          color:
                              _getColor(n),
                        ),

                        title:
                            Text(n.title),

                        subtitle:
                            Text(n.message),

                        trailing: Icon(
                          n.read
                              ? Icons.check
                              : Icons.fiber_new,

                          color: n.read
                              ? Colors.grey
                              : Colors.orange,
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}