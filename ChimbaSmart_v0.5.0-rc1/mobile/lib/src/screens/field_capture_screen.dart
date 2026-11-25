import 'package:flutter/material.dart';
import '../services/local_store.dart';
import '../services/location_service.dart';

class FieldCaptureScreen extends StatefulWidget {
  const FieldCaptureScreen({super.key});

  @override
  State<FieldCaptureScreen> createState() => _FieldCaptureScreenState();
}

class _FieldCaptureScreenState extends State<FieldCaptureScreen> {
  final _form = GlobalKey<FormState>();
  final _project = TextEditingController(text: 'default-project');
  final _identifier = TextEditingController();
  final _description = TextEditingController();
  final _value = TextEditingController();
  final _unit = TextEditingController(text: 'g/t');
  final _from = TextEditingController();
  final _to = TextEditingController();
  String _type = 'sample';
  double? _lat;
  double? _lon;
  double? _accuracy;
  bool _saving = false;

  Future<void> _gps() async {
    final position = await LocationService.getCurrentPosition();
    if (!mounted) return;
    setState(() {
      _lat = position?.latitude;
      _lon = position?.longitude;
      _accuracy = position?.accuracy;
    });
    if (position == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('GPS haijapatikana. Ruhusu eneo na ujaribu tena.')),
      );
    }
  }

  Map<String, dynamic> _payload() {
    final common = <String, dynamic>{
      'identifier': _identifier.text.trim(),
      'description': _description.text.trim(),
      'latitude': _lat,
      'longitude': _lon,
      'gps_accuracy_m': _accuracy,
      'captured_at': DateTime.now().toUtc().toIso8601String(),
    };
    if (_type == 'sample') {
      return {...common, 'sample_type': 'rock_chip'};
    }
    if (_type == 'assay') {
      return {
        ...common,
        'sample_id': _identifier.text.trim().toUpperCase(),
        'numeric_value': double.tryParse(_value.text.trim()),
        'unit': _unit.text.trim(),
      };
    }
    if (_type == 'collar') {
      return {...common, 'hole_id': _identifier.text.trim().toUpperCase()};
    }
    if (_type == 'interval') {
      return {
        ...common,
        'hole_id': _identifier.text.trim().toUpperCase(),
        'from_depth_m': double.tryParse(_from.text.trim()),
        'to_depth_m': double.tryParse(_to.text.trim()),
      };
    }
    return {
      ...common,
      'strike_deg': double.tryParse(_value.text.trim()),
      'dip_deg': double.tryParse(_unit.text.trim()),
    };
  }

  Future<void> _save() async {
    if (!_form.currentState!.validate()) return;
    if (_lat == null || _lon == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Pima GPS kabla ya kuhifadhi.')),
      );
      return;
    }
    setState(() => _saving = true);
    try {
      final recordId = await LocalStore.instance.addRecord(
        kind: _type,
        projectId: _project.text.trim(),
        payload: _payload(),
        crs: 'EPSG:4326',
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('$_type imehifadhiwa kwa uhalali; pending sync: $recordId')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Imeshindikana kuhifadhi: $e')),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Fomu ya uwanja')),
      body: Form(
        key: _form,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _project,
              decoration: const InputDecoration(labelText: 'UUID ya mradi'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Mradi unahitajika' : null,
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: _type,
              decoration: const InputDecoration(labelText: 'Aina ya rekodi'),
              items: const [
                DropdownMenuItem(value: 'sample', child: Text('Sampuli ya uso')),
                DropdownMenuItem(value: 'assay', child: Text('Matokeo ya assay')),
                DropdownMenuItem(value: 'collar', child: Text('Collar ya drillhole')),
                DropdownMenuItem(value: 'interval', child: Text('Interval ya drillhole')),
                DropdownMenuItem(value: 'orientation', child: Text('Muundo wa jiolojia')),
              ],
              onChanged: (v) => setState(() => _type = v ?? 'sample'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _identifier,
              decoration: const InputDecoration(labelText: 'Kitambulisho'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Kitambulisho kinahitajika' : null,
            ),
            if (_type == 'assay') ...[
              TextFormField(
                controller: _value,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Kiwango cha assay'),
              ),
              TextFormField(controller: _unit, decoration: const InputDecoration(labelText: 'Kipimo')),
            ],
            if (_type == 'interval') ...[
              TextFormField(
                controller: _from,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Kuanza (m)'),
              ),
              TextFormField(
                controller: _to,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Mwisho (m)'),
              ),
            ],
            if (_type == 'orientation') ...[
              TextFormField(
                controller: _value,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Strike RHR (°)'),
              ),
              TextFormField(
                controller: _unit,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Dip (°)'),
              ),
            ],
            TextFormField(
              controller: _description,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Maelezo'),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: _gps,
              icon: const Icon(Icons.my_location),
              label: Text(_lat == null
                  ? 'Pima GPS'
                  : 'GPS ${_lat!.toStringAsFixed(6)}, ${_lon!.toStringAsFixed(6)}'),
            ),
            if (_accuracy != null)
              Text('Usahihi: ${_accuracy!.toStringAsFixed(1)} m',
                  style: Theme.of(context).textTheme.bodySmall),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: _saving ? null : _save,
              child: Text(_saving ? 'Inahifadhi...' : 'Hifadhi bila mtandao'),
            ),
          ],
        ),
      ),
    );
  }
}
