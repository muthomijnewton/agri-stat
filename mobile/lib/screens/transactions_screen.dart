import 'package:flutter/material.dart';

import '../services/api_service.dart';
import 'add_transaction_screen.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  bool _hasError = false;

  List<dynamic> _transactions = [];
  List<dynamic> _products = [];
  List<dynamic> _filtered = [];

  String _search = '';
  String _typeFilter = 'all'; // 'all' | 'sale' | 'purchase'

  DateTime? _lastUpdated;

  // Build a quick id->name map from the product list
  Map<int, String> get _productNames {
    return {
      for (final p in _products)
        if (p['id'] != null) (p['id'] as int): (p['name']?.toString() ?? 'Product ${p['id']}'),
    };
  }

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
      if (mounted) setState(() { _isLoading = true; _hasError = false; });

      final results = await Future.wait([
        _apiService.getTransactions(limit: 200),
        _apiService.getProducts(),
      ]);

      if (!mounted) return;

      final txns = results[0] as List;
      final prods = results[1] as List;

      setState(() {
        _transactions = txns;
        _products = prods;
        _lastUpdated = DateTime.now();
        _isLoading = false;
      });

      _applyFilter();
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
    }
  }

  // ==========================
  // FILTER
  // ==========================

  void _applyFilter() {
    List<dynamic> result = _transactions;

    if (_typeFilter != 'all') {
      result = result.where((t) => t['transaction_type'] == _typeFilter).toList();
    }

    if (_search.isNotEmpty) {
      final q = _search.toLowerCase();
      result = result.where((t) {
        final id = t['product_id'];
        final name = id != null ? (_productNames[id as int] ?? '').toLowerCase() : '';
        final date = (t['transaction_date'] ?? '').toString().toLowerCase();
        return name.contains(q) || date.contains(q);
      }).toList();
    }

    setState(() => _filtered = result);
  }

  void _onSearch(String value) {
    _search = value;
    _applyFilter();
  }

  void _onTypeFilter(String value) {
    _typeFilter = value;
    _applyFilter();
  }

  // ==========================
  // OPEN ADD SCREEN
  // ==========================

  Future<void> _openAddTransaction() async {
    final result = await Navigator.push<bool>(
      context,
      MaterialPageRoute(builder: (_) => const AddTransactionScreen()),
    );
    if (result == true) _load(); // refresh after successful add
  }

  // ==========================
  // HELPERS
  // ==========================

  double _toDouble(dynamic v) => double.tryParse(v?.toString() ?? '') ?? 0;

  double get _totalRevenue =>
      _filtered.fold(0, (sum, t) => sum + _toDouble(t['total_price']));

  String _productName(dynamic id) {
    if (id == null) return 'Unknown';
    return _productNames[id as int] ?? 'Product $id';
  }

  Color _typeColor(String? type) =>
      type == 'purchase' ? Colors.blue.shade700 : Colors.green.shade700;

  Color _typeBgColor(String? type) =>
      type == 'purchase' ? Colors.blue.shade50 : Colors.green.shade50;

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    if (_hasError) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 60),
            const SizedBox(height: 16),
            const Text('Unable to load transactions'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: Column(
          children: [
            // ── Search bar ──
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 6),
              child: TextField(
                onChanged: _onSearch,
                decoration: InputDecoration(
                  prefixIcon: const Icon(Icons.search),
                  hintText: 'Search by product or date',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                ),
              ),
            ),

            // ── Type filter chips ──
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              child: Row(
                children: [
                  for (final opt in [
                    ('all', 'All'),
                    ('sale', 'Sales'),
                    ('purchase', 'Purchases'),
                  ])
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(opt.$2),
                        selected: _typeFilter == opt.$1,
                        onSelected: (_) => _onTypeFilter(opt.$1),
                      ),
                    ),
                ],
              ),
            ),

            // ── Summary strip ──
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              child: Row(
                children: [
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Transactions', style: TextStyle(fontSize: 12)),
                            Text(
                              '${_filtered.length}',
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Revenue', style: TextStyle(fontSize: 12)),
                            Text(
                              'KES ${_totalRevenue.toStringAsFixed(0)}',
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            if (_lastUpdated != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
                child: Align(
                  alignment: Alignment.centerRight,
                  child: Text(
                    'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
                    style: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                  ),
                ),
              ),

            // ── List ──
            Expanded(
              child: _filtered.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.receipt_long_outlined, size: 60, color: Colors.grey.shade400),
                          const SizedBox(height: 16),
                          Text(
                            _search.isEmpty && _typeFilter == 'all'
                                ? 'No transactions yet.\nTap + to record one.'
                                : 'No matching transactions.',
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.fromLTRB(12, 4, 12, 80),
                      itemCount: _filtered.length,
                      itemBuilder: (context, index) {
                        final t = _filtered[index] as Map<String, dynamic>;
                        final type = t['transaction_type']?.toString();
                        final name = _productName(t['product_id']);

                        return Card(
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                            child: Row(
                              children: [
                                // Icon
                                Container(
                                  width: 42,
                                  height: 42,
                                  decoration: BoxDecoration(
                                    color: _typeBgColor(type),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Icon(
                                    type == 'purchase' ? Icons.arrow_downward : Icons.arrow_upward,
                                    color: _typeColor(type),
                                    size: 20,
                                  ),
                                ),
                                const SizedBox(width: 12),
                                // Details
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        name,
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          // Type badge
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                            decoration: BoxDecoration(
                                              color: _typeBgColor(type),
                                              borderRadius: BorderRadius.circular(4),
                                            ),
                                            child: Text(
                                              type == 'purchase' ? 'Purchase' : 'Sale',
                                              style: TextStyle(
                                                fontSize: 11,
                                                fontWeight: FontWeight.w600,
                                                color: _typeColor(type),
                                              ),
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            'Qty: ${t['quantity']}',
                                            style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                                          ),
                                          const SizedBox(width: 8),
                                          Text(
                                            t['transaction_date']?.toString() ?? '',
                                            style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                // Total
                                Text(
                                  'KES ${_toDouble(t['total_price']).toStringAsFixed(0)}',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: _typeColor(type),
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
      // ── FAB ──
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openAddTransaction,
        icon: const Icon(Icons.add),
        label: const Text('Record'),
      ),
    );
  }
}
