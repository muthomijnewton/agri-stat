import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../widgets/recommendation_card.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() =>
      _RecommendationsScreenState();
}

class _RecommendationsScreenState
    extends State<RecommendationsScreen> {
  final ApiService _apiService =
      ApiService();

  bool _isLoading = true;

  bool _actionLoading = false;

  bool _hasError = false;

  List<dynamic> _recommendations = [];

  String _selectedStatus = 'all';

  DateTime? _lastUpdated;

  @override
  void initState() {
    super.initState();

    _loadRecommendations();
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

  String _toStringValue(
    dynamic value,
  ) {
    if (value == null) {
      return '';
    }

    return value.toString();
  }

  // ==========================
  // LOAD DATA
  // ==========================

  Future<void>
      _loadRecommendations() async {
    try {
      if (mounted) {
        setState(() {
          _isLoading = true;

          _hasError = false;
        });
      }

      final data =
          await _apiService
              .getRecommendations();

      if (!mounted) return;

      setState(() {
        _recommendations =
            data;

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
            'Error: $e',
          ),
        ),
      );
    }
  }

  // ==========================
  // FILTER
  // ==========================

  List<dynamic>
      get _filteredRecommendations {
    if (_selectedStatus ==
        'all') {
      return _recommendations;
    }

    return _recommendations
        .where(
          (r) =>
              _toStringValue(
                r['status'],
              ) ==
              _selectedStatus,
        )
        .toList();
  }

  // ==========================
  // COUNTS
  // ==========================

  int _countByStatus(
    String status,
  ) {
    return _recommendations
        .where(
          (r) =>
              _toStringValue(
                r['status'],
              ) ==
              status,
        )
        .length;
  }

  // ==========================
  // APPROVE
  // ==========================

  Future<void> _approve(
    int id,
  ) async {
    try {
      setState(() {
        _actionLoading = true;
      });

      await _apiService
          .approveRecommendation(
        id,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        const SnackBar(
          content: Text(
            'Recommendation approved',
          ),
        ),
      );

      await _loadRecommendations();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Approve failed: $e',
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _actionLoading =
              false;
        });
      }
    }
  }

  // ==========================
  // IMPLEMENT
  // ==========================

  Future<void> _implement(
    int id,
  ) async {
    try {
      setState(() {
        _actionLoading = true;
      });

      await _apiService
          .implementRecommendation(
        id,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        const SnackBar(
          content: Text(
            'Recommendation implemented',
          ),
        ),
      );

      await _loadRecommendations();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content: Text(
            'Implement failed: $e',
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _actionLoading =
              false;
        });
      }
    }
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
              'Unable to load recommendations',
            ),

            const SizedBox(
              height: 16,
            ),

            ElevatedButton(
              onPressed:
                  _loadRecommendations,

              child:
                  const Text(
                'Retry',
              ),
            ),
          ],
        ),
      );
    }

    return Stack(
      children: [
        RefreshIndicator(
          onRefresh:
              _loadRecommendations,

          child: ListView(
            padding:
                const EdgeInsets.all(
              12,
            ),

            children: [
              const Text(
                'AI Recommendations',

                style: TextStyle(
                  fontSize: 22,

                  fontWeight:
                      FontWeight.bold,
                ),
              ),

              const SizedBox(
                height: 16,
              ),

              // ==================
              // COUNTERS
              // ==================

              Row(
                children: [
                  Expanded(
                    child: Card(
                      child:
                          Padding(
                        padding:
                            const EdgeInsets.all(
                          12,
                        ),

                        child:
                            Column(
                          children: [
                            const Text(
                              'Pending',
                            ),

                            Text(
                              '${_countByStatus('pending')}',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  Expanded(
                    child: Card(
                      child:
                          Padding(
                        padding:
                            const EdgeInsets.all(
                          12,
                        ),

                        child:
                            Column(
                          children: [
                            const Text(
                              'Approved',
                            ),

                            Text(
                              '${_countByStatus('approved')}',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),

                  Expanded(
                    child: Card(
                      child:
                          Padding(
                        padding:
                            const EdgeInsets.all(
                          12,
                        ),

                        child:
                            Column(
                          children: [
                            const Text(
                              'Done',
                            ),

                            Text(
                              '${_countByStatus('implemented')}',
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(
                height: 16,
              ),

              // ==================
              // FILTER CHIPS
              // ==================

              SingleChildScrollView(
                scrollDirection:
                    Axis.horizontal,

                child: Row(
                  children: [
                    'all',

                    'pending',

                    'approved',

                    'implemented',
                  ].map(
                    (status) {
                      return Padding(
                        padding:
                            const EdgeInsets.only(
                          right: 8,
                        ),

                        child:
                            ChoiceChip(
                          label:
                              Text(
                            status
                                .toUpperCase(),
                          ),

                          selected:
                              _selectedStatus ==
                                  status,

                          onSelected:
                              (_) {
                            setState(
                              () {
                                _selectedStatus =
                                    status;
                              },
                            );
                          },
                        ),
                      );
                    },
                  ).toList(),
                ),
              ),

              const SizedBox(
                height: 12,
              ),

              if (_lastUpdated !=
                  null)
                Align(
                  alignment:
                      Alignment
                          .centerRight,

                  child: Text(
                    'Updated ${_lastUpdated!.hour}:${_lastUpdated!.minute.toString().padLeft(2, '0')}',
                  ),
                ),

              const SizedBox(
                height: 16,
              ),

              if (_filteredRecommendations
                  .isEmpty)
                const Center(
                  child: Padding(
                    padding:
                        EdgeInsets.all(
                      30,
                    ),

                    child: Text(
                      'No recommendations found',
                    ),
                  ),
                ),

              ..._filteredRecommendations
                  .map(
                (rec) {
                  final id =
                      _toInt(
                    rec['id'],
                  );

                  final productId =
                      _toStringValue(
                    rec['product_id'],
                  );

                  final quantity =
                      _toInt(
                    rec['recommended_quantity'],
                  );

                  final status =
                      _toStringValue(
                    rec['status'],
                  );

                  return RecommendationCard(
                    id: id,

                    productName:
                        'Product $productId',

                    recommendedQuantity:
                        quantity,

                    status:
                        status.isEmpty
                            ? 'pending'
                            : status,

                    onApprove:
                        status ==
                                'pending'
                            ? () =>
                                _approve(
                                  id,
                                )
                            : null,

                    onImplement:
                        status ==
                                'approved'
                            ? () =>
                                _implement(
                                  id,
                                )
                            : null,
                  );
                },
              ),
            ],
          ),
        ),

        if (_actionLoading)
          Container(
            color: Colors.black
                .withValues(
              alpha: 0.2,
            ),

            child: const Center(
              child:
                  CircularProgressIndicator(),
            ),
          ),
      ],
    );
  }
}