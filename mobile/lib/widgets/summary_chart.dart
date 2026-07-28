import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

/// Pie chart showing revenue split by transaction type.
///
/// Expects data items with shape: { type, count, revenue, quantity }
/// as returned by GET /stats/transaction-type-split
class SummaryChart extends StatelessWidget {
  final List<dynamic> data;

  const SummaryChart({super.key, required this.data});

  static const List<Color> _colors = [
    Color(0xFF2E7D32), // green  — sales
    Color(0xFF1565C0), // blue   — purchases
    Color(0xFF6A1B9A), // purple
    Color(0xFFC62828), // red
    Color(0xFFF9A825), // amber
    Color(0xFF00897B), // teal
  ];

  double _toDouble(dynamic value) {
    if (value == null) return 0;
    if (value is num) return value.toDouble();
    return double.tryParse(value.toString()) ?? 0;
  }

  String _label(String? type) {
    if (type == null || type.isEmpty) return 'Unknown';
    return '${type[0].toUpperCase()}${type.substring(1)}s';
  }

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return const Center(child: Text('No chart data available'));
    }

    final sections = List.generate(data.length, (i) {
      final item = data[i];
      final revenue = _toDouble(item['revenue']);
      final label = _label(item['type']?.toString());

      return PieChartSectionData(
        value: revenue,
        title: label,
        radius: 65,
        color: _colors[i % _colors.length],
        titleStyle: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      );
    });

    return PieChart(
      PieChartData(
        centerSpaceRadius: 45,
        sectionsSpace: 4,
        sections: sections,
        pieTouchData: PieTouchData(enabled: true),
      ),
    );
  }
}
