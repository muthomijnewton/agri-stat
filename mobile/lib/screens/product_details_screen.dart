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
  State<ProductDetailsScreen> createState() => _ProductDetailsScreenState();
}

class _ProductDetailsScreenState extends State<ProductDetailsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;

  Map<String, dynamic>? _product;
  List<dynamic> _transactions = [];
  List<dynamic> _recommendations = [];
  List<dynamic> _forecasts = []; // ✅ ADDED

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      setState(() => _isLoading = true);

      final product = await _apiService.getProduct(widget.productId);
      final transactions = await _apiService.getTransactions(
        productId: widget.productId,
      );
      final recommendations = await _apiService.getRecommendations(
        productId: widget.productId,
      );
      final forecasts = await _apiService.getProductForecasts(widget.productId); // ✅ ADDED

      setState(() {
        _product = product;
        _transactions = transactions;
        _recommendations = recommendations;
        _forecasts = forecasts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading product: $e')),
        );
      }
    }
  }

  // ================= FORECAST CHART =================
  List<FlSpot> _buildForecastSpots() {
    if (_forecasts.isEmpty) return [];

    final sorted = List.from(_forecasts)
      ..sort((a, b) => a['forecast_date'].compareTo(b['forecast_date']));

    return List.generate(sorted.length, (index) {
      return FlSpot(
        index.toDouble(),
        (sorted[index]['predicted_demand'] as num).toDouble(),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final product = _product ?? {};
    final spots = _buildForecastSpots();

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.productName),
        backgroundColor: const Color(0xFF2E7D32),
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [

            // ================= PRODUCT INFO =================
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product['name'] ?? widget.productName,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(product['category'] ?? 'Uncategorized'),
                    const SizedBox(height: 8),
                    Text("Price: ${product['unit_price'] ?? 'N/A'}"),
                    Text("Unit: ${product['unit'] ?? 'N/A'}"),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // ================= FORECAST GRAPH (NEW) =================
            const Text(
              "Forecast Trend",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            SizedBox(
              height: 220,
              child: spots.isEmpty
                  ? const Center(child: Text("No forecast data"))
                  : LineChart(
                      LineChartData(
                        gridData: const FlGridData(show: true),
                        titlesData: const FlTitlesData(show: false),
                        borderData: FlBorderData(show: true),
                        lineBarsData: [
                          LineChartBarData(
                            spots: spots,
                            isCurved: true,
                            barWidth: 3,
                            color: const Color(0xFF2E7D32),
                            dotData: const FlDotData(show: true),
                          ),
                        ],
                      ),
                    ),
            ),

            const SizedBox(height: 16),

            // ================= STATS =================
            Row(
              children: [
                Expanded(
                  child: _statCard(
                    "Transactions",
                    _transactions.length.toString(),
                    Icons.receipt,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _statCard(
                    "Recommendations",
                    _recommendations.length.toString(),
                    Icons.recommend,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // ================= TRANSACTIONS =================
            const Text(
              "Recent Transactions",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            if (_transactions.isEmpty)
              const Text("No transactions for this product")
            else
              ..._transactions.take(5).map((t) {
                return Card(
                  child: ListTile(
                    title: Text("Qty: ${t['quantity']}"),
                    subtitle: Text(t['transaction_date'] ?? ''),
                    trailing: Text(
                      "${t['total_price']}",
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2E7D32),
                      ),
                    ),
                  ),
                );
              }),

            const SizedBox(height: 20),

            // ================= RECOMMENDATIONS =================
            const Text(
              "Recommendations",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            if (_recommendations.isEmpty)
              const Text("No recommendations for this product")
            else
              ..._recommendations.map((r) {
                final status = r['status'] ?? 'pending';

                return Card(
                  child: ListTile(
                    title: Text("Qty: ${r['recommended_quantity']}"),
                    subtitle: Text("Status: $status"),
                    trailing: Chip(
                      label: Text(status),
                      backgroundColor: status == "approved"
                          ? Colors.green.withValues(alpha: 0.2)
                          : status == "pending"
                              ? Colors.orange.withValues(alpha: 0.2)
                              : Colors.blue.withValues(alpha: 0.2),
                    ),
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }

  Widget _statCard(String title, String value, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: const Color(0xFF2E7D32)),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(title),
          ],
        ),
      ),
    );
  }
}