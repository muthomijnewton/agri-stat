import 'package:flutter/material.dart';
import '../services/api_service.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  List<dynamic> _transactions = [];

  @override
  void initState() {
    super.initState();
    _loadTransactions();
  }

  Future<void> _loadTransactions() async {
    try {
      setState(() => _isLoading = true);

      final transactions = await _apiService.getTransactions();

      setState(() {
        _transactions = (transactions as List?) ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading transactions: $e'),
          ),
        );
      }
    }
  }

  /// ================= SAFE HELPERS =================

  double _toDouble(dynamic value) {
    if (value == null) return 0.0;

    return double.tryParse(value.toString()) ?? 0.0;
  }

  String _formatMoney(dynamic value) {
    return _toDouble(value).toStringAsFixed(0);
  }

  String _formatQuantity(dynamic value) {
    return _toDouble(value).toStringAsFixed(0);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_transactions.isEmpty) {
      return const Center(
        child: Text(
          'No transactions found',
          style: TextStyle(fontSize: 16),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadTransactions,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _transactions.length,
        itemBuilder: (context, index) {
          final transaction =
              (_transactions[index] as Map<String, dynamic>? ?? {});

          final productId =
              transaction['product_id']?.toString() ?? 'Unknown';

          final quantity =
              _formatQuantity(transaction['quantity']);

          final date =
              transaction['transaction_date']?.toString() ?? 'No date';

          final totalPrice =
              _formatMoney(transaction['total_price']);

          return Card(
            margin: const EdgeInsets.symmetric(
              vertical: 8,
            ),
            elevation: 2,
            child: ListTile(
              leading: Container(
                width: 45,
                height: 45,
                decoration: BoxDecoration(
                  color: const Color(
                    0xFF2E7D32,
                  ).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.receipt_long,
                  color: Color(0xFF2E7D32),
                ),
              ),

              title: Text(
                'Product ID: $productId',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),

              subtitle: Padding(
                padding: const EdgeInsets.only(
                  top: 4,
                ),
                child: Text(
                  'Quantity: $quantity\nDate: $date',
                  style: TextStyle(
                    color: Colors.grey[700],
                    height: 1.4,
                  ),
                ),
              ),

              trailing: Column(
                mainAxisAlignment:
                    MainAxisAlignment.center,

                crossAxisAlignment:
                    CrossAxisAlignment.end,

                children: [
                  Text(
                    'KSH $totalPrice',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2E7D32),
                    ),
                  ),

                  const SizedBox(height: 4),

                  const Icon(
                    Icons.arrow_forward_ios,
                    size: 14,
                    color: Colors.grey,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}