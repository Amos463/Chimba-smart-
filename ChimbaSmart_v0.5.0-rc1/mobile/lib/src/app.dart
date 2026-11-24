import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
const forest = Color(0xFF123F38);
class ChimbaSmartApp extends StatelessWidget {
  const ChimbaSmartApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'ChimbaSmart',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(useMaterial3: true, colorScheme: ColorScheme.fromSeed(seedColor: forest),
      scaffoldBackgroundColor: const Color(0xFFF4F7F5), cardTheme: CardThemeData(
        color: Colors.white, elevation: 0, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)))),
    home: const HomeScreen(),
  );
}
