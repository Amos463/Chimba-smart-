import 'package:flutter_test/flutter_test.dart';
import 'package:chimbasmart/src/app.dart';
void main(){testWidgets('renders ChimbaSmart home', (tester) async {
 await tester.pumpWidget(const ChimbaSmartApp());
 expect(find.text('ChimbaSmart'),findsOneWidget);
 expect(find.text('GEOLOGICAL FIELD PLATFORM'),findsOneWidget);
});}
