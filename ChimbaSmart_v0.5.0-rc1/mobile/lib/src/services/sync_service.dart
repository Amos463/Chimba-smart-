import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'local_store.dart';

/// Foreground sync primitive. The caller should invoke it when connectivity is
/// available; platform background scheduling is deliberately not assumed.
class SyncService {
 SyncService({required String baseUrl}) : _dio=Dio(BaseOptions(baseUrl:baseUrl,connectTimeout:const Duration(seconds:15),receiveTimeout:const Duration(seconds:30)));
 final Dio _dio;
 static const _secure=FlutterSecureStorage();
 Future<void> saveToken(String token)=>_secure.write(key:'access_token',value:token);
 Future<String?> _token()=>_secure.read(key:'access_token');

 Future<void> login(String username,String password) async {
  final r=await _dio.post('/auth/login',data:{'username':username,'password':password});
  await saveToken(r.data['access_token'] as String);
 }
 Future<int> pushPending({required String projectId, int batchSize=50}) async {
  final token=await _token();
  if(token==null) throw StateError('Mtumiaji hajaingia kwenye mfumo.');
  final rows=await LocalStore.instance.pending(limit:batchSize);
  if(rows.isEmpty)return 0;
  final records=<Map<String,dynamic>>[];
  for(final row in rows) {
   final payload=jsonDecode(row['payload_json'] as String) as Map<String,dynamic>;
   final canonical=jsonEncode(_sortMap(payload));
   final hash=sha256.convert(utf8.encode(canonical)).toString();
   records.add({
    'record_uuid':row['record_uuid'],'project_id':row['project_id'],'record_type':row['record_type'],
    'payload':payload,'created_at_utc':row['created_at_utc'],'updated_at_utc':row['updated_at_utc'],
    'device_id':row['device_id'],'source_method':row['source_method'],'crs':row['crs'],'content_hash':hash,
   });
  }
  final response=await _dio.post('/sync/push',data:{'records':records},
   options:Options(headers:{'Authorization':'Bearer $token'}));
  final acks=(response.data['accepted'] as List).cast<Map<String,dynamic>>();
  for(final ack in acks) {
   final status=ack['status'] as String;
   final uuid=ack['record_uuid'] as String;
   await LocalStore.instance.markStatus(uuid,
    status=='accepted'||status=='duplicate'?'synced':status=='conflict'?'conflict':(status=='invalid'&&ack['retry']!=true)?'rejected':'retry',
    error:ack['detail'] as String?,
    serverVersion:ack['server_version'] as int?);
  }
  return acks.where((a)=>a['status']=='accepted'||a['status']=='duplicate').length;
 }
 Map<String,dynamic> _sortMap(Map<String,dynamic> map) {
  final keys=map.keys.toList()..sort();
  return {for(final k in keys) k:map[k]};
 }
}
