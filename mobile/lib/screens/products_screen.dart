import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/product_card.dart';

class ProductsScreen extends StatefulWidget {
  const ProductsScreen({super.key});

  @override
  State<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  final ApiService _apiService = ApiService();

  bool _isLoading = true;
  List<dynamic> _products = [];

  @override
  void initState() {
    super.initState();
    _loadProducts();
  }

  Future<void> _loadProducts() async {
    try {
      setState(() => _isLoading = true);

      final products = await _apiService.getProducts();

      setState(() {
        _products = products;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading products: $e')),
        );
      }
    }
  }

  double _parsePrice(dynamic rawPrice) {
    if (rawPrice == null) return 0.0;

    if (rawPrice is int) return rawPrice.toDouble();

    if (rawPrice is double) return rawPrice;

    if (rawPrice is String) {
      return double.tryParse(rawPrice) ?? 0.0;
    }

    return 0.0;
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_products.isEmpty) {
      return const Center(
        child: Text(
          'No products found',
          style: TextStyle(fontSize: 16),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadProducts,
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: _products.length,
        itemBuilder: (context, index) {
          try {
            final product = _products[index];

            final price = _parsePrice(product['unit_price']);

            return ProductCard(
              id: product['id'] ?? 0,
              name: product['name'] ?? 'No name',
              category: product['category'] ?? 'Uncategorized',
              price: price,
              unit: product['unit'] ?? '',
            );
          } catch (e) {
            // Prevent entire screen crash if one item is bad
            return const Card(
              child: ListTile(
                title: Text('Error loading product'),
              ),
            );
          }
        },
      ),
    );
  }
}
