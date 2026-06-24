import 'package:flutter/material.dart';

import '../services/api_service.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() =>
      _TransactionsScreenState();
}

class _TransactionsScreenState
    extends State<TransactionsScreen> {
  final ApiService _apiService =
      ApiService();

  bool _isLoading = true;

  bool _hasError = false;

  List<dynamic> _transactions = [];

  List<dynamic> _filteredTransactions = [];

  String _search = '';

  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();

    _loadTransactions();
  }

  // ==========================
  // LOAD TRANSACTIONS
  // ==========================

  Future<void> _loadTransactions() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
          _hasError = false;
        });
      }

      final transactions =
          await _apiService.getTransactions();

      if (!mounted) return;

      setState(() {
        _transactions =
            transactions;

        _filteredTransactions =
            transactions;

        _lastUpdated =
            DateTime.now();

        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _hasError = true;

        _isLoading = false;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Error loading transactions: $e',
          ),
        ),
      );
    }
  }

  // ==========================
  // SEARCH
  // ==========================

  void _filterTransactions(
    String value,
  ) {
    _search = value;

    if (value.isEmpty) {
      setState(() {
        _filteredTransactions =
            _transactions;
      });

      return;
    }

    setState(() {
      _filteredTransactions =
          _transactions.where((t) {
        final id =
            (t['product_id'] ?? '')
                .toString()
                .toLowerCase();

        final date =
            (t['transaction_date'] ??
                    '')
                .toString()
                .toLowerCase();

        return id.contains(
              value.toLowerCase(),
            ) ||
            date.contains(
              value.toLowerCase(),
            );
      }).toList();
    });
  }

  // ==========================
  // HELPERS
  // ==========================

  double _toDouble(
    dynamic value,
  ) {
    if (value == null) {
      return 0;
    }

    return double.tryParse(
          value.toString(),
        ) ??
        0;
  }

  String _formatMoney(
    dynamic value,
  ) {
    return _toDouble(
      value,
    ).toStringAsFixed(0);
  }

  String _formatQuantity(
    dynamic value,
  ) {
    return _toDouble(
      value,
    ).toStringAsFixed(0);
  }

  double _totalRevenue() {
    return _filteredTransactions
        .fold<double>(
      0,
      (sum, t) =>
          sum +
          _toDouble(
            t['total_price'],
          ),
    );
  }

  int _todayTransactions() {
    final today =
        DateTime.now();

    return _filteredTransactions
        .where((t) {
      final date =
          t['transaction_date']
                  ?.toString() ??
              '';

      return date.contains(
        '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}',
      );
    }).length;
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(
    BuildContext context,
  ) {
    if (_isLoading) {
      return const Center(
        child:
            CircularProgressIndicator(),
      );
    }

    if (_hasError) {
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
              'Unable to load transactions',
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  _loadTransactions,

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
          _loadTransactions,

      child: Column(
        children: [
          // ==================
          // SEARCH
          // ==================

          Padding(
            padding:
                const EdgeInsets.all(
              12,
            ),

            child: TextField(
              onChanged:
                  _filterTransactions,

              decoration:
                  InputDecoration(
                prefixIcon:
                    const Icon(
                  Icons.search,
                ),

                hintText:
                    'Search transactions',

                border:
                    OutlineInputBorder(
                  borderRadius:
                      BorderRadius.circular(
                    12,
                  ),
                ),
              ),
            ),
          ),

          // ==================
          // STATS
          // ==================

          Padding(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 12,
            ),

            child: Row(
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
                            'Transactions',
                          ),

                          Text(
                            '${_filteredTransactions.length}',

                            style:
                                const TextStyle(
                              fontSize:
                                  22,

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
                            'Revenue',
                          ),

                          Text(
                            'KSH ${_totalRevenue().toStringAsFixed(0)}',

                            style:
                                const TextStyle(
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
          ),

          Padding(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 16,
            ),

            child: Row(
              mainAxisAlignment:
                  MainAxisAlignment
                      .spaceBetween,

              children: [
                Text(
                  'Today: ${_todayTransactions()}',
                ),

                Text(
                  _lastUpdated ==
                          null
                      ? ''

                      : 'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
                ),
              ],
            ),
          ),

          const SizedBox(
            height: 10,
          ),

          // ==================
          // EMPTY STATE
          // ==================

          Expanded(
            child:
                _filteredTransactions
                        .isEmpty

                    ? Center(
                        child: Column(
                          mainAxisAlignment:
                              MainAxisAlignment
                                  .center,

                          children: [
                            const Icon(
                              Icons.receipt_long_outlined,

                              size: 70,
                            ),

                            const SizedBox(
                              height:
                                  16,
                            ),

                            Text(
                              _search
                                      .isEmpty
                                  ? 'No transactions available'

                                  : 'No matching transactions',
                            ),
                          ],
                        ),
                      )

                    // ==================
                    // LIST
                    // ==================

                    : ListView.builder(
                        padding:
                            const EdgeInsets.all(
                          12,
                        ),

                        itemCount:
                            _filteredTransactions
                                .length,

                        itemBuilder:
                            (
                          context,
                          index,
                        ) {
                          final transaction =
                              _filteredTransactions[
                                      index]
                                  as Map<String,
                                      dynamic>;

                          final productId =
                              transaction['product_id']
                                      ?.toString() ??
                                  'Unknown';

                          final quantity =
                              _formatQuantity(
                            transaction[
                                'quantity'],
                          );

                          final date =
                              transaction['transaction_date']
                                      ?.toString() ??
                                  'No date';

                          final totalPrice =
                              _formatMoney(
                            transaction[
                                'total_price'],
                          );

                          return Card(
                            margin:
                                const EdgeInsets.symmetric(
                              vertical:
                                  8,
                            ),

                            child:
                                ListTile(
                              leading:
                                  Container(
                                width:
                                    45,

                                height:
                                    45,

                                decoration:
                                    BoxDecoration(
                                  color:
                                      const Color(
                                    0xFF2E7D32,
                                  ).withValues(
                                    alpha:
                                        0.15,
                                  ),

                                  borderRadius:
                                      BorderRadius.circular(
                                    8,
                                  ),
                                ),

                                child:
                                    const Icon(
                                  Icons.receipt_long,

                                  color:
                                      Color(
                                    0xFF2E7D32,
                                  ),
                                ),
                              ),

                              title:
                                  Text(
                                'Product ID: $productId',

                                style:
                                    const TextStyle(
                                  fontWeight:
                                      FontWeight.bold,
                                ),
                              ),

                              subtitle:
                                  Text(
                                'Quantity: $quantity\nDate: $date',
                              ),

                              trailing:
                                  Text(
                                'KSH $totalPrice',

                                style:
                                    const TextStyle(
                                  fontWeight:
                                      FontWeight.bold,

                                  color:
                                      Color(
                                    0xFF2E7D32,
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}