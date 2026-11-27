import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:chimbasmart/src/app.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late Directory testDirectory;

  setUpAll(() async {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;

    testDirectory = await Directory.systemTemp.createTemp(
      'chimbasmart_test_',
    );

    TestDefaultBinaryMessengerBinding
        .instance.defaultBinaryMessenger
        .setMockMethodCallHandler(
      const MethodChannel('plugins.flutter.io/path_provider'),
      (call) async {
        if (call.method == 'getApplicationDocumentsDirectory') {
          return testDirectory.path;
        }
        throw MissingPluginException(
          'Unsupported path_provider method: ${call.method}',
        );
      },
    );
  });

  testWidgets('renders ChimbaSmart home', (tester) async {
    await tester.pumpWidget(const ChimbaSmartApp());
    await tester.pumpAndSettle();

    expect(find.text('ChimbaSmart'), findsOneWidget);
    expect(find.text('GEOLOGICAL FIELD PLATFORM'), findsOneWidget);
    expect(
      find.text('Fomu ya sampuli, drillhole au muundo'),
      findsOneWidget,
    );
  });
}
