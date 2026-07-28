import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../services/api_service.dart';
import '../utils/type_safety.dart';

class ForecastsScreen extends StatefulWidget {
  const ForecastsScreen({super.key});

  @override
  State<ForecastsScreen> createState() => _ForecastsScreenState();
}

class _ForecastsScreenState extends State<ForecastsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  bool _hasError = false;

  List<dynamic> _forecasts = [];

  /// id → name map built from GET /products
  Map<int, String> _productNames = {};

  int? _selectedProductId;
  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();
    _load();
  }

  // ==========================
  // LOAD DATA
  // ==========================

  Future<void> _load() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
          _hasError = false;
        });
      }

      // Fetch forecasts and products in parallel
      final results = await Future.wait([
        _apiService.getForecasts(),
        _apiService.getProducts(),
      ]);

      final forecasts = results[0] as List;
      final prods = results[1] as List;

      // Build id → name lookup
      final names = <int, String>{
        for (final p in prods)
          if (p['id'] != null)
            TypeSafety.toInt(p['id']): p['name']?.toString() ?? 'Product ${p['id']}',
      };

      if (!mounted) return;

      setState(() {
        _forecasts = forecasts;
        _productNames = names;
        _lastUpdated = DateTime.now();
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _hasError = true;
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading forecasts: $e')),
      );
    }
  }

  // ==========================
  // HELPERS
  // ==========================

  String _productName(dynamic rawId) {
    if (rawId == null) return 'Unknown';
    final id = TypeSafety.toInt(rawId);
    return _productNames[id] ?? 'Product $id';
  }

  // ==========================
  // FILTER
  // ==========================

  List<dynamic> get _filtered {
    if (_selectedProductId == null) return _forecasts;
    return _forecasts
        .where((f) => TypeSafety.toInt(f['product_id']) == _selectedProductId)
        .toList();
  }

  /// Unique product IDs present in the forecast list, sorted.
  List<int> _uniqueProductIds() {
    return _forecasts
        .map((f) => TypeSafety.toInt(f['product_id']))
        .where((id) => id != 0)
        .toSet()
        .toList()
      ..sort();
  }

  // ==========================
  // CHART DATA
  // ==========================

  List<FlSpot> _buildSpots() {
    final data = [..._filtered]
      ..sort((a, b) =>
          (a['forecast_date'] ?? '').toString().compareTo(
                (b['forecast_date'] ?? '').toString(),
              ));

    return List.generate(
      data.length,
      (i) => FlSpot(i.toDouble(), TypeSafety.toDouble(data[i]['predicted_demand'])),
    );
  }

  // ==========================
  // ANALYTICS
  // ==========================

  double _averageDemand() {
    if (_filtered.isEmpty) return 0;
    final total = _filtered.fold<double>(
      0,
      (sum, f) => sum + TypeSafety.toDouble(f['predicted_demand']),
    );
    return total / _filtered.length;
  }

  double _highestDemand() {
    return _filtered.fold<double>(
      0,
      (max, f) {
        final v = TypeSafety.toDouble(f['predicted_demand']);
        return v > max ? v : max;
      },
    );
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_hasError) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 70),
            const SizedBox(height: 16),
            const Text('Unable to load forecasts'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }

    final spots = _buildSpots();
    final productIds = _uniqueProductIds();

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          const Text(
            'Forecast Trends',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 12),

          // ── Product filter chips ──
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                ChoiceChip(
                  label: const Text('All Products'),
                  selected: _selectedProductId == null,
                  onSelected: (_) => setState(() => _selectedProductId = null),
                ),
                const SizedBox(width: 8),
                ...productIds.map(
                  (id) => Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(_productNames[id] ?? 'Product $id'),
                      selected: _selectedProductId == id,
                      onSelected: (_) => setState(() => _selectedProductId = id),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Stats row ──
          Row(
            children: [
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      children: [
                        const Text('Average'),
                        Text(_averageDemand().toStringAsFixed(0)),
                      ],
                    ),
                  ),
                ),
              ),
              Expanded(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      children: [
                        const Text('Highest'),
                        Text(_highestDemand().toStringAsFixed(0)),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          if (_lastUpdated != null)
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
              ),
            ),

          const SizedBox(height: 20),

          // ── Line chart ──
          SizedBox(
            height: 300,
            child: spots.isEmpty
                ? const Center(child: Text('No forecast data'))
                : LineChart(
                    LineChartData(
                      gridData: const FlGridData(show: true),
                      titlesData: const FlTitlesData(show: false),
                      borderData: FlBorderData(show: true),
                      lineBarsData: [
                        LineChartBarData(
                          spots: spots,
                          isCurved: true,
                          barWidth: 4,
                          color: const Color(0xFF2E7D32),
                          dotData: const FlDotData(show: true),
                        ),
                      ],
                    ),
                  ),
          ),

          const SizedBox(height: 20),

          const Text(
            'Forecast Details',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 12),

          if (_filtered.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(30),
                child: Text('No forecasts available'),
              ),
            ),

          // ── Detail cards ──
          ..._filtered.map((forecast) {
            final name = _productName(forecast['product_id']);
            return Card(
              child: ListTile(
                leading: const Icon(Icons.show_chart, color: Color(0xFF2E7D32)),
                title: Text(name),
                subtitle: Text('Date: ${forecast['forecast_date']}'),
                trailing: Text(
                  '${TypeSafety.toDouble(forecast['predicted_demand']).toStringAsFixed(0)} units',
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
