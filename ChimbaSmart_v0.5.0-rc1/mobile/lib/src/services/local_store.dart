import 'dart:convert';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

class LocalStore {
  LocalStore._();

  static final instance = LocalStore._();
  Database? _db;

  Future<Database> get db async {
    if (_db != null) return _db!;
    final dir = await getApplicationDocumentsDirectory();
    _db = await openDatabase(
      p.join(dir.path, 'chimbasmart.db'),
      version: 2,
      onCreate: (d, v) async {
        await _createSchema(d);
      },
      onUpgrade: (d, oldVersion, newVersion) async {
        if (oldVersion < 2) {
          await d.execute('''
            CREATE TABLE IF NOT EXISTS attachments(
              attachment_uuid TEXT PRIMARY KEY,
              project_id TEXT NOT NULL,
              sample_id TEXT NOT NULL,
              sample_record_uuid TEXT NOT NULL,
              file_path TEXT NOT NULL,
              filename TEXT NOT NULL,
              media_type TEXT NOT NULL,
              sync_status TEXT NOT NULL DEFAULT 'pending',
              server_attachment_id INTEGER,
              created_at_utc TEXT NOT NULL,
              last_error TEXT
            )
          ''');
          await d.execute(
              'CREATE INDEX IF NOT EXISTS idx_attachments_sync ON attachments(sync_status, created_at_utc)');
          await d.execute(
              'CREATE INDEX IF NOT EXISTS idx_records_project ON records(project_id, record_type)');
        }
      },
    );
    return _db!;
  }

  Future<void> _createSchema(Database d) async {
    await d.execute('''
      CREATE TABLE records(
        record_uuid TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        record_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at_utc TEXT NOT NULL,
        updated_at_utc TEXT NOT NULL,
        device_id TEXT NOT NULL,
        source_method TEXT NOT NULL,
        crs TEXT,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        server_version INTEGER,
        last_error TEXT,
        deleted_at_utc TEXT
      )
    ''');
    await d.execute(
        'CREATE INDEX idx_records_sync ON records(sync_status, created_at_utc)');
    await d.execute(
        'CREATE INDEX idx_records_project ON records(project_id, record_type)');
    await d.execute('''
      CREATE TABLE sync_state(
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at_utc TEXT NOT NULL
      )
    ''');
    await d.execute('''
      CREATE TABLE attachments(
        attachment_uuid TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        sample_id TEXT NOT NULL,
        sample_record_uuid TEXT NOT NULL,
        file_path TEXT NOT NULL,
        filename TEXT NOT NULL,
        media_type TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        server_attachment_id INTEGER,
        created_at_utc TEXT NOT NULL,
        last_error TEXT
      )
    ''');
    await d.execute(
        'CREATE INDEX idx_attachments_sync ON attachments(sync_status, created_at_utc)');
  }

  Future<String> addRecord({
    required String kind,
    required Map<String, dynamic> payload,
    required String projectId,
    String deviceId = 'device-unregistered',
    String? crs,
    String syncStatus = 'pending',
    String? recordUuid,
  }) async {
    final d = await db;
    final now = DateTime.now().toUtc().toIso8601String();
    final uuid = recordUuid ?? const Uuid().v4();
    await d.insert('records', {
      'record_uuid': uuid,
      'project_id': projectId,
      'record_type': kind,
      'payload_json': jsonEncode(payload),
      'created_at_utc': now,
      'updated_at_utc': now,
      'device_id': deviceId,
      'source_method': 'mobile_manual_or_sensor',
      'crs': crs,
      'sync_status': syncStatus,
    });
    return uuid;
  }

  Future<void> addAttachment({
    required String projectId,
    required String sampleId,
    required String sampleRecordUuid,
    required String filePath,
    required String filename,
    required String mediaType,
  }) async {
    final d = await db;
    await d.insert('attachments', {
      'attachment_uuid': const Uuid().v4(),
      'project_id': projectId,
      'sample_id': sampleId,
      'sample_record_uuid': sampleRecordUuid,
      'file_path': filePath,
      'filename': filename,
      'media_type': mediaType,
      'sync_status': 'pending',
      'created_at_utc': DateTime.now().toUtc().toIso8601String(),
    });
  }

  Future<int> countRecords() async =>
      Sqflite.firstIntValue(
          await (await db).rawQuery('SELECT COUNT(*) FROM records')) ??
      0;

  Future<int> countPending() async =>
      Sqflite.firstIntValue(await (await db).rawQuery(
          "SELECT COUNT(*) FROM records WHERE sync_status IN ('pending','retry')")) ??
      0;

  Future<List<Map<String, dynamic>>> pending({
    required String projectId,
    int limit = 100,
  }) async =>
      (await db).query(
        'records',
        where: "project_id=? AND sync_status IN ('pending','retry')",
        whereArgs: [projectId],
        orderBy: 'created_at_utc',
        limit: limit,
      );

  Future<void> upsertPulledRecord({
    required String uuid,
    required String projectId,
    required String kind,
    required Map<String, dynamic> payload,
    required String? crs,
    required int? serverVersion,
  }) async {
    final d = await db;
    final existing = await d.query(
      'records',
      columns: ['sync_status'],
      where: 'record_uuid=?',
      whereArgs: [uuid],
      limit: 1,
    );

    // Never overwrite unsynced field work with a server copy.
    if (existing.isNotEmpty &&
        ['pending', 'retry', 'conflict'].contains(existing.first['sync_status'])) {
      return;
    }

    final now = DateTime.now().toUtc().toIso8601String();
    await d.insert(
      'records',
      {
        'record_uuid': uuid,
        'project_id': projectId,
        'record_type': kind,
        'payload_json': jsonEncode(payload),
        'created_at_utc': now,
        'updated_at_utc': now,
        'device_id': 'server-pull',
        'source_method': 'server_sync',
        'crs': crs,
        'sync_status': 'synced',
        'server_version': serverVersion,
        'last_error': null,
        'deleted_at_utc': null,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> markPulledDeleted(String uuid) async {
    await (await db).update(
      'records',
      {
        'sync_status': 'deleted',
        'deleted_at_utc': DateTime.now().toUtc().toIso8601String(),
      },
      where: 'record_uuid=? AND sync_status NOT IN (?, ?, ?)',
      whereArgs: [uuid, 'pending', 'retry', 'conflict'],
    );
  }

  Future<List<Map<String, dynamic>>> pendingAttachments({int limit = 20}) async =>
      (await db).query('attachments',
          where: "sync_status IN ('pending','retry')",
          orderBy: 'created_at_utc',
          limit: limit);

  Future<void> markStatus(
    String uuid,
    String status, {
    String? error,
    int? serverVersion,
  }) async =>
      (await db).update(
        'records',
        {
          'sync_status': status,
          'last_error': error,
          'server_version': serverVersion,
        },
        where: 'record_uuid=?',
        whereArgs: [uuid],
      );

  Future<void> markAttachmentStatus(
    String uuid,
    String status, {
    String? error,
    int? serverAttachmentId,
  }) async =>
      (await db).update(
        'attachments',
        {
          'sync_status': status,
          'last_error': error,
          'server_attachment_id': serverAttachmentId,
        },
        where: 'attachment_uuid=?',
        whereArgs: [uuid],
      );

  Future<void> setSyncCursor(String projectId, int cursor) async {
    final d = await db;
    await d.insert(
      'sync_state',
      {
        'key': 'server_cursor:$projectId',
        'value': cursor.toString(),
        'updated_at_utc': DateTime.now().toUtc().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<int> syncCursor(String projectId) async {
    final rows = await (await db).query(
      'sync_state',
      where: 'key=?',
      whereArgs: ['server_cursor:$projectId'],
    );
    if (rows.isEmpty) return 0;
    return int.tryParse(rows.first['value'] as String) ?? 0;
  }
}
