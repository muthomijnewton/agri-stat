import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class SummaryChart extends StatelessWidget {
  final List<dynamic> data;

  const SummaryChart({
    super.key,
    required this.data,
  });

  static const List<Color> chartColors = [
    Color(0xFF2E7D32),
    Color(0xFF1565C0),
    Color(0xFF6A1B9A),
    Color(0xFFC62828),
    Color(0xFFF9A825),
    Color(0xFF00897B),
    Color(0xFF5D4037),
    Color(0xFF455A64),
  ];

  double _toDouble(dynamic value) {
    if (value == null) return 0;

    if (value is num) {
      return value.toDouble();
    }

    if (value is String) {
      return double.tryParse(value) ?? 0;
    }

    return 0;
  }

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return const Center(
        child: Text(
          'No chart data available',
        ),
      );
    }

    final sections = List.generate(
      data.length,
      (index) {
        final item = data[index];

        final total = _toDouble(
          item['total'],
        );

        final category =
            item['category']
                    ?.toString() ??
                'Unknown';

        return PieChartSectionData(
          value: total,

          title:
              category.length > 10
                  ? '${category.substring(0, 10)}...'
                  : category,

          radius: 65,

          color: chartColors[
              index %
                  chartColors.length],

          titleStyle:
              const TextStyle(
            fontSize: 11,

            fontWeight:
                FontWeight.bold,

            color: Colors.white,
          ),
        );
      },
    );

    return PieChart(
      PieChartData(
        centerSpaceRadius: 45,

        sectionsSpace: 4,

        sections: sections,

        pieTouchData:
            PieTouchData(
          enabled: true,
        ),
      ),
    );
  }
}