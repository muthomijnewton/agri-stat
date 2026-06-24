import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/summary_chart.dart';
import '../utils/type_safety.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  bool _hasError = false;

  Map<String, dynamic> _stats = {};

  List<dynamic> _summaryData = [];

  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  // ==========================
  // SMART INSIGHTS ENGINE
  // ==========================

  Map<String, dynamic> _generateInsights(
    List<dynamic> data,
  ) {
    if (data.isEmpty) {
      return {
        "message": "No data available yet.",
        "top": null,
        "low": null,
      };
    }

    final sorted = [...data];

    sorted.sort(
      (a, b) => TypeSafety.toDouble(
        b['total'],
      ).compareTo(
        TypeSafety.toDouble(a['total']),
      ),
    );

    final top = sorted.first;

    final low = sorted.last;

    final total = data.fold<double>(
      0,
      (sum, item) =>
          sum + TypeSafety.toDouble(item['total']),
    );

    final topShare = total == 0
        ? 0
        : (TypeSafety.toDouble(
                  top['total'],
                ) /
                total) *
            100;

    String message;

    if (topShare > 60) {
      message =
          "High dependency on ${top['category']}. Consider diversification.";
    } else if (topShare > 40) {
      message =
          "${top['category']} is performing strongly.";
    } else {
      message =
          "Sales are well distributed.";
    }

    return {
      "message": message,
      "top": top,
      "low": low,
    };
  }

  // ==========================
  // LOAD DASHBOARD
  // ==========================

  Future<void> _loadDashboardData() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
          _hasError = false;
        });
      }

      final results = await Future.wait([
        _apiService.getProducts(),

        _apiService.getTransactions(),

        _apiService.getForecasts(),

        _apiService.getRecommendations(),

        _apiService.fetchSummary(),
      ]);

      final products = results[0] as List? ?? [];

      final transactions =
          results[1] as List? ?? [];

      final forecasts =
          results[2] as List? ?? [];

      final recommendations =
          results[3] as List? ?? [];

      final summary =
          results[4] as List? ?? [];

      final pendingRecs =
          recommendations.where(
            (r) =>
                r['status'] == 'pending',
          ).length;

      final totalRevenue =
          transactions.fold<double>(
        0,
        (sum, item) =>
            sum +
            TypeSafety.toDouble(
              item['total_price'],
            ),
      );

      final avgTransaction =
          transactions.isEmpty
              ? 0
              : totalRevenue /
                  transactions.length;

      if (!mounted) return;

      setState(() {
        _summaryData = summary;

        _stats = {
          "totalProducts":
              products.length,

          "totalTransactions":
              transactions.length,

          "activeForecasts":
              forecasts.length,

          "pendingRecommendations":
              pendingRecs,

          "totalRevenue":
              totalRevenue,

          "avgTransaction":
              avgTransaction,
        };

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
            "Dashboard error: $e",
          ),
        ),
      );
    }
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
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
              MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 70,
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              "Unable to load dashboard",
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  _loadDashboardData,

              child:
                  const Text("Retry"),
            ),
          ],
        ),
      );
    }

    final insights =
        _generateInsights(
      _summaryData,
    );

    return RefreshIndicator(
      onRefresh:
          _loadDashboardData,

      child: ListView(
        padding:
            const EdgeInsets.all(16),

        children: [
          const Text(
            "Dashboard Overview",

            style: TextStyle(
              fontSize: 24,
              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 8,
          ),

          Text(
            _lastUpdated == null
                ? ""
                : "Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}",
          ),

          const SizedBox(
            height: 24,
          ),

          // ==================
          // STATS GRID
          // ==================

          GridView.count(
            crossAxisCount: 2,

            crossAxisSpacing: 12,

            mainAxisSpacing: 12,

            shrinkWrap: true,

            physics:
                const NeverScrollableScrollPhysics(),

            children: [
              StatCard(
                title: "Products",

                value:
                    "${_stats['totalProducts'] ?? 0}",

                icon:
                    Icons.inventory_2,

                backgroundColor:
                    const Color(
                  0xFF2E7D32,
                ),
              ),

              StatCard(
                title:
                    "Transactions",

                value:
                    "${_stats['totalTransactions'] ?? 0}",

                icon: Icons
                    .receipt_long,

                backgroundColor:
                    const Color(
                  0xFF1565C0,
                ),
              ),

              StatCard(
                title: "Revenue",

                value:
                    "KSH ${TypeSafety.toDouble(_stats['totalRevenue']).toStringAsFixed(0)}",

                icon: Icons
                    .attach_money,

                backgroundColor:
                    const Color(
                  0xFF6A1B9A,
                ),
              ),

              StatCard(
                title:
                    "Alerts",

                value:
                    "${_stats['pendingRecommendations'] ?? 0}",

                icon: Icons
                    .warning_amber_rounded,

                backgroundColor:
                    const Color(
                  0xFFC62828,
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 24,
          ),

          // ==================
          // CHART
          // ==================

          const Text(
            "Sales by Category",

            style: TextStyle(
              fontSize: 18,
              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 16,
          ),

          Container(
            height: 250,

            padding:
                const EdgeInsets.all(8),

            child:
                _summaryData.isEmpty
                    ? const Center(
                        child: Text(
                          "No summary data available",
                        ),
                      )
                    : SummaryChart(
                        data:
                            _summaryData,
                      ),
          ),

          const SizedBox(
            height: 24,
          ),

          // ==================
          // INSIGHTS
          // ==================

          Card(
            color:
                const Color(
              0xFF1B5E20,
            ),

            child: Padding(
              padding:
                  const EdgeInsets.all(
                16,
              ),

              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment
                        .start,

                children: [
                  const Text(
                    "Smart Insights",

                    style: TextStyle(
                      color:
                          Colors.white,

                      fontSize: 18,

                      fontWeight:
                          FontWeight
                              .bold,
                    ),
                  ),

                  const SizedBox(
                    height: 12,
                  ),

                  Text(
                    insights[
                        'message'],

                    style:
                        const TextStyle(
                      color:
                          Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(
            height: 24,
          ),

          ElevatedButton.icon(
            onPressed:
                _loadDashboardData,

            icon: const Icon(
              Icons.refresh,
            ),

            label: const Text(
              "Refresh Dashboard",
            ),
          ),
        ],
      ),
    );
  }
}