import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../services/api_service.dart';

class ProductDetailsScreen extends StatefulWidget {
  final int productId;
  final String productName;

  const ProductDetailsScreen({
    super.key,
    required this.productId,
    required this.productName,
  });

  @override
  State<ProductDetailsScreen> createState() =>
      _ProductDetailsScreenState();
}

class _ProductDetailsScreenState
    extends State<ProductDetailsScreen> {
  final ApiService _apiService =
      ApiService();

  bool _isLoading = true;

  Map<String, dynamic>? _product;

  List<dynamic> _transactions = [];

  List<dynamic> _recommendations = [];

  List<dynamic> _forecasts = [];

  @override
  void initState() {
    super.initState();

    _loadData();
  }

  // ===========================
  // SAFE CONVERTERS
  // ===========================

  double _toDouble(dynamic value) {
    if (value == null) return 0;

    if (value is num) {
      return value.toDouble();
    }

    return double.tryParse(
          value.toString(),
        ) ??
        0;
  }

  String _safe(dynamic value) {
    if (value == null) return '--';

    return value.toString();
  }

  // ===========================
  // LOAD DATA
  // ===========================

  Future<void> _loadData() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
        });
      }

      final results =
          await Future.wait([
        _apiService.getProduct(
          widget.productId,
        ),

        _apiService.getTransactions(
          productId:
              widget.productId,
        ),

        _apiService
            .getRecommendations(
          productId:
              widget.productId,
        ),

        _apiService
            .getProductForecasts(
          widget.productId,
        ),
      ]);

      if (!mounted) return;

      setState(() {
        _product =
            results[0]
                as Map<String, dynamic>?;

        _transactions =
            (results[1] as List?) ??
                [];

        _recommendations =
            (results[2] as List?) ??
                [];

        _forecasts =
            (results[3] as List?) ??
                [];

        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isLoading = false;
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

  // ===========================
  // FORECAST CHART
  // ===========================

  List<FlSpot> _buildForecastSpots() {
    if (_forecasts.isEmpty) {
      return [];
    }

    final sorted =
        List.from(_forecasts);

    sorted.sort(
      (a, b) => a[
              'forecast_date']
          .compareTo(
        b['forecast_date'],
      ),
    );

    return List.generate(
      sorted.length,
      (index) {
        return FlSpot(
          index.toDouble(),

          _toDouble(
            sorted[index][
                'predicted_demand'],
          ),
        );
      },
    );
  }

  // ===========================
  // KPI CARD
  // ===========================

  Widget _statCard(
    String title,
    String value,
    IconData icon,
  ) {
    return Card(
      elevation: 2,

      child: Padding(
        padding:
            const EdgeInsets.all(
          16,
        ),

        child: Column(
          children: [
            Icon(
              icon,

              color: const Color(
                0xFF2E7D32,
              ),
            ),

            const SizedBox(
              height: 8,
            ),

            Text(
              value,

              style:
                  const TextStyle(
                fontSize: 20,

                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 4,
            ),

            Text(title),
          ],
        ),
      ),
    );
  }

  // ===========================
  // BUILD
  // ===========================

  @override
  Widget build(
    BuildContext context,
  ) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(
          child:
              CircularProgressIndicator(),
        ),
      );
    }

    final product =
        _product ?? {};

    final spots =
        _buildForecastSpots();

    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.productName,
        ),
      ),

      body: RefreshIndicator(
        onRefresh: _loadData,

        child: ListView(
          padding:
              const EdgeInsets.all(
            16,
          ),

          children: [
            // =====================
            // PRODUCT CARD
            // =====================

            Hero(
              tag:
                  'product_${widget.productId}',

              child: Card(
                elevation: 3,

                child: Padding(
                  padding:
                      const EdgeInsets.all(
                    18,
                  ),

                  child: Column(
                    crossAxisAlignment:
                        CrossAxisAlignment
                            .start,

                    children: [
                      Text(
                        _safe(
                          product['name'],
                        ),

                        style:
                            const TextStyle(
                          fontSize: 24,

                          fontWeight:
                              FontWeight.bold,
                        ),
                      ),

                      const SizedBox(
                        height: 10,
                      ),

                      Text(
                        'Category: ${_safe(product['category'])}',
                      ),

                      Text(
                        'Price: KES ${_safe(product['unit_price'])}',
                      ),

                      Text(
                        'Unit: ${_safe(product['unit'])}',
                      ),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(
              height: 24,
            ),

            // =====================
            // FORECAST GRAPH
            // =====================

            const Text(
              'Forecast Trend',

              style: TextStyle(
                fontSize: 18,

                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            SizedBox(
              height: 240,

              child: spots.isEmpty
                  ? const Center(
                      child: Text(
                        'No forecast data',
                      ),
                    )

                  : LineChart(
                      LineChartData(
                        gridData:
                            const FlGridData(
                          show: true,
                        ),

                        titlesData:
                            const FlTitlesData(
                          show: false,
                        ),

                        borderData:
                            FlBorderData(
                          show: true,
                        ),

                        lineBarsData: [
                          LineChartBarData(
                            spots: spots,

                            isCurved:
                                true,

                            barWidth: 4,

                            color:
                                const Color(
                              0xFF2E7D32,
                            ),

                            dotData:
                                const FlDotData(
                              show: true,
                            ),
                          ),
                        ],
                      ),
                    ),
            ),

            const SizedBox(
              height: 24,
            ),

            // =====================
            // KPIs
            // =====================

            Row(
              children: [
                Expanded(
                  child: _statCard(
                    'Transactions',

                    _transactions.length
                        .toString(),

                    Icons.receipt_long,
                  ),
                ),

                const SizedBox(
                  width: 12,
                ),

                Expanded(
                  child: _statCard(
                    'Recommendations',

                    _recommendations
                        .length
                        .toString(),

                    Icons.lightbulb,
                  ),
                ),
              ],
            ),

            const SizedBox(
              height: 24,
            ),

            // =====================
            // TRANSACTIONS
            // =====================

            const Text(
              'Recent Transactions',

              style: TextStyle(
                fontSize: 18,

                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            if (_transactions
                .isEmpty)
              const Text(
                'No transactions',
              ),

            ..._transactions
                .take(5)
                .map(
              (t) {
                return Card(
                  child: ListTile(
                    leading:
                        const Icon(
                      Icons.receipt,
                    ),

                    title: Text(
                      'Qty: ${_safe(t['quantity'])}',
                    ),

                    subtitle: Text(
                      _safe(
                        t[
                            'transaction_date'],
                      ),
                    ),

                    trailing: Text(
                      'KES ${_safe(t['total_price'])}',

                      style:
                          const TextStyle(
                        color: Color(
                          0xFF2E7D32,
                        ),

                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),
                  ),
                );
              },
            ),

            const SizedBox(
              height: 24,
            ),

            // =====================
            // RECOMMENDATIONS
            // =====================

            const Text(
              'Recommendations',

              style: TextStyle(
                fontSize: 18,

                fontWeight:
                    FontWeight.bold,
              ),
            ),

            const SizedBox(
              height: 10,
            ),

            if (_recommendations
                .isEmpty)
              const Text(
                'No recommendations',
              ),

            ..._recommendations
                .map(
              (r) {
                final status =
                    _safe(
                  r['status'],
                );

                return Card(
                  child: ListTile(
                    leading:
                        const Icon(
                      Icons.lightbulb,
                    ),

                    title: Text(
                      'Qty: ${_safe(r['recommended_quantity'])}',
                    ),

                    subtitle: Text(
                      'Status: $status',
                    ),

                    trailing: Chip(
                      label:
                          Text(status),

                      backgroundColor:
                          status ==
                                  'approved'
                              ? Colors.green
                                  .withValues(
                                  alpha:
                                      0.2,
                                )

                              : status ==
                                      'pending'
                                  ? Colors.orange
                                      .withValues(
                                      alpha:
                                          0.2,
                                    )

                                  : Colors.blue
                                      .withValues(
                                      alpha:
                                          0.2,
                                    ),
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}