import 'package:flutter/material.dart';
class FeatureTile extends StatelessWidget {
 final IconData icon; final String title,detail;
 const FeatureTile({super.key,required this.icon,required this.title,required this.detail});
 @override Widget build(BuildContext context)=>SizedBox(width:165,child:Card(child:Padding(padding:const EdgeInsets.all(14),child:Column(crossAxisAlignment:CrossAxisAlignment.start,children:[
  Icon(icon,color:const Color(0xFF123F38)),const SizedBox(height:9),Text(title,style:const TextStyle(fontWeight:FontWeight.bold)),const SizedBox(height:4),Text(detail,style:const TextStyle(fontSize:11,color:Colors.black54))
 ]))));
}
