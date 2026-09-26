import 'package:flutter/material.dart';

import 'screens/health_dashboard_screen.dart';
import 'services/api_client.dart';

void main() {
  runApp(const PainelIntegracoesApp());
}

class PainelIntegracoesApp extends StatelessWidget {
  const PainelIntegracoesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Painel de Integrações',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: HealthDashboardScreen(apiClient: ApiClient()),
    );
  }
}
