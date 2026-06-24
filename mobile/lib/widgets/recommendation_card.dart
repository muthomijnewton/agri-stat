import 'package:flutter/material.dart';

class RecommendationCard extends StatelessWidget {
  final int id;

  final String productName;

  final int recommendedQuantity;

  final String status;

  final VoidCallback? onApprove;

  final VoidCallback? onImplement;

  const RecommendationCard({
    super.key,

    required this.id,

    required this.productName,

    required this.recommendedQuantity,

    required this.status,

    this.onApprove,

    this.onImplement,
  });

  Color _statusColor() {
    switch (status.toLowerCase()) {
      case 'approved':
        return Colors.blue;

      case 'implemented':
        return Colors.green;

      case 'rejected':
        return Colors.red;

      default:
        return Colors.orange;
    }
  }

  IconData _statusIcon() {
    switch (status.toLowerCase()) {
      case 'approved':
        return Icons.check_circle;

      case 'implemented':
        return Icons.task_alt;

      case 'rejected':
        return Icons.cancel;

      default:
        return Icons.pending_actions;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark =
        Theme.of(context).brightness ==
            Brightness.dark;

    final isPending =
        status.toLowerCase() == 'pending';

    final isApproved =
        status.toLowerCase() == 'approved';

    return Card(
      margin: const EdgeInsets.symmetric(
        vertical: 8,
      ),

      child: Padding(
        padding: const EdgeInsets.all(
          16,
        ),

        child: Column(
          crossAxisAlignment:
              CrossAxisAlignment.start,

          children: [
            // ==================
            // HEADER
            // ==================

            Row(
              children: [
                Container(
                  width: 48,

                  height: 48,

                  decoration:
                      BoxDecoration(
                    color: _statusColor()
                        .withValues(
                      alpha: 0.15,
                    ),

                    borderRadius:
                        BorderRadius.circular(
                      12,
                    ),
                  ),

                  child: Icon(
                    _statusIcon(),

                    color:
                        _statusColor(),
                  ),
                ),

                const SizedBox(
                  width: 12,
                ),

                Expanded(
                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,

                    children: [
                      Text(
                        productName,

                        style:
                            const TextStyle(
                          fontSize: 16,

                          fontWeight:
                              FontWeight.bold,
                        ),
                      ),

                      Text(
                        'ID: $id',

                        style:
                            TextStyle(
                          color: isDark

                              ? Colors.grey[
                                  400]

                              : Colors.grey[
                                  600],
                        ),
                      ),
                    ],
                  ),
                ),

                Container(
                  padding:
                      const EdgeInsets.symmetric(
                    horizontal: 10,

                    vertical: 6,
                  ),

                  decoration:
                      BoxDecoration(
                    color: _statusColor()
                        .withValues(
                      alpha: 0.18,
                    ),

                    borderRadius:
                        BorderRadius.circular(
                      20,
                    ),
                  ),

                  child: Text(
                    status.toUpperCase(),

                    style: TextStyle(
                      color:
                          _statusColor(),

                      fontWeight:
                          FontWeight.bold,

                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 16,
            ),

            // ==================
            // BODY
            // ==================

            Text(
              'Recommended Quantity',

              style: TextStyle(
                color: isDark

                    ? Colors.grey[400]

                    : Colors.grey[600],
              ),
            ),

            const SizedBox(
              height: 6,
            ),

            Text(
              '$recommendedQuantity units',

              style:
                  const TextStyle(
                fontSize: 22,

                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 18,
            ),

            // ==================
            // ACTIONS
            // ==================

            if (isPending)
              SizedBox(
                width: double.infinity,

                child:
                    ElevatedButton.icon(
                  onPressed:
                      onApprove,

                  icon: const Icon(
                    Icons.check,
                  ),

                  label: const Text(
                    'Approve',
                  ),
                ),
              ),

            if (isApproved)
              SizedBox(
                width: double.infinity,

                child:
                    ElevatedButton.icon(
                  onPressed:
                      onImplement,

                  style:
                      ElevatedButton.styleFrom(
                    backgroundColor:
                        Colors.green,
                  ),

                  icon: const Icon(
                    Icons.task_alt,
                  ),

                  label: const Text(
                    'Implement',
                  ),
                ),
              ),

            if (!isPending &&
                !isApproved)
              Center(
                child: Text(
                  'No actions available',

                  style: TextStyle(
                    color: isDark

                        ? Colors.grey[
                            500]

                        : Colors.grey[
                            600],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}