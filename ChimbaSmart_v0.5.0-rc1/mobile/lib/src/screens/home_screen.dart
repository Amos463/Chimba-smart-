import 'package:flutter/material.dart';
import '../services/local_store.dart';
import '../services/location_service.dart';
import '../widgets/feature_tile.dart';
import 'field_capture_screen.dart';
class HomeScreen extends StatefulWidget { const HomeScreen({super.key}); @override State<HomeScreen> createState()=>_HomeScreenState(); }
class _HomeScreenState extends State<HomeScreen> {
  int count=0; String sync='Data huhifadhiwa kwenye kifaa'; bool busy=false;
  @override void initState(){super.initState(); _load();}
  Future<void> _load() async { final n=await LocalStore.instance.countRecords(); if(mounted)setState(()=>count=n); }
  Future<void> _capture() async {
    setState(()=>busy=true);
    try {
      final loc=await LocationService.getCurrentPosition();
      await LocalStore.instance.addRecord(projectId:'default-project',kind:'field_observation', payload:{
        'latitude':loc?.latitude,'longitude':loc?.longitude,'accuracy_m':loc?.accuracy,
        'captured_at':DateTime.now().toUtc().toIso8601String(),
        'note':'Rekodi ya majaribio — hariri kabla ya matumizi ya field'
      });
      await _load();
      if(mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content:Text('Rekodi imehifadhiwa kwenye simu.')));
    } catch(e) { if(mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content:Text('Imeshindikana: $e'))); }
    finally {if(mounted)setState(()=>busy=false);}
  }
  @override Widget build(BuildContext context)=>Scaffold(
    appBar:AppBar(title:const Text('ChimbaSmart'),actions:[IconButton(onPressed:_load,icon:const Icon(Icons.refresh))]),
    body:ListView(padding:const EdgeInsets.all(18),children:[
      Container(padding:const EdgeInsets.all(22),decoration:BoxDecoration(color:const Color(0xFF123F38),borderRadius:BorderRadius.circular(22)),
       child:const Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
        Text('GEOLOGICAL FIELD PLATFORM',style:TextStyle(color:Colors.white70,fontSize:11,letterSpacing:1.3)),
        SizedBox(height:12),Text('Data za jiolojia,\nmahali popote.',style:TextStyle(color:Colors.white,fontSize:27,fontWeight:FontWeight.bold)),
        SizedBox(height:8),Text('Rekodi kwanza. Sawazisha seva mtandao unapopatikana.',style:TextStyle(color:Colors.white70))])),
      const SizedBox(height:16),
      Row(children:[Expanded(child:_metric('Rekodi kwenye kifaa','$count')),const SizedBox(width:10),Expanded(child:_metric('Hali ya mtandao','Offline-first'))]),
      const SizedBox(height:18),FilledButton.icon(onPressed:busy?null:_capture,icon:const Icon(Icons.add_location_alt),label:Text(busy?'Inahifadhi...':'Rekodi eneo la sasa')),
      const SizedBox(height:10),OutlinedButton.icon(
        onPressed:()=>Navigator.of(context).push(MaterialPageRoute(builder:(_)=>const FieldCaptureScreen())),
        icon:const Icon(Icons.assignment_add),label:const Text('Fomu ya sampuli, drillhole au muundo')),
      const SizedBox(height:20),const Text('MODULI ZA UKUSANYAJI',style:TextStyle(fontWeight:FontWeight.w800,letterSpacing:1)),
      const SizedBox(height:10),const Wrap(spacing:10,runSpacing:10,children:[
        FeatureTile(icon:Icons.landscape,title:'Miamba',detail:'Lithology, alteration, mineralization'),
        FeatureTile(icon:Icons.explore,title:'Miundo',detail:'Strike, dip, trend, plunge'),
        FeatureTile(icon:Icons.science,title:'Sampuli',detail:'Sample identity na assay'),
        FeatureTile(icon:Icons.vertical_align_bottom,title:'Drillholes',detail:'Collar, survey, intervals'),
        FeatureTile(icon:Icons.sensors,title:'Geophysics',detail:'Vipimo na raw files'),
        FeatureTile(icon:Icons.map,title:'GIS',detail:'CRS, layers, raster/vector'),
      ]),
      const SizedBox(height:18),Text(sync,style:Theme.of(context).textTheme.bodySmall),
    ]));
  Widget _metric(String a,String b)=>Card(child:Padding(padding:const EdgeInsets.all(16),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[Text(a,style:const TextStyle(color:Colors.black54)),const SizedBox(height:6),Text(b,style:const TextStyle(fontWeight:FontWeight.bold,fontSize:18))])));
}
