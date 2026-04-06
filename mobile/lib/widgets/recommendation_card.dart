import 'package:flutter/material.dart';

class RecommendationCard extends StatelessWidget {
  final int id;
  final String productName;
  final int recommendedQuantity;
  final String status;
  final VoidCallback? onApprove;
  final VoidCallback? onImplement;

  const RecommendationCard({
    Key? key,
    required this.id,
    required this.productName,
    required this.recommendedQuantity,
    required this.status,
    this.onApprove,
    this.onImplement,
  }) : super(key: key);

  Color _getStatusColor() {
    switch (status) {
      case 'pending':
        return Colors.orange;
      case 'approved':
        return Colors.blue;
      case 'implemented':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          border: Border(
            left: BorderSide(
              color: _getStatusColor(),
              width: 4,
            ),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
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
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: _getStatusColor().withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      status.toUpperCase(),
                      style: TextStyle(
                        color: _getStatusColor(),
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                'Recommended: $recommendedQuantity units',
                style: const TextStyle(fontSize: 14),
              ),
              const SizedBox(height: 12),
              if (status == 'pending' && onApprove != null)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: onApprove,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2E7D32),
                    ),
                    child: const Text('✓ Approve'),
                  ),
                ),
              if (status == 'approved' && onImplement != null)
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: onImplement,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                    child: const Text('✓ Implement'),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
