import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:painel_integracoes/main.dart';

void main() {
  testWidgets('mostra o titulo do painel e um indicador de carregamento',
      (WidgetTester tester) async {
    await tester.pumpWidget(const PainelIntegracoesApp());

    expect(find.text('Painel de Integrações'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
