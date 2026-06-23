import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

class SummaryChart extends StatelessWidget {
  final List<dynamic> data; // Your JSON list

  const SummaryChart({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return PieChart(
      PieChartData(
        sections: data.map((item) {
          return PieChartSectionData(
            value: item['total'].toDouble(),
            title: item['category'],
            color: Colors.primaries[data.indexOf(item) % Colors.primaries.length],
            radius: 50,
          );
        }).toList(),
      ),
    );
  }
}