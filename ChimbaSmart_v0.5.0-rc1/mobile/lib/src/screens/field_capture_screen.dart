import 'package:flutter/material.dart';
import '../services/local_store.dart';
import '../services/location_service.dart';

class FieldCaptureScreen extends StatefulWidget {
  final String initialType;
  const FieldCaptureScreen({super.key, this.initialType = 'sample'});

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
  final _dip = TextEditingController();
  final _from = TextEditingController();
  final _to = TextEditingController();
  final _depth = TextEditingController();
  final _lithology = TextEditingController();
  String _type = 'sample';

  @override
  void initState() {
    super.initState();
    _type = widget.initialType;
  }
  double? _lat;
  double? _lon;
  double? _accuracy;
  bool _saving = false;

  Future<void> _gps() async {
    try {
      final position = await LocationService.getCurrentPosition();
      if (!mounted) return;

      setState(() {
        _lat = position?.latitude;
        _lon = position?.longitude;
        _accuracy = position?.accuracy;
      });

      if (position == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('GPS haijapatikana. Ruhusu eneo na ujaribu tena.'),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('GPS imeshindikana: $e')),
      );
    }
  }

  Map<String, dynamic> _payload() {
    final id = _identifier.text.trim();
    final description = _description.text.trim();

    final common = <String, dynamic>{
      'latitude': _lat,
      'longitude': _lon,
            'lat': _lat,
      'lon': _lon,
'gps_accuracy_m': _accuracy,
      'captured_at': DateTime.now().toUtc().toIso8601String(),
    };

    switch (_type) {
      case 'sample':
        return {
          ...common,
          'sample_id': id.toUpperCase(),
          'sample_type': 'rock_chip',
          'lithology': _lithology.text.trim().isEmpty
              ? null : _lithology.text.trim(),
          'description': description,
          'location_method': 'phone_gps',
        };
      case 'assay':
        return {
          ...common,
          'sample_id': id.toUpperCase(),
          'value_num': double.tryParse(_value.text.trim()),
          'unit': _unit.text.trim(),
          'qa_role': 'primary',
        };
      case 'collar':
        return {
          ...common,
          'hole_id': id.toUpperCase(),
          'kind': 'pit',
          'depth_m': double.tryParse(_depth.text.trim()),
          'lat': _lat,
          'lon': _lon,
          'gps_accuracy_m': _accuracy,
        };
      case 'interval':
        return {
          ...common,
          'hole_id': id.toUpperCase(),
          'from_m': double.tryParse(_from.text.trim()),
          'to_m': double.tryParse(_to.text.trim()),
          'kind': 'lithology',
          'value_text': description,
        };
      case 'orientation':
        return {
          ...common,
          'lat': _lat,
          'lon': _lon,
          'strike_deg': double.tryParse(_value.text.trim()),
          'dip_deg': double.tryParse(_dip.text.trim()),
          'kind': 'compass',
        };
      case 'lithology':
        return {
          ...common,
          'identifier': id,
          'lithology': _lithology.text.trim(),
          'description': description,
          'record_subtype': 'surface_lithology',
        };
      case 'geophysics_observation':
      case 'gis_feature':
        return {
          ...common,
          'identifier': id,
          'description': description,
          'value': _value.text.trim(),
          'unit': _unit.text.trim(),
          'record_subtype': _type,
          'status': 'raw_field_observation',
        };
      default:
        throw StateError('Aina ya rekodi haitambuliki: $_type');
    }
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
  void dispose() {
    _project.dispose();
    _identifier.dispose();
    _description.dispose();
    _value.dispose();
    _unit.dispose();
    _dip.dispose();
    _from.dispose();
    _to.dispose();
    _depth.dispose();
    _lithology.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Rekodi: ${_type.toUpperCase()}')),
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
                DropdownMenuItem(value: 'lithology', child: Text('Maelezo ya miamba')),
                DropdownMenuItem(value: 'geophysics_observation', child: Text('Rekodi ya geophysics')),
                DropdownMenuItem(value: 'gis_feature', child: Text('Rekodi ya GIS')),
              ],
              onChanged: (v) => setState(() => _type = v ?? 'sample'),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _identifier,
              decoration: const InputDecoration(labelText: 'Kitambulisho'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Kitambulisho kinahitajika' : null,
            ),
            if (_type == 'sample' || _type == 'lithology') ...[
              TextFormField(
                controller: _lithology,
                decoration: const InputDecoration(
                    labelText: 'Aina ya mwamba / Lithology'),
              ),
            ],
            if (_type == 'collar') ...[
              TextFormField(
                controller: _depth,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                    labelText: 'Kina cha shimo (m)'),
                validator: (v) {
                  if (_type != 'collar') return null;
                  final n = double.tryParse(v ?? '');
                  return n == null || n <= 0 ? 'Weka kina sahihi' : null;
                },
              ),
            ],
            if (_type == 'geophysics_observation' || _type == 'gis_feature') ...[
              TextFormField(
                controller: _value,
                decoration: const InputDecoration(
                    labelText: 'Thamani / jina la layer (hiari)'),
              ),
              TextFormField(
                controller: _unit,
                decoration: const InputDecoration(
                    labelText: 'Kipimo au aina ya data'),
              ),
            ],
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
                validator: (v) => double.tryParse(v ?? '') == null
                    ? 'Weka kina cha kuanzia' : null,
              ),
              TextFormField(
                controller: _to,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Mwisho (m)'),
                validator: (v) {
                  final from = double.tryParse(_from.text);
                  final to = double.tryParse(v ?? '');
                  return from == null || to == null || to <= from
                      ? 'Kina cha mwisho lazima kizidi cha mwanzo' : null;
                },
              ),
            ],
            if (_type == 'orientation') ...[
              TextFormField(
                controller: _value,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Strike RHR (°)'),
              ),
              TextFormField(
                controller: _dip,
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
