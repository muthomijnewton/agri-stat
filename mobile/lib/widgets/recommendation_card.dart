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

  @override
  Widget build(BuildContext context) {
    final isPending = status.toLowerCase() == 'pending';
    final isApproved = status.toLowerCase() == 'approved';

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    productName,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _statusColor().withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    status.toUpperCase(),
                    style: TextStyle(
                      color: _statusColor(),
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 10),

            Text(
              "Recommended Quantity: $recommendedQuantity",
              style: const TextStyle(fontSize: 14),
            ),

            const SizedBox(height: 12),

            // ACTIONS
            Row(
              children: [
                if (isPending)
                  Expanded(
                    child: ElevatedButton(
                      onPressed: onApprove,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue,
                      ),
                      child: const Text("Approve"),
                    ),
                  ),

                if (isPending) const SizedBox(width: 10),

                if (isApproved)
                  Expanded(
                    child: ElevatedButton(
                      onPressed: onImplement,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                      ),
                      child: const Text("Implement"),
                    ),
                  ),

                if (!isPending && !isApproved)
                  const Expanded(
                    child: SizedBox(),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
