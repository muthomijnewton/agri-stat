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
  final ApiService _api = ApiService();

  bool _isLoading = true;
  bool _hasError = false;
  bool _generating = false;

  List<dynamic> _forecasts = [];
  Map<int, String> _productNames = {};
  List<dynamic> _products = []; // full product list for the generate picker

  int? _selectedProductId;
  DateTime? _lastUpdated;

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
        _api.getForecasts(),
        _api.getProducts(),
      ]);

      final forecasts = results[0] as List;
      final prods = results[1] as List;

      final names = <int, String>{
        for (final p in prods)
          if (p['id'] != null)
            TypeSafety.toInt(p['id']): p['name']?.toString() ?? 'Product ${p['id']}',
      };

      if (!mounted) return;
      setState(() {
        _forecasts = forecasts;
        _products = prods;
        _productNames = names;
        _lastUpdated = DateTime.now();
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading forecasts: $e')),
      );
    }
  }

  // ==========================
  // GENERATE
  // ==========================

  /// Opens a bottom sheet to choose: single product or all products.
  Future<void> _openGenerateSheet() async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _GenerateForecastSheet(
        products: _products,
        productNames: _productNames,
        onGenerate: (productId) async {
          Navigator.pop(context);
          await _runGenerate(productId);
        },
        onGenerateAll: () async {
          Navigator.pop(context);
          await _runGenerateAll();
        },
      ),
    );
  }

  Future<void> _runGenerate(int productId) async {
    setState(() => _generating = true);
    try {
      final result = await _api.generateForecast(productId);
      if (!mounted) return;
      final periods = TypeSafety.toInt(result['periods_generated']);
      final name = _productNames[productId] ?? 'Product $productId';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Forecast generated for $name ($periods periods)'),
          backgroundColor: Colors.green.shade700,
        ),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_friendlyError(e)),
          backgroundColor: Colors.red.shade700,
        ),
      );
    } finally {
      if (mounted) setState(() => _generating = false);
    }
  }

  Future<void> _runGenerateAll() async {
    setState(() => _generating = true);
    try {
      final result = await _api.generateAllForecasts();
      if (!mounted) return;
      final summary = result['summary'] as Map<String, dynamic>? ?? {};
      final succeeded = TypeSafety.toInt(summary['succeeded']);
      final skipped = TypeSafety.toInt(summary['skipped']);
      final failed = TypeSafety.toInt(summary['failed']);
      _showBatchResultDialog(
        title: 'Batch Forecast Complete',
        succeeded: succeeded,
        skipped: skipped,
        failed: failed,
        results: (result['results'] as List? ?? []).cast<Map<String, dynamic>>(),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(_friendlyError(e)), backgroundColor: Colors.red.shade700),
      );
    } finally {
      if (mounted) setState(() => _generating = false);
    }
  }

  void _showBatchResultDialog({
    required String title,
    required int succeeded,
    required int skipped,
    required int failed,
    required List<Map<String, dynamic>> results,
  }) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: SizedBox(
          width: double.maxFinite,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Summary chips
              Wrap(
                spacing: 8,
                children: [
                  Chip(
                    label: Text('✓ $succeeded succeeded'),
                    backgroundColor: Colors.green.shade100,
                  ),
                  if (skipped > 0)
                    Chip(
                      label: Text('⏭ $skipped skipped'),
                      backgroundColor: Colors.orange.shade100,
                    ),
                  if (failed > 0)
                    Chip(
                      label: Text('✗ $failed failed'),
                      backgroundColor: Colors.red.shade100,
                    ),
                ],
              ),
              const SizedBox(height: 12),
              // Per-product log
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 240),
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: results.length,
                  itemBuilder: (_, i) {
                    final r = results[i];
                    final status = r['status']?.toString() ?? '';
                    final icon = status == 'success'
                        ? Icons.check_circle
                        : status == 'skipped'
                            ? Icons.skip_next
                            : Icons.error_outline;
                    final color = status == 'success'
                        ? Colors.green
                        : status == 'skipped'
                            ? Colors.orange
                            : Colors.red;
                    return ListTile(
                      dense: true,
                      leading: Icon(icon, color: color, size: 18),
                      title: Text(r['product_name']?.toString() ?? ''),
                      subtitle: Text(r['message']?.toString() ?? ''),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  // ==========================
  // HELPERS
  // ==========================

  String _friendlyError(Object e) {
    final s = e.toString();
    final match = RegExp(r'"detail"\s*:\s*"([^"]+)"').firstMatch(s);
    return match?.group(1) ?? s;
  }

  String _productName(dynamic rawId) {
    if (rawId == null) return 'Unknown';
    final id = TypeSafety.toInt(rawId);
    return _productNames[id] ?? 'Product $id';
  }

  List<dynamic> get _filtered {
    if (_selectedProductId == null) return _forecasts;
    return _forecasts
        .where((f) => TypeSafety.toInt(f['product_id']) == _selectedProductId)
        .toList();
  }

  List<int> _uniqueProductIds() {
    return _forecasts
        .map((f) => TypeSafety.toInt(f['product_id']))
        .where((id) => id != 0)
        .toSet()
        .toList()
      ..sort();
  }

  List<FlSpot> _buildSpots() {
    final data = [..._filtered]
      ..sort((a, b) => (a['forecast_date'] ?? '').toString()
          .compareTo((b['forecast_date'] ?? '').toString()));
    return List.generate(
      data.length,
      (i) => FlSpot(i.toDouble(), TypeSafety.toDouble(data[i]['predicted_demand'])),
    );
  }

  double _averageDemand() {
    if (_filtered.isEmpty) return 0;
    return _filtered.fold<double>(0, (s, f) => s + TypeSafety.toDouble(f['predicted_demand'])) /
        _filtered.length;
  }

  double _highestDemand() {
    return _filtered.fold<double>(
      0, (mx, f) { final v = TypeSafety.toDouble(f['predicted_demand']); return v > mx ? v : mx; });
  }

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

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 80),
          children: [
            const Text('Forecast Trends',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
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
                  ...productIds.map((id) => Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(_productNames[id] ?? 'Product $id'),
                          selected: _selectedProductId == id,
                          onSelected: (_) => setState(() => _selectedProductId = id),
                        ),
                      )),
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
                      child: Column(children: [
                        const Text('Average'),
                        Text(_averageDemand().toStringAsFixed(0)),
                      ]),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(children: [
                        const Text('Highest'),
                        Text(_highestDemand().toStringAsFixed(0)),
                      ]),
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

            const Text('Forecast Details',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),

            if (_filtered.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(30),
                  child: Text('No forecasts available.\nTap the button below to generate one.',
                      textAlign: TextAlign.center),
                ),
              ),

            ..._filtered.map((forecast) => Card(
                  child: ListTile(
                    leading: const Icon(Icons.show_chart, color: Color(0xFF2E7D32)),
                    title: Text(_productName(forecast['product_id'])),
                    subtitle: Text('Date: ${forecast['forecast_date']}'),
                    trailing: Text(
                      '${TypeSafety.toDouble(forecast['predicted_demand']).toStringAsFixed(0)} units',
                      style: const TextStyle(
                          color: Color(0xFF2E7D32), fontWeight: FontWeight.bold),
                    ),
                  ),
                )),
          ],
        ),
      ),

      // ── Generate FAB ──
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _generating ? null : _openGenerateSheet,
        backgroundColor: const Color(0xFF2E7D32),
        icon: _generating
            ? const SizedBox(
                width: 18, height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : const Icon(Icons.auto_graph, color: Colors.white),
        label: Text(
          _generating ? 'Generating…' : 'Generate Forecast',
          style: const TextStyle(color: Colors.white),
        ),
      ),
    );
  }
}

// ==========================
// GENERATE SHEET
// ==========================

class _GenerateForecastSheet extends StatefulWidget {
  final List<dynamic> products;
  final Map<int, String> productNames;
  final void Function(int productId) onGenerate;
  final VoidCallback onGenerateAll;

  const _GenerateForecastSheet({
    required this.products,
    required this.productNames,
    required this.onGenerate,
    required this.onGenerateAll,
  });

  @override
  State<_GenerateForecastSheet> createState() => _GenerateForecastSheetState();
}

class _GenerateForecastSheetState extends State<_GenerateForecastSheet> {
  int? _selectedProductId;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Handle bar
          Center(
            child: Container(
              width: 40, height: 4,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 16),

          const Text('Generate Forecast',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(
            'Choose a single product to generate a forecast for, or run for all products at once.',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
          ),
          const SizedBox(height: 20),

          // Product dropdown
          DropdownButtonFormField<int>(
            decoration: InputDecoration(
              labelText: 'Select Product',
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            value: _selectedProductId,
            hint: const Text('Pick a product…'),
            items: widget.products.map<DropdownMenuItem<int>>((p) {
              final id = TypeSafety.toInt(p['id']);
              final name = p['name']?.toString() ?? 'Product $id';
              return DropdownMenuItem(value: id, child: Text(name));
            }).toList(),
            onChanged: (v) => setState(() => _selectedProductId = v),
          ),
          const SizedBox(height: 14),

          // Generate single
          FilledButton.icon(
            onPressed: _selectedProductId == null
                ? null
                : () => widget.onGenerate(_selectedProductId!),
            icon: const Icon(Icons.auto_graph),
            label: const Text('Generate for Selected Product'),
            style: FilledButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 10),

          // Divider
          Row(children: [
            const Expanded(child: Divider()),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text('or', style: TextStyle(color: Colors.grey.shade500)),
            ),
            const Expanded(child: Divider()),
          ]),
          const SizedBox(height: 10),

          // Generate all
          OutlinedButton.icon(
            onPressed: widget.onGenerateAll,
            icon: const Icon(Icons.all_inclusive),
            label: const Text('Generate for All Products'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ],
      ),
    );
  }
}
