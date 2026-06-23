import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/summary_chart.dart';
import '../utils/type_safety.dart'; // 👈 ADD THIS

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;

  Map<String, dynamic> _stats = {};
  List<dynamic> _summaryData = [];

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  /// ================= SMART INSIGHTS ENGINE =================
  Map<String, dynamic> _generateInsights(List<dynamic> data) {
    if (data.isEmpty) {
      return {
        "message": "No data available for insights",
        "top": null,
        "low": null,
      };
    }

    final sorted = [...data];

    sorted.sort((a, b) =>
        TypeSafety.toDouble(b['total'])
            .compareTo(TypeSafety.toDouble(a['total'])));

    final top = sorted.first;
    final low = sorted.last;

    final total = data.fold<double>(
      0,
      (sum, item) => sum + TypeSafety.toDouble(item['total']),
    );

    final topShare = total == 0
        ? 0
        : (TypeSafety.toDouble(top['total']) / total) * 100;

    String message;

    if (topShare > 60) {
      message =
          "High dependency on ${top['category']} (${topShare.toStringAsFixed(1)}%). Consider diversification.";
    } else if (topShare > 40) {
      message =
          "${top['category']} leads sales (${topShare.toStringAsFixed(1)}%). Balanced growth recommended.";
    } else {
      message = "Sales are well distributed across categories.";
    }

    return {
      "message": message,
      "top": top,
      "low": low,
    };
  }

  /// ================= DATA LOADING =================
  Future<void> _loadDashboardData() async {
    try {
      setState(() => _isLoading = true);

      final results = await Future.wait([
        _apiService.getProducts(),
        _apiService.getTransactions(),
        _apiService.getForecasts(),
        _apiService.getRecommendations(),
        _apiService.fetchSummary(),
      ]);

      final products = (results[0] as List?) ?? [];
      final transactions = (results[1] as List?) ?? [];
      final forecasts = (results[2] as List?) ?? [];
      final recommendations = (results[3] as List?) ?? [];
      final summary = (results[4] as List?) ?? [];

      final pendingRecs =
          recommendations.where((r) => r['status'] == 'pending').length;

      final totalRevenue = transactions.fold<double>(
        0.0,
        (sum, t) => sum + TypeSafety.toDouble(t['total_price']),
      );

      final avgTransaction =
          transactions.isNotEmpty ? totalRevenue / transactions.length : 0.0;

      setState(() {
        _summaryData = summary;

        _stats = {
          "totalProducts": products.length,
          "totalTransactions": transactions.length,
          "activeForecasts": forecasts.length,
          "pendingRecommendations": pendingRecs,
          "totalRevenue": totalRevenue,
          "avgTransaction": avgTransaction,
        };

        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Dashboard error: $e")),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final insights = _generateInsights(_summaryData);

    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            "Dashboard Overview",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 24),

          /// ================= STATS GRID =================
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              StatCard(
                title: "Products",
                value: "${_stats['totalProducts'] ?? 0}",
                icon: Icons.inventory_2,
                backgroundColor: const Color(0xFF2E7D32),
              ),
              StatCard(
                title: "Transactions",
                value: "${_stats['totalTransactions'] ?? 0}",
                icon: Icons.receipt_long,
                backgroundColor: const Color(0xFF1565C0),
              ),
              StatCard(
                title: "Revenue",
                value:
                    "KSH ${(TypeSafety.toDouble(_stats['totalRevenue'])).toStringAsFixed(0)}",
                icon: Icons.attach_money,
                backgroundColor: const Color(0xFF6A1B9A),
              ),
              StatCard(
                title: "Pending Alerts",
                value: "${_stats['pendingRecommendations'] ?? 0}",
                icon: Icons.warning_amber_rounded,
                backgroundColor: const Color(0xFFC62828),
              ),
            ],
          ),

          const SizedBox(height: 24),

          /// ================= CHART =================
          const Text(
            "Sales by Category",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 16),

          Container(
            height: 250,
            padding: const EdgeInsets.all(8),
            child: _summaryData.isEmpty
                ? const Center(child: Text("No summary data available"))
                : SummaryChart(data: _summaryData),
          ),

          const SizedBox(height: 24),

          /// ================= SMART INSIGHTS =================
          Card(
            color: const Color(0xFF1B5E20),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.insights, color: Colors.white),
                      SizedBox(width: 8),
                      Text(
                        "Smart Insights",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    insights['message'],
                    style: const TextStyle(color: Colors.white),
                  ),
                  const SizedBox(height: 12),
                  if (insights['top'] != null)
                    Text(
                      "Top Category: ${insights['top']['category']} "
                      "(${TypeSafety.toDouble(insights['top']['total']).toStringAsFixed(0)})",
                      style: const TextStyle(color: Colors.white70),
                    ),
                  if (insights['low'] != null)
                    Text(
                      "Lowest Category: ${insights['low']['category']} "
                      "(${TypeSafety.toDouble(insights['low']['total']).toStringAsFixed(0)})",
                      style: const TextStyle(color: Colors.white70),
                    ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          /// ================= QUICK ACTIONS =================
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.flash_on),
                      SizedBox(width: 8),
                      Text(
                        "Quick Actions",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _loadDashboardData,
                      icon: const Icon(Icons.refresh),
                      label: const Text("Refresh Dashboard"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2E7D32),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}