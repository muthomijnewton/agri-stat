import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ForecastsScreen extends StatefulWidget {
  const ForecastsScreen({Key? key}) : super(key: key);

  @override
  State<ForecastsScreen> createState() => _ForecastsScreenState();
}

class _ForecastsScreenState extends State<ForecastsScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  List<dynamic> _forecasts = [];

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
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading forecasts: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_forecasts.isEmpty) {
      return const Center(
        child: Text('No forecasts found'),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadForecasts,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _forecasts.length,
        itemBuilder: (context, index) {
          final forecast = _forecasts[index];
          return Card(
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Product ID: ${forecast['product_id']}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      if (forecast['model_type'] != null)
                        Chip(
                          label: Text(forecast['model_type']),
                          backgroundColor: const Color(0xFF2E7D32).withOpacity(0.2),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Forecast Date: ${forecast['forecast_date']}'),
                  const SizedBox(height: 8),
                  Text(
                    'Predicted Demand: ${forecast['predicted_demand']} units',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Color(0xFF2E7D32),
                    ),
                  ),
                  if (forecast['confidence_lower'] != null && forecast['confidence_upper'] != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Confidence: ${forecast['confidence_lower']} - ${forecast['confidence_upper']}',
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                    ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
