import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/recommendation_card.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() =>
      _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  bool _actionLoading = false;

  List<dynamic> _recommendations = [];

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  int _toInt(dynamic value) {
    if (value == null) return 0;

    if (value is int) return value;

    if (value is double) return value.toInt();

    if (value is String) {
      return int.tryParse(value) ?? 0;
    }

    return 0;
  }

  String _toStringValue(dynamic value) {
    if (value == null) return '';

    return value.toString();
  }

  Future<void> _loadRecommendations() async {
    try {
      setState(() => _isLoading = true);

      final data = await _apiService.getRecommendations();

      setState(() {
        _recommendations = (data as List?) ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Error loading recommendations: $e',
            ),
          ),
        );
      }
    }
  }

  Future<void> _approve(int id) async {
    try {
      setState(() => _actionLoading = true);

      await _apiService.approveRecommendation(id);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Recommendation approved'),
          ),
        );
      }

      await _loadRecommendations();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Approve failed: $e'),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _actionLoading = false);
      }
    }
  }

  Future<void> _implement(int id) async {
    try {
      setState(() => _actionLoading = true);

      await _apiService.implementRecommendation(id);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Recommendation implemented'),
          ),
        );
      }

      await _loadRecommendations();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Implement failed: $e'),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _actionLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_recommendations.isEmpty) {
      return const Center(
        child: Text(
          'No recommendations found',
        ),
      );
    }

    return Stack(
      children: [
        RefreshIndicator(
          onRefresh: _loadRecommendations,
          child: ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: _recommendations.length,
            itemBuilder: (context, index) {
              final rec = _recommendations[index] ?? {};

              final id = _toInt(rec['id']);

              final productId =
                  _toStringValue(rec['product_id']);

              final quantity =
                  _toInt(rec['recommended_quantity']);

              final status =
                  _toStringValue(rec['status']);

              return RecommendationCard(
                id: id,

                productName: 'Product $productId',

                recommendedQuantity: quantity,

                status: status.isEmpty
                    ? 'pending'
                    : status,

                onApprove: status == 'pending'
                    ? () => _approve(id)
                    : null,

                onImplement: status == 'approved'
                    ? () => _implement(id)
                    : null,
              );
            },
          ),
        ),

        if (_actionLoading)
          Container(
            color: Colors.black.withValues(alpha: 0.2),
            child: const Center(
              child: CircularProgressIndicator(),
            ),
          ),
      ],
    );
  }
}