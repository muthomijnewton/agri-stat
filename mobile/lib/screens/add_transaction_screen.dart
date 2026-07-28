import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../services/api_service.dart';

class AddTransactionScreen extends StatefulWidget {
  const AddTransactionScreen({super.key});

  @override
  State<AddTransactionScreen> createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends State<AddTransactionScreen> {
  final ApiService _apiService = ApiService();
  final _formKey = GlobalKey<FormState>();

  // Form fields
  int? _selectedProductId;
  String _transactionType = 'sale';
  final _quantityController = TextEditingController();
  final _unitPriceController = TextEditingController();
  final _notesController = TextEditingController();
  DateTime _transactionDate = DateTime.now();

  List<dynamic> _products = [];
  bool _loadingProducts = true;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _loadProducts();
    // Auto-calculate total when qty or price changes
    _quantityController.addListener(_updateTotal);
    _unitPriceController.addListener(_updateTotal);
  }

  @override
  void dispose() {
    _quantityController.removeListener(_updateTotal);
    _unitPriceController.removeListener(_updateTotal);
    _quantityController.dispose();
    _unitPriceController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _updateTotal() {
    // Triggers a rebuild so the computed total display stays in sync
    if (mounted) setState(() {});
  }

  double get _computedTotal {
    final qty = double.tryParse(_quantityController.text) ?? 0;
    final price = double.tryParse(_unitPriceController.text) ?? 0;
    return qty * price;
  }

  Future<void> _loadProducts() async {
    final products = await _apiService.getProducts();
    if (!mounted) return;
    setState(() {
      _products = products;
      _loadingProducts = false;
    });
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _transactionDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null && mounted) {
      setState(() => _transactionDate = picked);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedProductId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a product.')),
      );
      return;
    }

    setState(() => _submitting = true);

    try {
      final qty = int.parse(_quantityController.text.trim());
      final price = double.parse(_unitPriceController.text.trim());

      await _apiService.createTransaction({
        'product_id': _selectedProductId,
        'transaction_type': _transactionType,
        'quantity': qty,
        'unit_price': price,
        'total_price': double.parse(_computedTotal.toStringAsFixed(2)),
        'transaction_date': DateFormat('yyyy-MM-dd').format(_transactionDate),
        if (_notesController.text.trim().isNotEmpty)
          'notes': _notesController.text.trim(),
      });

      if (!mounted) return;
      Navigator.pop(context, true); // return true so caller can refresh
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to record transaction: ${_errorMessage(e)}'),
          backgroundColor: Colors.red.shade700,
        ),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  String _errorMessage(Object e) {
    // Dig the detail out of a Dio error response if present
    if (e.toString().contains('detail')) {
      final match = RegExp(r'"detail"\s*:\s*"([^"]+)"').firstMatch(e.toString());
      if (match != null) return match.group(1)!;
    }
    return e.toString();
  }

  InputDecoration _inputDecoration(String label, {String? hint}) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Record Transaction'),
        actions: [
          if (_submitting)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Center(child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))),
            ),
        ],
      ),
      body: _loadingProducts
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // ── Product ──
                    DropdownButtonFormField<int>(
                      decoration: _inputDecoration('Product *'),
                      value: _selectedProductId,
                      items: _products.map<DropdownMenuItem<int>>((p) {
                        return DropdownMenuItem<int>(
                          value: p['id'] as int,
                          child: Text(p['name']?.toString() ?? 'Product ${p['id']}'),
                        );
                      }).toList(),
                      onChanged: (val) => setState(() => _selectedProductId = val),
                      validator: (val) => val == null ? 'Select a product' : null,
                    ),

                    const SizedBox(height: 14),

                    // ── Transaction type ──
                    DropdownButtonFormField<String>(
                      decoration: _inputDecoration('Transaction Type *'),
                      value: _transactionType,
                      items: const [
                        DropdownMenuItem(value: 'sale', child: Text('Sale (outgoing)')),
                        DropdownMenuItem(value: 'purchase', child: Text('Purchase (incoming)')),
                      ],
                      onChanged: (val) => setState(() => _transactionType = val!),
                    ),

                    const SizedBox(height: 14),

                    // ── Quantity + Unit Price ──
                    Row(
                      children: [
                        Expanded(
                          child: TextFormField(
                            controller: _quantityController,
                            decoration: _inputDecoration('Quantity *', hint: '0'),
                            keyboardType: TextInputType.number,
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Required';
                              final n = int.tryParse(v);
                              if (n == null || n <= 0) return 'Enter a positive integer';
                              return null;
                            },
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: TextFormField(
                            controller: _unitPriceController,
                            decoration: _inputDecoration('Unit Price (KES) *', hint: '0.00'),
                            keyboardType: const TextInputType.numberWithOptions(decimal: true),
                            validator: (v) {
                              if (v == null || v.isEmpty) return 'Required';
                              final n = double.tryParse(v);
                              if (n == null || n < 0) return 'Enter a valid price';
                              return null;
                            },
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 14),

                    // ── Computed total (read-only) ──
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: theme.dividerColor),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Total', style: theme.textTheme.bodyMedium?.copyWith(color: theme.hintColor)),
                          Text(
                            'KES ${_computedTotal.toStringAsFixed(2)}',
                            style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 14),

                    // ── Date ──
                    InkWell(
                      onTap: _pickDate,
                      borderRadius: BorderRadius.circular(10),
                      child: InputDecorator(
                        decoration: _inputDecoration('Date *'),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(DateFormat('dd MMM yyyy').format(_transactionDate)),
                            const Icon(Icons.calendar_today_outlined, size: 18),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 14),

                    // ── Notes ──
                    TextFormField(
                      controller: _notesController,
                      decoration: _inputDecoration('Notes', hint: 'Optional'),
                      maxLines: 3,
                    ),

                    const SizedBox(height: 24),

                    // ── Submit ──
                    FilledButton(
                      onPressed: _submitting ? null : _submit,
                      style: FilledButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      child: _submitting
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Text('Record Transaction', style: TextStyle(fontSize: 16)),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
