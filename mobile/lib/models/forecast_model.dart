import 'package:json_annotation/json_annotation.dart';

part 'forecast.g.dart';

@JsonSerializable()
class Forecast {
  final int id;
  final int productId;
  final DateTime forecastDate;
  final int predictedDemand;
  final double? confidenceLower;
  final double? confidenceUpper;
  final String? modelType;
  final double? accuracyScore;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Forecast({
    required this.id,
    required this.productId,
    required this.forecastDate,
    required this.predictedDemand,
    this.confidenceLower,
    this.confidenceUpper,
    this.modelType,
    this.accuracyScore,
    required this.createdAt,
    this.updatedAt,
  });

  factory Forecast.fromJson(Map<String, dynamic> json) => _$ForecastFromJson(json);
  Map<String, dynamic> toJson() => _$ForecastToJson(this);
}
