import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/recommendation_card.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({Key? key}) : super(key: key);

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _recommendations = [];

  @override
  void initState() {
    super.initState();
    _loadRecommendations();
  }

  Future<void> _loadRecommendations() async {
    try {
      setState(() => _isLoading = true);
      final recommendations = await _apiService.getRecommendations();
      setState(() {
        _recommendations = recommendations;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading recommendations: $e')),
      );
    }
  }

  Future<void> _approveRecommendation(int id) async {
    try {
      await _apiService.approveRecommendation(id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Recommendation approved!')),
      );
      _loadRecommendations();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error approving recommendation: $e')),
      );
    }
  }

  Future<void> _implementRecommendation(int id) async {
    try {
      await _apiService.implementRecommendation(id);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Recommendation implemented!')),
      );
      _loadRecommendations();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error implementing recommendation: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_recommendations.isEmpty) {
      return const Center(
        child: Text('No recommendations found'),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadRecommendations,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _recommendations.length,
        itemBuilder: (context, index) {
          final rec = _recommendations[index];
          return RecommendationCard(
            id: rec['id'],
            productName: 'Product ID: ${rec['product_id']}',
            recommendedQuantity: rec['recommended_quantity'],
            status: rec['status'],
            onApprove: rec['status'] == 'pending'
                ? () => _approveRecommendation(rec['id'])
                : null,
            onImplement: rec['status'] == 'approved'
                ? () => _implementRecommendation(rec['id'])
                : null,
          );
        },
      ),
    );
  }
}
