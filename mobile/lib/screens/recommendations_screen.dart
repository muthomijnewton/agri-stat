import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../utils/type_safety.dart';
import '../widgets/recommendation_card.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  final ApiService _api = ApiService();

  bool _isLoading = true;
  bool _actionLoading = false;
  bool _generating = false;
  bool _hasError = false;

  List<dynamic> _recommendations = [];
  Map<int, String> _productNames = {};
  List<dynamic> _products = [];

  String _selectedStatus = 'all';
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
        _api.getRecommendations(),
        _api.getProducts(),
      ]);

      final recs = results[0] as List;
      final prods = results[1] as List;

      final names = <int, String>{
        for (final p in prods)
          if (p['id'] != null)
            TypeSafety.toInt(p['id']): p['name']?.toString() ?? 'Product ${p['id']}',
      };

      if (!mounted) return;
      setState(() {
        _recommendations = recs;
        _products = prods;
        _productNames = names;
        _lastUpdated = DateTime.now();
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  // ==========================
  // GENERATE
  // ==========================

  Future<void> _openGenerateSheet() async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => _GenerateRecommendationSheet(
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
      final result = await _api.generateRecommendation(productId);
      if (!mounted) return;
      final qty = TypeSafety.toInt(result['recommended_quantity']);
      final name = _productNames[productId] ?? 'Product $productId';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Recommendation for $name: stock $qty units'),
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
      final result = await _api.generateAllRecommendations();
      if (!mounted) return;
      final summary = result['summary'] as Map<String, dynamic>? ?? {};
      _showBatchResultDialog(
        title: 'Batch Recommendations Complete',
        succeeded: TypeSafety.toInt(summary['succeeded']),
        skipped: TypeSafety.toInt(summary['skipped']),
        failed: TypeSafety.toInt(summary['failed']),
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
  // APPROVE / IMPLEMENT
  // ==========================

  Future<void> _approve(int id) async {
    try {
      setState(() => _actionLoading = true);
      await _api.approveRecommendation(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Recommendation approved')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Approve failed: $e')),
      );
    } finally {
      if (mounted) setState(() => _actionLoading = false);
    }
  }

  Future<void> _implement(int id) async {
    try {
      setState(() => _actionLoading = true);
      await _api.implementRecommendation(id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Recommendation implemented')),
      );
      await _load();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Implement failed: $e')),
      );
    } finally {
      if (mounted) setState(() => _actionLoading = false);
    }
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
    if (_selectedStatus == 'all') return _recommendations;
    return _recommendations
        .where((r) => r['status']?.toString() == _selectedStatus)
        .toList();
  }

  int _countByStatus(String status) =>
      _recommendations.where((r) => r['status']?.toString() == status).length;

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
            const Text('Unable to load recommendations'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }

    return Scaffold(
      body: Stack(
        children: [
          RefreshIndicator(
            onRefresh: _load,
            child: ListView(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 80),
              children: [
                const Text('AI Recommendations',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),

                // ── Status counters ──
                Row(
                  children: [
                    for (final (label, status) in [
                      ('Pending', 'pending'),
                      ('Approved', 'approved'),
                      ('Done', 'implemented'),
                    ])
                      Expanded(
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Column(
                              children: [
                                Text(label),
                                Text('${_countByStatus(status)}'),
                              ],
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 16),

                // ── Filter chips ──
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      for (final s in ['all', 'pending', 'approved', 'implemented'])
                        Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(s.toUpperCase()),
                            selected: _selectedStatus == s,
                            onSelected: (_) => setState(() => _selectedStatus = s),
                          ),
                        ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),

                if (_lastUpdated != null)
                  Align(
                    alignment: Alignment.centerRight,
                    child: Text(
                      'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
                    ),
                  ),
                const SizedBox(height: 16),

                if (_filtered.isEmpty)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(30),
                      child: Text(
                        'No recommendations found.\nTap the button below to generate some.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),

                ..._filtered.map((rec) {
                  final id = TypeSafety.toInt(rec['id']);
                  final qty = TypeSafety.toInt(rec['recommended_quantity']);
                  final status = rec['status']?.toString() ?? 'pending';

                  return RecommendationCard(
                    id: id,
                    productName: _productName(rec['product_id']),
                    recommendedQuantity: qty,
                    status: status.isEmpty ? 'pending' : status,
                    onApprove: status == 'pending' ? () => _approve(id) : null,
                    onImplement: status == 'approved' ? () => _implement(id) : null,
                  );
                }),
              ],
            ),
          ),

          // ── Action overlay ──
          if (_actionLoading)
            Container(
              color: Colors.black.withValues(alpha: 0.2),
              child: const Center(child: CircularProgressIndicator()),
            ),
        ],
      ),

      // ── Generate FAB ──
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _generating ? null : _openGenerateSheet,
        backgroundColor: const Color(0xFF1565C0),
        icon: _generating
            ? const SizedBox(
                width: 18, height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
            : const Icon(Icons.lightbulb_outline, color: Colors.white),
        label: Text(
          _generating ? 'Generating…' : 'Generate',
          style: const TextStyle(color: Colors.white),
        ),
      ),
    );
  }
}

// ==========================
// GENERATE SHEET
// ==========================

class _GenerateRecommendationSheet extends StatefulWidget {
  final List<dynamic> products;
  final Map<int, String> productNames;
  final void Function(int productId) onGenerate;
  final VoidCallback onGenerateAll;

  const _GenerateRecommendationSheet({
    required this.products,
    required this.productNames,
    required this.onGenerate,
    required this.onGenerateAll,
  });

  @override
  State<_GenerateRecommendationSheet> createState() =>
      _GenerateRecommendationSheetState();
}

class _GenerateRecommendationSheetState
    extends State<_GenerateRecommendationSheet> {
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

          const Text('Generate Recommendation',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text(
            'Generate an AI-powered inventory recommendation for one product or all products at once.',
            style: TextStyle(color: Colors.grey.shade600, fontSize: 13),
          ),
          const SizedBox(height: 20),

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

          FilledButton.icon(
            onPressed: _selectedProductId == null
                ? null
                : () => widget.onGenerate(_selectedProductId!),
            icon: const Icon(Icons.lightbulb_outline),
            label: const Text('Generate for Selected Product'),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF1565C0),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
          const SizedBox(height: 10),

          Row(children: [
            const Expanded(child: Divider()),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text('or', style: TextStyle(color: Colors.grey.shade500)),
            ),
            const Expanded(child: Divider()),
          ]),
          const SizedBox(height: 10),

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
