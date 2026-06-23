import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/stat_card.dart';
import '../widgets/summary_chart.dart'; // Import your new chart widget

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  Map<String, dynamic> _stats = {};
  List<dynamic> _summaryData = []; // New state variable for chart data

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    try {
      setState(() => _isLoading = true);

      // Fetch all data
      final products = await _apiService.getProducts();
      final transactions = await _apiService.getTransactions();
      final forecasts = await _apiService.getForecasts();
      final recommendations = await _apiService.getRecommendations();
      final summary = await _apiService.fetchSummary(); // Fetching the new endpoint

      final pendingRecs = (recommendations).where((r) => r['status'] == 'pending').length;

      setState(() {
        _summaryData = summary; // Storing the data
        _stats = {
          'totalProducts': products.length,
          'totalTransactions': transactions.length,
          'activeForecasts': forecasts.length,
          'pendingRecommendations': pendingRecs,
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return RefreshIndicator(
      onRefresh: _loadDashboardData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Dashboard Overview', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              StatCard(title: 'Total Products', value: '${_stats['totalProducts'] ?? 0}', icon: Icons.inventory, backgroundColor: const Color(0xFF2E7D32)),
              StatCard(title: 'Transactions', value: '${_stats['totalTransactions'] ?? 0}', icon: Icons.receipt, backgroundColor: const Color(0xFF1565C0)),
              StatCard(title: 'Forecasts', value: '${_stats['activeForecasts'] ?? 0}', icon: Icons.trending_up, backgroundColor: const Color(0xFFF57C00)),
              StatCard(title: 'Pending', value: '${_stats['pendingRecommendations'] ?? 0}', icon: Icons.warning, backgroundColor: const Color(0xFFC62828)),
            ],
          ),
          const SizedBox(height: 24),
          // --- Added Chart Section ---
          const Text('Sales by Category', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Container(
            height: 250,
            padding: const EdgeInsets.all(8),
            child: _summaryData.isEmpty 
                ? const Center(child: Text("No summary data available"))
                : SummaryChart(data: _summaryData),
          ),
          const SizedBox(height: 24),
          // --- End Chart Section ---
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Quick Actions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _loadDashboardData,
                      icon: const Icon(Icons.refresh),
                      label: const Text('Refresh Data'),
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32)),
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