import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../widgets/product_card.dart';

class ProductsScreen extends StatefulWidget {
  const ProductsScreen({super.key});

  @override
  State<ProductsScreen> createState() =>
      _ProductsScreenState();
}

class _ProductsScreenState
    extends State<ProductsScreen> {
  final ApiService _apiService =
      ApiService();

  bool _isLoading = true;

  bool _hasError = false;

  List<dynamic> _products = [];

  List<dynamic> _filteredProducts = [];

  String _search = '';

  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();

    _loadProducts();
  }

  // ==========================
  // LOAD PRODUCTS
  // ==========================

  Future<void> _loadProducts() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;
          _hasError = false;
        });
      }

      final products =
          await _apiService.getProducts();

      products.sort(
        (a, b) => (a['name'] ?? '')
            .toString()
            .toLowerCase()
            .compareTo(
              (b['name'] ?? '')
                  .toString()
                  .toLowerCase(),
            ),
      );

      if (!mounted) return;

      setState(() {
        _products = products;

        _filteredProducts = products;

        _lastUpdated = DateTime.now();

        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _hasError = true;

        _isLoading = false;
      });

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Error loading products: $e',
          ),
        ),
      );
    }
  }

  // ==========================
  // SEARCH
  // ==========================

  void _filterProducts(
    String value,
  ) {
    _search = value;

    if (value.isEmpty) {
      setState(() {
        _filteredProducts =
            _products;
      });

      return;
    }

    setState(() {
      _filteredProducts =
          _products.where((p) {
        final name =
            (p['name'] ?? '')
                .toString()
                .toLowerCase();

        final category =
            (p['category'] ?? '')
                .toString()
                .toLowerCase();

        return name.contains(
              value.toLowerCase(),
            ) ||
            category.contains(
              value.toLowerCase(),
            );
      }).toList();
    });
  }

  // ==========================
  // SAFE PRICE PARSER
  // ==========================

  double _parsePrice(
    dynamic rawPrice,
  ) {
    if (rawPrice == null) {
      return 0;
    }

    if (rawPrice is int) {
      return rawPrice.toDouble();
    }

    if (rawPrice is double) {
      return rawPrice;
    }

    if (rawPrice is String) {
      return double.tryParse(
            rawPrice,
          ) ??
          0;
    }

    return 0;
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(
        child:
            CircularProgressIndicator(),
      );
    }

    if (_hasError) {
      return Center(
        child: Column(
          mainAxisAlignment:
              MainAxisAlignment.center,

          children: [
            const Icon(
              Icons.error_outline,
              size: 70,
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              "Unable to load products",
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  _loadProducts,

              child:
                  const Text("Retry"),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadProducts,

      child: Column(
        children: [
          // ==================
          // SEARCH BAR
          // ==================

          Padding(
            padding:
                const EdgeInsets.all(
              12,
            ),

            child: TextField(
              onChanged:
                  _filterProducts,

              decoration:
                  InputDecoration(
                prefixIcon:
                    const Icon(
                  Icons.search,
                ),

                hintText:
                    'Search products...',

                border:
                    OutlineInputBorder(
                  borderRadius:
                      BorderRadius.circular(
                    12,
                  ),
                ),
              ),
            ),
          ),

          // ==================
          // INFO BAR
          // ==================

          Padding(
            padding:
                const EdgeInsets.symmetric(
              horizontal: 16,
            ),

            child: Row(
              mainAxisAlignment:
                  MainAxisAlignment
                      .spaceBetween,

              children: [
                Text(
                  "${_filteredProducts.length} products",
                ),

                Text(
                  _lastUpdated ==
                          null
                      ? ""
                      : "Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}",
                ),
              ],
            ),
          ),

          const SizedBox(
            height: 10,
          ),

          // ==================
          // EMPTY STATE
          // ==================

          Expanded(
            child: _filteredProducts
                    .isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment:
                          MainAxisAlignment
                              .center,

                      children: [
                        const Icon(
                          Icons.inventory_2_outlined,
                          size: 70,
                        ),

                        const SizedBox(
                          height: 16,
                        ),

                        Text(
                          _search
                                  .isEmpty
                              ? "No products available"

                              : "No matching products",
                        ),
                      ],
                    ),
                  )

                // ==================
                // PRODUCT LIST
                // ==================

                : ListView.builder(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    itemCount:
                        _filteredProducts
                            .length,

                    itemBuilder:
                        (
                      context,
                      index,
                    ) {
                      try {
                        final product =
                            _filteredProducts[
                                index];

                        return ProductCard(
                          id:
                              product['id'] ??
                                  0,

                          name:
                              product['name'] ??
                                  'No name',

                          category:
                              product['category'] ??
                                  'Uncategorized',

                          price:
                              _parsePrice(
                            product[
                                'unit_price'],
                          ),

                          unit:
                              product['unit'] ??
                                  '',
                        );
                      } catch (e) {
                        return const Card(
                          child: ListTile(
                            title: Text(
                              'Invalid product data',
                            ),
                          ),
                        );
                      }
                    },
                  ),
          ),
        ],
      ),
    );
  }
}