import 'package:json_annotation/json_annotation.dart';

part 'transaction.g.dart';

@JsonSerializable()
class Transaction {
  final int id;
  final int productId;
  final int? userId;
  final int quantity;
  final double unitPrice;
  final double totalPrice;
  final DateTime transactionDate;
  final String? notes;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Transaction({
    required this.id,
    required this.productId,
    this.userId,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
    required this.transactionDate,
    this.notes,
    required this.createdAt,
    this.updatedAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) => _$TransactionFromJson(json);
  Map<String, dynamic> toJson() => _$TransactionToJson(this);
}
