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

  bool hasError = false;

  bool refreshing = false;

  DateTime? lastUpdated;

  @override
  void initState() {
    super.initState();

    loadNotifications();
  }

  // ==========================
  // LOAD NOTIFICATIONS
  // ==========================

  Future<void> loadNotifications() async {

    if (refreshing) return;

    refreshing = true;

    try {

      if (mounted) {
        setState(() {
          loading = true;
          hasError = false;
        });
      }

      final data =
          await service.getNotifications();

      if (!mounted) return;

      setState(() {
        notifications = data;

        loading = false;

        hasError = false;

        lastUpdated =
            DateTime.now();
      });

    } catch (e) {

      if (!mounted) return;

      setState(() {

        loading = false;

        hasError = true;

        notifications = [];
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

    } finally {

      refreshing = false;
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

    // LOADING

    if (loading) {

      return const Center(
        child:
            CircularProgressIndicator(),
      );
    }

    // ERROR

    if (hasError) {

      return Center(
        child: Column(

          mainAxisAlignment:
              MainAxisAlignment.center,

          children: [

            const Icon(
              Icons.error_outline,

              size: 70,

              color: Colors.red,
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              'Unable to load notifications',

              style: TextStyle(
                fontSize: 16,
              ),
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton.icon(

              onPressed:
                  loadNotifications,

              icon: const Icon(
                Icons.refresh,
              ),

              label:
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
          // HEADER
          // ==================

          const Text(

            'Notifications',

            style: TextStyle(

              fontSize: 24,

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

                        const SizedBox(
                          height: 6,
                        ),

                        Text(

                          '$unreadCount',

                          style:
                              const TextStyle(

                            fontSize: 22,

                            fontWeight:
                                FontWeight.bold,
                          ),
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

                        const SizedBox(
                          height: 6,
                        ),

                        Text(

                          '$warningCount',

                          style:
                              const TextStyle(

                            fontSize: 22,

                            fontWeight:
                                FontWeight.bold,
                          ),
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

                        const SizedBox(
                          height: 6,
                        ),

                        Text(

                          '$dangerCount',

                          style:
                              const TextStyle(

                            fontSize: 22,

                            fontWeight:
                                FontWeight.bold,
                          ),
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

          // ==================
          // LAST UPDATED
          // ==================

          if (lastUpdated != null)

            Align(

              alignment:
                  Alignment.centerRight,

              child: Text(

                'Updated ${lastUpdated!.hour}:${lastUpdated!.minute.toString().padLeft(2, '0')}',

                style:
                    const TextStyle(

                  color: Colors.grey,
                ),
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

              child: Column(

                children: [

                  Icon(

                    Icons.notifications_off,

                    size: 60,

                    color: Colors.grey,
                  ),

                  SizedBox(
                    height: 12,
                  ),

                  Text(

                    'No notifications',

                    style: TextStyle(

                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),

          // ==================
          // LIST
          // ==================

          ...notifications.map(

            (n) {

              return Card(

                color: n.read

                    ? null

                    : Colors.orange.withValues(
                        alpha: 0.08,
                      ),

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

                    color:

                        n.read

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