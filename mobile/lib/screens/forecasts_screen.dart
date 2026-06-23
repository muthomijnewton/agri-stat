import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../services/api_service.dart';

class ForecastsScreen extends StatefulWidget {
  const ForecastsScreen({super.key});

  @override
  State<ForecastsScreen> createState() => _ForecastsScreenState();
}

class _ForecastsScreenState extends State<ForecastsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  List<dynamic> _forecasts = [];

  int? _selectedProductId;

  int _toInt(dynamic value) {
    if (value == null) return 0;
    if (value is int) return value;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }

  double _toDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  @override
  void initState() {
    super.initState();
    _loadForecasts();
  }

  Future<void> _loadForecasts() async {
    try {
      setState(() => _isLoading = true);

      final forecasts = await _apiService.getForecasts();

      setState(() {
        _forecasts = forecasts;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading forecasts: $e')),
        );
      }
    }
  }

  List<dynamic> get _filteredForecasts {
    if (_selectedProductId == null) return _forecasts;
    return _forecasts
        .where((f) => _toInt(f['product_id']) == _selectedProductId)
        .toList();
  }

  List<FlSpot> _buildSpots() {
    final data = _filteredForecasts;

    if (data.isEmpty) return [];

    data.sort((a, b) =>
        a['forecast_date'].compareTo(b['forecast_date']));

    return List.generate(data.length, (index) {
      final item = data[index];
      return FlSpot(
        index.toDouble(),
        _toDouble(item['predicted_demand']),
      );
    });
  }

  List<int> _getUniqueProductIds() {
    return _forecasts
        .map((e) => _toInt(e['product_id']))
        .where((id) => id != 0)
        .toSet()
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    final spots = _buildSpots();

    return RefreshIndicator(
      onRefresh: _loadForecasts,
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          const Text(
            "Forecast Trends",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 12),

          // PRODUCT FILTER
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                ChoiceChip(
                  label: const Text("All Products"),
                  selected: _selectedProductId == null,
                  onSelected: (_) {
                    setState(() => _selectedProductId = null);
                  },
                ),
                const SizedBox(width: 8),
                ..._getUniqueProductIds().map((id) {
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text("Product $id"),
                      selected: _selectedProductId == id,
                      onSelected: (_) {
                        setState(() => _selectedProductId = id);
                      },
                    ),
                  );
                }),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // CHART
          SizedBox(
            height: 300,
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
                          dotData: const FlDotData(show: true),
                          color: const Color(0xFF2E7D32),
                        ),
                      ],
                    ),
                  ),
          ),

          const SizedBox(height: 20),

          const Text(
            "Forecast Details",
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 10),

          // LIST BELOW CHART
          ..._filteredForecasts.map((forecast) {
            return Card(
              child: ListTile(
                title: Text(
                  "Product ${forecast['product_id']}",
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  "Date: ${forecast['forecast_date']}",
                ),
                trailing: Text(
                  "${forecast['predicted_demand']} units",
                  style: const TextStyle(
                    color: Color(0xFF2E7D32),
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
