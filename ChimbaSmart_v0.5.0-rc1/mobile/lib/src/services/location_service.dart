import 'package:geolocator/geolocator.dart';
class LocationService {
 static Future<Position?> getCurrentPosition() async {
  if(!await Geolocator.isLocationServiceEnabled()) return null;
  var p=await Geolocator.checkPermission();
  if(p==LocationPermission.denied)p=await Geolocator.requestPermission();
  if(p==LocationPermission.denied||p==LocationPermission.deniedForever)return null;
  return Geolocator.getCurrentPosition(locationSettings:const LocationSettings(accuracy:LocationAccuracy.high,timeLimit:Duration(seconds:15)));
 }
}
