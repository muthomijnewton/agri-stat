import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../services/api_service.dart';

class ForecastsScreen extends StatefulWidget {
  const ForecastsScreen({super.key});

  @override
  State<ForecastsScreen> createState() =>
      _ForecastsScreenState();
}

class _ForecastsScreenState
    extends State<ForecastsScreen> {
  final ApiService _apiService =
      ApiService();

  bool _isLoading = true;

  bool _hasError = false;

  List<dynamic> _forecasts = [];

  int? _selectedProductId;

  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();

    _loadForecasts();
  }

  // ==========================
  // SAFE CONVERTERS
  // ==========================

  int _toInt(dynamic value) {
    if (value == null) return 0;

    if (value is int) return value;

    if (value is num) {
      return value.toInt();
    }

    if (value is String) {
      return int.tryParse(
            value,
          ) ??
          0;
    }

    return 0;
  }

  double _toDouble(
    dynamic value,
  ) {
    if (value == null) {
      return 0;
    }

    if (value is num) {
      return value.toDouble();
    }

    if (value is String) {
      return double.tryParse(
            value,
          ) ??
          0;
    }

    return 0;
  }

  // ==========================
  // LOAD DATA
  // ==========================

  Future<void> _loadForecasts() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;

          _hasError = false;
        });
      }

      final forecasts =
          await _apiService.getForecasts();

      if (!mounted) return;

      setState(() {
        _forecasts = forecasts;

        _lastUpdated =
            DateTime.now();

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
            'Error loading forecasts: $e',
          ),
        ),
      );
    }
  }

  // ==========================
  // FILTERS
  // ==========================

  List<dynamic>
      get _filteredForecasts {
    if (_selectedProductId ==
        null) {
      return _forecasts;
    }

    return _forecasts.where(
      (f) {
        return _toInt(
              f['product_id'],
            ) ==
            _selectedProductId;
      },
    ).toList();
  }

  // ==========================
  // PRODUCT IDS
  // ==========================

  List<int> _getProducts() {
    return _forecasts
        .map(
          (e) => _toInt(
            e['product_id'],
          ),
        )
        .where((e) => e != 0)
        .toSet()
        .toList();
  }

  // ==========================
  // CHART DATA
  // ==========================

  List<FlSpot> _buildSpots() {
    final data =
        [..._filteredForecasts];

    if (data.isEmpty) {
      return [];
    }

    data.sort(
      (a, b) => (a[
              'forecast_date'] ??
          '')
          .toString()
          .compareTo(
            (b['forecast_date'] ??
                    '')
                .toString(),
          ),
    );

    return List.generate(
      data.length,

      (index) {
        return FlSpot(
          index.toDouble(),

          _toDouble(
            data[index]
                ['predicted_demand'],
          ),
        );
      },
    );
  }

  // ==========================
  // ANALYTICS
  // ==========================

  double _averageDemand() {
    if (_filteredForecasts
        .isEmpty) {
      return 0;
    }

    double total = 0;

    for (var item
        in _filteredForecasts) {
      total += _toDouble(
        item['predicted_demand'],
      );
    }

    return total /
        _filteredForecasts.length;
  }

  double _highestDemand() {
    double highest = 0;

    for (var item
        in _filteredForecasts) {
      final value =
          _toDouble(
        item['predicted_demand'],
      );

      if (value > highest) {
        highest = value;
      }
    }

    return highest;
  }

  // ==========================
  // BUILD
  // ==========================

  @override
  Widget build(
    BuildContext context,
  ) {
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
              MainAxisAlignment
                  .center,

          children: [
            const Icon(
              Icons.error_outline,

              size: 70,
            ),

            const SizedBox(
              height: 16,
            ),

            const Text(
              'Unable to load forecasts',
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  _loadForecasts,

              child:
                  const Text(
                'Retry',
              ),
            ),
          ],
        ),
      );
    }

    final spots =
        _buildSpots();

    return RefreshIndicator(
      onRefresh:
          _loadForecasts,

      child: ListView(
        padding:
            const EdgeInsets.all(
          12,
        ),

        children: [
          const Text(
            'Forecast Trends',

            style: TextStyle(
              fontSize: 22,

              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 12,
          ),

          // ==================
          // FILTER CHIPS
          // ==================

          SingleChildScrollView(
            scrollDirection:
                Axis.horizontal,

            child: Row(
              children: [
                ChoiceChip(
                  label: const Text(
                    'All Products',
                  ),

                  selected:
                      _selectedProductId ==
                          null,

                  onSelected:
                      (_) {
                    setState(() {
                      _selectedProductId =
                          null;
                    });
                  },
                ),

                const SizedBox(
                  width: 8,
                ),

                ..._getProducts().map(
                  (id) {
                    return Padding(
                      padding:
                          const EdgeInsets.only(
                        right: 8,
                      ),

                      child:
                          ChoiceChip(
                        label:
                            Text(
                          'Product $id',
                        ),

                        selected:
                            _selectedProductId ==
                                id,

                        onSelected:
                            (_) {
                          setState(
                            () {
                              _selectedProductId =
                                  id;
                            },
                          );
                        },
                      ),
                    );
                  },
                ),
              ],
            ),
          ),

          const SizedBox(
            height: 16,
          ),

          // ==================
          // STATS
          // ==================

          Row(
            children: [
              Expanded(
                child: Card(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    child: Column(
                      children: [
                        const Text(
                          'Average',
                        ),

                        Text(
                          _averageDemand()
                              .toStringAsFixed(
                            0,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              Expanded(
                child: Card(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(
                      12,
                    ),

                    child: Column(
                      children: [
                        const Text(
                          'Highest',
                        ),

                        Text(
                          _highestDemand()
                              .toStringAsFixed(
                            0,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(
            height: 12,
          ),

          if (_lastUpdated != null)
            Align(
              alignment:
                  Alignment.centerRight,

              child: Text(
                'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
              ),
            ),

          const SizedBox(
            height: 20,
          ),

          // ==================
          // CHART
          // ==================

          SizedBox(
            height: 300,

            child: spots.isEmpty
                ? const Center(
                    child: Text(
                      'No forecast data',
                    ),
                  )

                : LineChart(
                    LineChartData(
                      gridData:
                          const FlGridData(
                        show: true,
                      ),

                      titlesData:
                          const FlTitlesData(
                        show: false,
                      ),

                      borderData:
                          FlBorderData(
                        show: true,
                      ),

                      lineBarsData: [
                        LineChartBarData(
                          spots:
                              spots,

                          isCurved:
                              true,

                          barWidth:
                              4,

                          color:
                              const Color(
                            0xFF2E7D32,
                          ),

                          dotData:
                              const FlDotData(
                            show:
                                true,
                          ),
                        ),
                      ],
                    ),
                  ),
          ),

          const SizedBox(
            height: 20,
          ),

          const Text(
            'Forecast Details',

            style: TextStyle(
              fontSize: 18,

              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 12,
          ),

          if (_filteredForecasts
              .isEmpty)
            const Center(
              child: Padding(
                padding:
                    EdgeInsets.all(
                  30,
                ),

                child: Text(
                  'No forecasts available',
                ),
              ),
            ),

          ..._filteredForecasts.map(
            (forecast) {
              return Card(
                child: ListTile(
                  leading:
                      const Icon(
                    Icons.show_chart,

                    color: Color(
                      0xFF2E7D32,
                    ),
                  ),

                  title: Text(
                    'Product ${forecast['product_id']}',
                  ),

                  subtitle: Text(
                    'Date: ${forecast['forecast_date']}',
                  ),

                  trailing: Text(
                    '${forecast['predicted_demand']} units',

                    style:
                        const TextStyle(
                      color: Color(
                        0xFF2E7D32,
                      ),

                      fontWeight:
                          FontWeight.bold,
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}