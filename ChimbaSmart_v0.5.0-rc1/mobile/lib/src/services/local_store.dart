import 'dart:convert';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

class LocalStore {
 LocalStore._(); static final instance=LocalStore._(); Database? _db;
 Future<Database> get db async {
  if(_db!=null)return _db!;
  final dir=await getApplicationDocumentsDirectory();
  _db=await openDatabase(p.join(dir.path,'chimbasmart.db'),version:1,
   onCreate:(d,v) async {
    await d.execute('''CREATE TABLE records(
      record_uuid TEXT PRIMARY KEY, project_id TEXT NOT NULL, record_type TEXT NOT NULL,
      payload_json TEXT NOT NULL, created_at_utc TEXT NOT NULL, updated_at_utc TEXT NOT NULL,
      device_id TEXT NOT NULL, source_method TEXT NOT NULL, crs TEXT,
      sync_status TEXT NOT NULL DEFAULT 'pending', server_version INTEGER,
      last_error TEXT, deleted_at_utc TEXT)''');
    await d.execute('CREATE INDEX idx_records_sync ON records(sync_status, created_at_utc)');
    await d.execute('''CREATE TABLE sync_state(
      key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at_utc TEXT NOT NULL)''');
   });
  return _db!;
 }
 Future<void> addRecord({required String kind,required Map<String,dynamic> payload,String projectId='default-project',String deviceId='device-unregistered',String? crs}) async {
  final d=await db; final now=DateTime.now().toUtc().toIso8601String();
  await d.insert('records',{'record_uuid':const Uuid().v4(),'project_id':projectId,'record_type':kind,
   'payload_json':jsonEncode(payload),'created_at_utc':now,'updated_at_utc':now,'device_id':deviceId,
   'source_method':'mobile_manual_or_sensor','crs':crs,'sync_status':'pending'});
 }
 Future<int> countRecords() async => Sqflite.firstIntValue(await (await db).rawQuery('SELECT COUNT(*) FROM records'))??0;
 Future<List<Map<String,dynamic>>> pending({int limit=100}) async => (await db).query('records',where:"sync_status IN ('pending','retry')",orderBy:'created_at_utc',limit:limit);
 Future<void> markStatus(String uuid,String status,{String? error,int? serverVersion}) async => (await db).update('records',{'sync_status':status,'last_error':error,'server_version':serverVersion},where:'record_uuid=?',whereArgs:[uuid]);
}
