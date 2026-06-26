import 'package:flutter/material.dart';

import '../services/api_service.dart';

class AddProductScreen extends StatefulWidget {
  const AddProductScreen({super.key});

  @override
  State<AddProductScreen> createState() =>
      _AddProductScreenState();
}

class _AddProductScreenState
    extends State<AddProductScreen> {
  final _formKey =
      GlobalKey<FormState>();

  final ApiService _apiService =
      ApiService();

  final TextEditingController
      _nameController =
      TextEditingController();

  final TextEditingController
      _categoryController =
      TextEditingController();

  final TextEditingController
      _unitController =
      TextEditingController();

  final TextEditingController
      _priceController =
      TextEditingController();

  bool _saving = false;

  Future<void> _saveProduct() async {
    if (!_formKey.currentState!
        .validate()) {
      return;
    }

    try {
      setState(() {
        _saving = true;
      });

      final result =
          await _apiService.createProduct({
        "name":
            _nameController.text.trim(),

        "category":
            _categoryController.text.trim(),

        "unit":
            _unitController.text.trim(),

        "unit_price": double.parse(
          _priceController.text.trim(),
        ),
      });

      if (!mounted) return;

      if (result != null) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(
          const SnackBar(
            content:
                Text("Product added"),
            backgroundColor:
                Colors.green,
          ),
        );

        Navigator.pop(
          context,
          true,
        );
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(
          const SnackBar(
            content: Text(
              "Failed to save product",
            ),
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(
        SnackBar(
          content:
              Text("Error: $e"),
          backgroundColor:
              Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _saving = false;
        });
      }
    }
  }

  InputDecoration _input(
    String label,
    IconData icon,
  ) {
    return InputDecoration(
      labelText: label,

      prefixIcon: Icon(icon),

      border: OutlineInputBorder(
        borderRadius:
            BorderRadius.circular(14),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title:
            const Text("Add Product"),
      ),

      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding:
                const EdgeInsets.all(20),

            child: ConstrainedBox(
              constraints:
                  const BoxConstraints(
                maxWidth: 600,
              ),

              child: Card(
                elevation: 6,

                shape:
                    RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(
                    20,
                  ),
                ),

                child: Padding(
                  padding:
                      const EdgeInsets.all(
                    24,
                  ),

                  child: Form(
                    key: _formKey,

                    child: Column(
                      crossAxisAlignment:
                          CrossAxisAlignment
                              .stretch,

                      children: [
                        const Icon(
                          Icons.inventory_2,
                          size: 70,
                          color:
                              Color(
                            0xFF2E7D32,
                          ),
                        ),

                        const SizedBox(
                          height: 12,
                        ),

                        const Text(
                          "New Product",
                          textAlign:
                              TextAlign.center,
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight:
                                FontWeight.bold,
                          ),
                        ),

                        const SizedBox(
                          height: 24,
                        ),

                        TextFormField(
                          controller:
                              _nameController,

                          decoration:
                              _input(
                            "Product Name",
                            Icons.agriculture,
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .trim()
                                    .isEmpty) {
                              return "Enter product name";
                            }

                            return null;
                          },
                        ),

                        const SizedBox(
                          height: 16,
                        ),

                        TextFormField(
                          controller:
                              _categoryController,

                          decoration:
                              _input(
                            "Category",
                            Icons.category,
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .trim()
                                    .isEmpty) {
                              return "Enter category";
                            }

                            return null;
                          },
                        ),

                        const SizedBox(
                          height: 16,
                        ),

                        TextFormField(
                          controller:
                              _unitController,

                          decoration:
                              _input(
                            "Unit",
                            Icons.scale,
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .trim()
                                    .isEmpty) {
                              return "Enter unit";
                            }

                            return null;
                          },
                        ),

                        const SizedBox(
                          height: 16,
                        ),

                        TextFormField(
                          controller:
                              _priceController,

                          keyboardType:
                              const TextInputType.numberWithOptions(
                            decimal: true,
                          ),

                          decoration:
                              _input(
                            "Unit Price (KES)",
                            Icons.attach_money,
                          ),

                          validator:
                              (value) {
                            if (value ==
                                    null ||
                                value
                                    .trim()
                                    .isEmpty) {
                              return "Enter price";
                            }

                            if (double.tryParse(
                                    value) ==
                                null) {
                              return "Invalid price";
                            }

                            return null;
                          },
                        ),

                        const SizedBox(
                          height: 28,
                        ),

                        SizedBox(
                          height: 54,

                          child:
                              ElevatedButton.icon(
                            onPressed:
                                _saving
                                    ? null
                                    : _saveProduct,

                            icon:
                                _saving
                                    ? const SizedBox(
                                        height:
                                            20,
                                        width:
                                            20,
                                        child:
                                            CircularProgressIndicator(
                                          strokeWidth:
                                              2,
                                        ),
                                      )
                                    : const Icon(
                                        Icons.save,
                                      ),

                            label: Text(
                              _saving
                                  ? "Saving..."
                                  : "Save Product",
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _categoryController.dispose();
    _unitController.dispose();
    _priceController.dispose();

    super.dispose();
  }
}