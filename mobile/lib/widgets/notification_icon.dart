import 'package:flutter/material.dart';

class NotificationIcon extends StatelessWidget {
  final int count;
  final VoidCallback onTap;

  const NotificationIcon({
    super.key,
    required this.count,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        IconButton(
          icon: const Icon(Icons.notifications),
          onPressed: onTap,
        ),

        if (count > 0)
          Positioned(
            right: 6,
            top: 6,
            child: Container(
              padding: const EdgeInsets.all(5),
              decoration: const BoxDecoration(
                color: Colors.red,
                shape: BoxShape.circle,
              ),
              child: Text(
                count > 9 ? "9+" : "$count",
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                ),
              ),
            ),
          ),
      ],
    );
  }
}