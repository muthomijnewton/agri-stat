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
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  bool _actionLoading = false;
  bool _hasError = false;

  List<dynamic> _recommendations = [];

  /// id → name map built from GET /products
  Map<int, String> _productNames = {};

  String _selectedStatus = 'all';
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

      // Fetch recommendations and products in parallel
      final results = await Future.wait([
        _apiService.getRecommendations(),
        _apiService.getProducts(),
      ]);

      final recs = results[0] as List;
      final prods = results[1] as List;

      // Build id → name lookup
      final names = <int, String>{
        for (final p in prods)
          if (p['id'] != null)
            TypeSafety.toInt(p['id']): p['name']?.toString() ?? 'Product ${p['id']}',
      };

      if (!mounted) return;

      setState(() {
        _recommendations = recs;
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
        SnackBar(content: Text('Error: $e')),
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
    if (_selectedStatus == 'all') return _recommendations;
    return _recommendations
        .where((r) => r['status']?.toString() == _selectedStatus)
        .toList();
  }

  int _countByStatus(String status) =>
      _recommendations.where((r) => r['status']?.toString() == status).length;

  // ==========================
  // APPROVE
  // ==========================

  Future<void> _approve(int id) async {
    try {
      setState(() => _actionLoading = true);
      await _apiService.approveRecommendation(id);
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

  // ==========================
  // IMPLEMENT
  // ==========================

  Future<void> _implement(int id) async {
    try {
      setState(() => _actionLoading = true);
      await _apiService.implementRecommendation(id);
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
            const Text('Unable to load recommendations'),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: _load, child: const Text('Retry')),
          ],
        ),
      );
    }

    return Stack(
      children: [
        RefreshIndicator(
          onRefresh: _load,
          child: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              const Text(
                'AI Recommendations',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),

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
                    for (final status in ['all', 'pending', 'approved', 'implemented'])
                      Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ChoiceChip(
                          label: Text(status.toUpperCase()),
                          selected: _selectedStatus == status,
                          onSelected: (_) => setState(() => _selectedStatus = status),
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
                    child: Text('No recommendations found'),
                  ),
                ),

              // ── Recommendation cards ──
              ..._filtered.map((rec) {
                final id = TypeSafety.toInt(rec['id']);
                final quantity = TypeSafety.toInt(rec['recommended_quantity']);
                final status = rec['status']?.toString() ?? 'pending';
                final name = _productName(rec['product_id']);

                return RecommendationCard(
                  id: id,
                  productName: name,
                  recommendedQuantity: quantity,
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
    );
  }
}
