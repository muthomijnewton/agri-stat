import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class SummaryChart extends StatelessWidget {
  final List<dynamic> data;

  const SummaryChart({
    super.key,
    required this.data,
  });

  double _toDouble(dynamic value) {
    if (value == null) return 0;

    if (value is num) return value.toDouble();

    if (value is String) {
      return double.tryParse(value) ?? 0;
    }

    return 0;
  }

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return const Center(
        child: Text('No chart data available'),
      );
    }

    return PieChart(
      PieChartData(
        centerSpaceRadius: 40,

        sectionsSpace: 3,

        sections: List.generate(
          data.length,
          (index) {
            final item = data[index];

            final total = _toDouble(item['total']);

            final category =
                item['category']?.toString() ?? 'Unknown';

            return PieChartSectionData(
              value: total,

              title: category,

              radius: 60,

              titleStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),

              color: Colors.primaries[
                  index % Colors.primaries.length],
            );
          },
        ),
      ),
    );
  }
}