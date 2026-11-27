import 'package:flutter_test/flutter_test.dart';
import 'package:chimbasmart/src/app.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('renders ChimbaSmart home', (tester) async {
    await tester.pumpWidget(const ChimbaSmartApp());

    // Allow asynchronous local-storage initialization to complete.
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 100));

    expect(find.text('ChimbaSmart'), findsOneWidget);
    expect(find.text('GEOLOGICAL FIELD PLATFORM'), findsOneWidget);
    expect(
      find.text('Fomu ya sampuli, drillhole au muundo'),
      findsOneWidget,
    );
  });
}
