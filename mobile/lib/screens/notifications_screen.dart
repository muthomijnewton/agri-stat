import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../utils/type_safety.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final ApiService _api = ApiService();

  List<Map<String, dynamic>> _notifications = [];
  bool _loading = true;
  bool _hasError = false;
  bool _markingAll = false;
  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();
    _load();
  }

  // ==========================
  // LOAD
  // ==========================

  Future<void> _load() async {
    try {
      if (mounted) setState(() { _loading = true; _hasError = false; });

      final data = await _api.getNotifications();

      // Sort: unread first, then by id descending (newest first)
      final list = data.cast<Map<String, dynamic>>()
        ..sort((a, b) {
          final aRead = a['read'] == true ? 1 : 0;
          final bRead = b['read'] == true ? 1 : 0;
          if (aRead != bRead) return aRead - bRead;
          return TypeSafety.toInt(b['id']) - TypeSafety.toInt(a['id']);
        });

      if (!mounted) return;
      setState(() {
        _notifications = list;
        _lastUpdated = DateTime.now();
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _loading = false; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  // ==========================
  // MARK SINGLE READ
  // ==========================

  Future<void> _markRead(Map<String, dynamic> n) async {
    if (n['read'] == true) return; // already read — nothing to do

    final id = TypeSafety.toInt(n['id']);
    // Optimistic update
    setState(() => n['read'] = true);

    final ok = await _api.markNotificationRead(id);
    if (!ok && mounted) {
      // Roll back
      setState(() => n['read'] = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not mark as read')),
      );
    }
  }

  // ==========================
  // MARK ALL READ
  // ==========================

  Future<void> _markAllRead() async {
    final hasUnread = _notifications.any((n) => n['read'] != true);
    if (!hasUnread) return;

    setState(() => _markingAll = true);

    // Optimistic update
    final prev = _notifications.map((n) => Map<String, dynamic>.from(n)).toList();
    setState(() {
      for (final n in _notifications) {
        n['read'] = true;
      }
    });

    final ok = await _api.markAllNotificationsRead();
    if (!ok && mounted) {
      // Roll back
      setState(() => _notifications = prev);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Could not mark all as read')),
      );
    }

    if (mounted) setState(() => _markingAll = false);
  }

  // ==========================
  // HELPERS
  // ==========================

  int get _unreadCount => _notifications.where((n) => n['read'] != true).length;
  int get _warningCount => _notifications.where((n) => n['type'] == 'warning').length;
  int get _dangerCount => _notifications.where((n) => n['type'] == 'danger').length;

  Color _typeColor(String? type) {
    switch (type) {
      case 'danger': return Colors.red;
      case 'warning': return Colors.orange;
      case 'success': return Colors.green;
      default: return Colors.blue;
    }
  }

  IconData _typeIcon(String? type) {
    switch (type) {
      case 'danger': return Icons.error_outline;
      case 'warning': return Icons.warning_amber_rounded;
      case 'success': return Icons.check_circle_outline;
      default: return Icons.info_outline;
    }
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    if (_hasError) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 70, color: Colors.red),
            const SizedBox(height: 16),
            const Text('Unable to load notifications', style: TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _load,
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          // ── Header row ──
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Notifications',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              if (_unreadCount > 0)
                _markingAll
                    ? const SizedBox(
                        width: 20, height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : TextButton.icon(
                        onPressed: _markAllRead,
                        icon: const Icon(Icons.done_all, size: 16),
                        label: const Text('Mark all read'),
                      ),
            ],
          ),

          const SizedBox(height: 16),

          // ── Counter strip ──
          Row(
            children: [
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(children: [
                      const Text('Unread'),
                      const SizedBox(height: 4),
                      Text('$_unreadCount',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    ]),
                  ),
                ),
              ),
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(children: [
                      const Text('Warnings'),
                      const SizedBox(height: 4),
                      Text('$_warningCount',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    ]),
                  ),
                ),
              ),
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(children: [
                      const Text('Danger'),
                      const SizedBox(height: 4),
                      Text('$_dangerCount',
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                    ]),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),

          if (_lastUpdated != null)
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
                style: const TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ),

          const SizedBox(height: 12),

          // ── Empty state ──
          if (_notifications.isEmpty)
            const Padding(
              padding: EdgeInsets.all(30),
              child: Column(
                children: [
                  Icon(Icons.notifications_off, size: 60, color: Colors.grey),
                  SizedBox(height: 12),
                  Text('No notifications', style: TextStyle(fontSize: 16)),
                ],
              ),
            ),

          // ── Notification list ──
          ..._notifications.map((n) {
            final isRead = n['read'] == true;
            final type = n['type']?.toString();
            final color = _typeColor(type);

            return Card(
              color: isRead ? null : color.withValues(alpha: 0.07),
              margin: const EdgeInsets.symmetric(vertical: 5),
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: () => _markRead(n),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Type icon
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.15),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(_typeIcon(type), color: color, size: 20),
                      ),

                      const SizedBox(width: 12),

                      // Text content
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              n['title']?.toString() ?? '',
                              style: TextStyle(
                                fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              n['message']?.toString() ?? '',
                              style: TextStyle(
                                fontSize: 13,
                                color: Colors.grey.shade600,
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(width: 8),

                      // Read indicator
                      Icon(
                        isRead ? Icons.check_circle : Icons.fiber_new,
                        color: isRead ? Colors.grey.shade400 : color,
                        size: 18,
                      ),
                    ],
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
