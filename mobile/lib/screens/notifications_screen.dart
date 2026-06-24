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

  List<AppNotification>
      notifications = [];

  bool loading = true;

  bool hasError = false;

  DateTime? lastUpdated;

  @override
  void initState() {
    super.initState();

    loadNotifications();
  }

  // ==========================
  // LOAD
  // ==========================

  Future<void>
      loadNotifications() async {
    try {
      if (mounted) {
        setState(() {
          loading = true;

          hasError = false;
        });
      }

      final data =
          await service
              .getNotifications();

      if (!mounted) return;

      setState(() {
        notifications = data;

        loading = false;

        lastUpdated =
            DateTime.now();
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        loading = false;

        hasError = true;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Error: $e',
          ),
        ),
      );
    }
  }

  // ==========================
  // COUNTERS
  // ==========================

  int get unreadCount {
    return notifications
        .where(
          (n) => !n.read,
        )
        .length;
  }

  int get warningCount {
    return notifications
        .where(
          (n) =>
              n.type ==
              'warning',
        )
        .length;
  }

  int get dangerCount {
    return notifications
        .where(
          (n) =>
              n.type ==
              'danger',
        )
        .length;
  }

  // ==========================
  // COLORS
  // ==========================

  Color _getColor(
    AppNotification n,
  ) {
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

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(
    BuildContext context,
  ) {
    if (loading) {
      return const Center(
        child:
            CircularProgressIndicator(),
      );
    }

    if (hasError) {
      return Center(
        child: Column(
          mainAxisAlignment:
              MainAxisAlignment
                  .center,

          children: [
            const Icon(
              Icons.error_outline,

              size: 70,
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              'Unable to load notifications',
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  loadNotifications,

              child:
                  const Text(
                'Retry',
              ),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh:
          loadNotifications,

      child: ListView(
        padding:
            const EdgeInsets.all(
          12,
        ),

        children: [

          // ==================
          // TITLE
          // ==================

          const Text(
            'Notifications',

            style: TextStyle(
              fontSize: 22,

              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 16,
          ),

          // ==================
          // STATS
          // ==================

          Row(
            children: [
              Expanded(
                child: Card(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    child: Column(
                      children: [
                        const Text(
                          'Unread',
                        ),

                        Text(
                          '$unreadCount',
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              Expanded(
                child: Card(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    child: Column(
                      children: [
                        const Text(
                          'Warnings',
                        ),

                        Text(
                          '$warningCount',
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              Expanded(
                child: Card(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    child: Column(
                      children: [
                        const Text(
                          'Danger',
                        ),

                        Text(
                          '$dangerCount',
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 12,
          ),

          if (lastUpdated !=
              null)
            Align(
              alignment:
                  Alignment.centerRight,

              child: Text(
                'Updated ${lastUpdated!.hour}:${lastUpdated!.minute.toString().padLeft(2, '0')}',
              ),
            ),

          const SizedBox(
            height: 16,
          ),

          // ==================
          // EMPTY STATE
          // ==================

          if (notifications
              .isEmpty)

            const Padding(
              padding:
                  EdgeInsets.all(
                30,
              ),

              child: Center(
                child: Text(
                  'No notifications',
                ),
              ),
            ),

          // ==================
          // LIST
          // ==================

          ...notifications.map(
            (n) {
              return Card(
                margin:
                    const EdgeInsets.symmetric(
                  vertical: 6,
                ),

                child: ListTile(
                  leading: Icon(
                    Icons.notifications,

                    color:
                        _getColor(n),
                  ),

                  title: Text(
                    n.title,

                    style:
                        TextStyle(
                      fontWeight:
                          n.read
                              ? FontWeight.normal
                              : FontWeight.bold,
                    ),
                  ),

                  subtitle:
                      Text(
                    n.message,
                  ),

                  trailing: Icon(
                    n.read
                        ? Icons.check_circle

                        : Icons.fiber_new,

                    color: n.read

                        ? Colors.grey

                        : Colors.orange,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}