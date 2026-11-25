let selectedSample=null;
const typeNames={rock_chip:'Rock chip',soil:'Udongo',stream_sediment:'Mchanga wa mto',channel:'Channel',surface:'Sampuli ya uso'};
const sampleCacheKey=()=>`samples:${S.user}:${S.pid}`;
const normalizedId=value=>String(value||'').trim().toUpperCase();
const sampleIdFromRecord=record=>record?.payload?.sample_id||record?.sample_id||null;

async function loadProjects(){
  const selector=$('#projectSelect');
  let projects=[];
  if(navigator.onLine&&S.tok){
    projects=await(await api('/projects')).json();
    await meta(`projects:${S.user}`,projects);
  }else projects=await getMeta(`projects:${S.user}`)||[];
  selector.innerHTML=projects.map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
  if(!projects.length)return;
  if(!projects.some(p=>p.id===S.pid))S.pid=projects[0].id;
  selector.value=S.pid;
}

async function sampleRows(){
  const key=sampleCacheKey();
  let rows=await getMeta(key)||[];
  if(navigator.onLine&&S.tok){
    try{
      const response=await(await api(`/projects/${encodeURIComponent(S.pid)}/samples`)).json();
      rows=response.samples||[];
      await meta(key,rows);
    }catch(error){
      if(!rows.length)throw error;
    }
  }
  const pending=(await q()).filter(record=>record.record_type==='sample');
  const pendingAssays=(await q()).filter(record=>record.record_type==='assay');
  const byId=new Map(rows.map(row=>[normalizedId(row.sample_id),row]));
  for(const record of pending){
    const id=normalizedId(sampleIdFromRecord(record));
    if(id&&!byId.has(id)){
      const payload=record.payload;
      byId.set(id,{sample_id:id,record_uuid:record.record_uuid,sample_type:payload.sample_type,lat:payload.lat,lon:payload.lon,latest_assay:null,qa_status:'not_assessed',attachment_count:0,sync_status:'pending'});
    }
  }
  for(const record of pendingAssays){
    const id=normalizedId(sampleIdFromRecord(record)),row=byId.get(id);
    if(row)row.latest_assay={...record.payload,pending:true};
  }
  return [...byId.values()].sort((a,b)=>a.sample_id.localeCompare(b.sample_id));
}

async function sampleSyncStatus(sample){
  const id=normalizedId(sample.sample_id);
  const pending=(await q()).filter(record=>normalizedId(sampleIdFromRecord(record))===id);
  const rejected=(await all('rejected')).filter(item=>item.owner===S.user&&item.project_id===S.pid&&normalizedId(sampleIdFromRecord(item.record))===id);
  const photos=(await all('photos')).filter(item=>item.owner===S.user&&item.project_id===S.pid&&normalizedId(item.sample_id)===id);
  if(rejected.length)return 'Inahitaji ukaguzi';
  if(pending.length||photos.length)return 'Inasubiri kusawazishwa';
  return sample.sync_status==='synced'?'Imesawazishwa':'Hali haijulikani';
}

async function renderSamples(){
  if(!S.user||!S.pid)return;
  let rows;
  try{rows=await sampleRows()}
  catch(error){$('#sampleList').innerHTML=`<p class="msg">${esc(error.message)}</p>`;return}
  const search=normalizedId($('#sampleSearch').value);
  const kind=$('#sampleTypeFilter').value;
  const visible=rows.filter(row=>(!search||normalizedId(row.sample_id).includes(search))&&(!kind||row.sample_type===kind));
  if(!visible.length){
    $('#sampleList').innerHTML='<p class="note">Hakuna sampuli zinazolingana. Hifadhi sampuli mpya au jaribu kichujio kingine.</p>';
    return;
  }
  const cards=await Promise.all(visible.map(async row=>{
    const status=await sampleSyncStatus(row);
    const conflicting=['conflicting_or_multiple_assays','conflicting_detection_limits'].includes(row.assay_status);
    const assay=conflicting?'Assays zinakinzana — hakuna iliyochaguliwa':row.latest_assay?`${row.latest_assay.value_num} ${row.latest_assay.unit}${row.latest_assay.pending?' (inasubiri)':''}`:'Hakuna assay bado';
    return `<button class="sample-card" data-sample="${esc(row.sample_id)}"><b>${esc(row.sample_id)}</b><span>${esc(typeNames[row.sample_type]||row.sample_type||'Aina haijulikani')} · ${esc(assay)}</span><span class="status">${esc(status)} · QA/QC: ${esc(row.qa_status||'not_assessed')}</span></button>`;
  }));
  $('#sampleList').innerHTML=cards.join('');
}

async function openSample(sampleId,stay=false){
  let row;
  try{row=(await sampleRows()).find(item=>normalizedId(item.sample_id)===normalizedId(sampleId))}
  catch(error){alert(`Sampuli haikuweza kupakiwa: ${error.message}`);return}
  if(!row)return;
  selectedSample=row;
  $('#detailHeading').textContent=`Sampuli ${row.sample_id}`;
  const conflicting=['conflicting_or_multiple_assays','conflicting_detection_limits'].includes(row.assay_status);
  const assay=conflicting?'<br><b>Assay:</b> Kuna matokeo yanayokinzana; hakuna thamani iliyochaguliwa.':row.latest_assay?`<br><b>Assay ya karibuni:</b> ${esc(row.latest_assay.value_num)} ${esc(row.latest_assay.unit)}${row.latest_assay.pending?' (inasubiri)':''}`:'';
  $('#sampleInfo').innerHTML=`<b>Aina:</b> ${esc(typeNames[row.sample_type]||row.sample_type)}<br><b>Eneo:</b> ${Number.isFinite(row.lat)?`${row.lat.toFixed(5)}, ${row.lon.toFixed(5)}`:'halijahifadhiwa'}<br><b>Hali ya usawazishaji:</b> ${esc(await sampleSyncStatus(row))}<br><b>QA/QC:</b> ${esc(row.qa_status||'not_assessed')}<br><b>Picha:</b> ${Number(row.attachment_count||0)}${assay}`;
  $('#assayMessage').textContent='';
  ['#assayValue','#assayLab','#assayCertificate','#assayMethod','#assayBatch','#detectionLimit','#certifiedValue','#duplicateSample'].forEach(id=>$(id).value='');
  $('#assayUnit').value='g/t';
  $('#qaRole').value='primary';
  $('#belowDetection').checked=false;
  $('#tolerance').value='10';
  $('#qaRole').dispatchEvent(new Event('change'));
  show('sampleDetail',stay);
}

function formNumber(id){
  const value=$(id).value.trim();
  return value===''?null:Number(value);
}

async function saveLaterAssay(){
  const error=$('#assayMessage');
  if(!selectedSample){error.textContent='Chagua sampuli kwanza.';return}
  const value=formNumber('#assayValue');
  const role=$('#qaRole').value;
  const below=$('#belowDetection').checked;
  const limit=formNumber('#detectionLimit');
  const certified=formNumber('#certifiedValue');
  const tolerance=formNumber('#tolerance');
  const duplicate=normalizedId($('#duplicateSample').value);
  const unit=$('#assayUnit').value.trim();
  if(value===null||!Number.isFinite(value)||value<0){error.textContent='Weka thamani ya assay isiyo hasi.';return}
  if(!unit){error.textContent='Weka kipimo cha assay.';return}
  if(below&&(limit===null||!Number.isFinite(limit)||limit<0||value>limit)){error.textContent='Chini ya kikomo huhitaji detection limit halali, na thamani isiizidi.';return}
  if(!below&&limit!==null&&(!Number.isFinite(limit)||limit<0)){error.textContent='Detection limit si sahihi.';return}
  if(role==='standard'&&(certified===null||!Number.isFinite(certified)||certified<=0)){error.textContent='Standard inahitaji certified value iliyo chanya.';return}
  if(role==='duplicate'&&(!duplicate||duplicate===normalizedId(selectedSample.sample_id))){error.textContent='Duplicate inahitaji namba ya sampuli nyingine.';return}
  if(tolerance===null||!Number.isFinite(tolerance)||tolerance<=0||tolerance>100){error.textContent='Uvumilivu uwe zaidi ya 0 na usizidi 100%.';return}
  const record=R('assay',{
    sample_id:normalizedId(selectedSample.sample_id),value_num:value,unit,
    lab_name:$('#assayLab').value.trim()||null,certificate_ref:$('#assayCertificate').value.trim()||null,
    method:$('#assayMethod').value.trim()||null,detection_limit:limit,below_detection:below,
    qa_role:role,certified_value:role==='standard'?certified:null,
    duplicate_of_sample_id:role==='duplicate'?duplicate:null,tolerance_pct:tolerance,
    batch_id:$('#assayBatch').value.trim()||null,
  });
  await put('queue',{key:record.record_uuid,record,owner:S.user});
  error.textContent=navigator.onLine?'Matokeo yamehifadhiwa; yanasawazishwa.':'Yamehifadhiwa kwenye kifaa na yatasawazishwa mtandao ukipatikana.';
  await sync();
  await openSample(selectedSample.sample_id,true);
}

async function refreshConflicts(){
  const target=$('#conflictList');
  if(!target||!S.user||!S.pid)return;
  if(!navigator.onLine||!S.tok){
    target.hidden=true;
    return;
  }
  try{
    const conflicts=await(await api(`/projects/${encodeURIComponent(S.pid)}/conflicts`)).json();
    for(const item of await all('conflicts')){
      if(item.owner===S.user&&item.project_id===S.pid){
        const conflictId=item.conflict?.record_uuid;
        if(conflictId)await del('rejected',conflictId);
        await del('conflicts',item.key);
      }
    }
    for(const conflict of conflicts)await put('conflicts',{key:String(conflict.id),owner:S.user,project_id:S.pid,conflict});
  }catch(error){
    if(error.status===403){
      target.hidden=false;
      target.innerHTML='<b>Utatuzi wa migongano</b><p class="note">Unahitaji ruhusa ya reviewer. Mwombe msimamizi au mkaguzi wa mradi ashughulikie conflict.</p>';
      return;
    }
    target.hidden=false;
    target.innerHTML=`<p class="msg">${esc(error.message)}</p>`;
    return;
  }
  const items=(await all('conflicts')).filter(item=>item.owner===S.user&&item.project_id===S.pid);
  target.hidden=!items.length;
  target.innerHTML=items.map(item=>{
    const conflict=item.conflict;
    const payload=JSON.parse(conflict.incoming_json||'{}');
    const sampleId=payload.sample_id||conflict.record_uuid;
    return `<article class="conflict-card"><b>${esc(sampleId)}</b><p>Rekodi ya kifaa inakinzana na seva. Hifadhi toleo la seva au kataa mabadiliko yanayosubiri.</p><button class="btn o" data-resolve="${conflict.id}" data-resolution="keep_server">Hifadhi la seva</button><button class="btn o" data-resolve="${conflict.id}" data-resolution="rejected">Kataa toleo la kifaa</button></article>`;
  }).join('');
}

async function resolveConflict(id,resolution){
  const response=await api(`/projects/${encodeURIComponent(S.pid)}/conflicts/${encodeURIComponent(id)}/resolve`,{
    method:'POST',body:JSON.stringify({resolution}),
  });
  if(response.ok){
    await del('conflicts',String(id));
    await refreshConflicts();
    await sync();
    await renderSamples();
  }
}

function renderGrid(grid){
  const canvas=$('#jobGrid');
  if(!Array.isArray(grid)||!grid.length||!Array.isArray(grid[0])){
    canvas.hidden=true;
    return;
  }
  const rows=grid.length,cols=grid[0].length;
  const values=grid.flat().filter(Number.isFinite);
  if(!values.length){canvas.hidden=true;return}
  const min=Math.min(...values),max=Math.max(...values),cell=12;
  canvas.width=cols*cell;canvas.height=rows*cell;canvas.hidden=false;
  const context=canvas.getContext('2d');
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){
    const value=Number(grid[y][x]);
    const ratio=max===min ? 0.5 : (value-min)/(max-min);
    context.fillStyle=`hsl(${240-240*ratio} 75% 48%)`;
    context.fillRect(x*cell,y*cell,cell,cell);
  }
}

async function runAnalysis(){
  const resultBox=$('#analysisResult');
  const engine=$('#jobEngine').value;
  try{
    if(!navigator.onLine)throw new Error('Uchambuzi unahitaji mtandao; sampuli zako za nje ya mtandao zimehifadhiwa.');
    const analysis=await(await api(`/projects/${encodeURIComponent(S.pid)}/analysis`)).json();
    const types=analysis.trend.available_sample_types||[];
    let sampleType=$('#jobSampleType').value;
    if(types.length>1&&!sampleType)throw new Error('Chagua aina ya sampuli; aina tofauti hazichanganywi.');
    if(!sampleType&&types.length===1)sampleType=types[0];
    if(!sampleType)throw new Error('Hakuna aina ya sampuli yenye assays halali ya g/t.');
    resultBox.textContent='Kazi imetumwa. Inasubiri matokeo…';
    $('#jobGrid').hidden=true;
    const queued=await(await api('/jobs',{method:'POST',body:JSON.stringify({
      project_id:S.pid,engine,params:{sample_type:sampleType},
    })})).json();
    let job=null;
    for(let attempt=0;attempt<90;attempt++){
      job=await(await api(`/jobs/${encodeURIComponent(queued.id)}`)).json();
      if(['done','rejected','failed'].includes(job.status))break;
      await new Promise(resolve=>setTimeout(resolve,1000));
    }
    if(!job||!['done','rejected','failed'].includes(job.status)){
      resultBox.innerHTML=`Kazi ${esc(queued.id)} bado inachakatwa. Fungua tena uchambuzi kuona hali.`;
      return;
    }
    const warnings=job.warnings||job.result?.warnings||[];
    const body=job.status==='done'
      ? `<b>${esc(job.engine)} — imekamilika</b><p>${esc(job.result?.trend?.msg||job.result?.method||'Matokeo yamepatikana.')}</p><p>Sample type: ${esc(sampleType)} · input hash: ${esc(job.input_hash||'')}</p>`
      : `<b>Kazi ${esc(job.status)}</b><p>${esc(job.error||'Hakuna maelezo ya ziada.')}</p>`;
    resultBox.innerHTML=body+(warnings.length?`<p><b>Maonyo:</b><br>${warnings.map(esc).join('<br>')}</p>`:'');
    renderGrid(job.result?.values);
  }catch(error){
    resultBox.innerHTML=`<p class="msg">${esc(error.message)}</p>`;
  }
}

async function logoutSecurely(){
  if(!navigator.onLine){alert('Mtandao unahitajika ili seva ibatilishe session. Data zako za nje ya mtandao zitabaki salama; jaribu tena ukiwa mtandaoni.');return}
  try{
    await api('/auth/logout',{method:'POST',body:JSON.stringify({refresh_token:S.refresh||null})});
    delete S.tok;delete S.refresh;delete S.user;delete S.pid;
    hist=['login'];show('login',1);
  }catch(error){alert(`Hatuwezi kuthibitisha logout: ${error.message}`)}
}

const originalShow=show;
show=(name,back)=>{
  originalShow(name,back);
  if(name==='mysamples')renderSamples();
};
const originalEnsure=ensure;
ensure=async()=>{
  await originalEnsure();
  await loadProjects();
};
const originalSync=sync;
sync=async(...args)=>{
  await originalSync(...args);
  if(!idb||!S.user||!S.pid)return;
  await Promise.all([renderSamples(),refreshConflicts()]);
};

document.addEventListener('chimba-ready',async()=>{
  try{await loadProjects()}catch(error){if(navigator.onLine)$('#qn').textContent=error.message}
  $('#projectSelect').addEventListener('change',async event=>{
    S.pid=event.target.value;
    await sync();
    await renderSamples();
    await refreshConflicts();
  });
  $('#sampleSearch').addEventListener('input',renderSamples);
  $('#sampleTypeFilter').addEventListener('change',renderSamples);
  $('#refreshSamples').addEventListener('click',renderSamples);
  $('#sampleList').addEventListener('click',event=>{
    const button=event.target.closest('[data-sample]');
    if(button)openSample(button.dataset.sample);
  });
  $('#saveAssay').addEventListener('click',saveLaterAssay);
  $('#qaRole').addEventListener('change',()=>{
    const role=$('#qaRole').value;
    if(role!=='primary')$('#belowDetection').checked=false;
    $('#certifiedValue').disabled=role!=='standard';
    $('#duplicateSample').disabled=role!=='duplicate';
    $('#belowDetection').disabled=role!=='primary';
    $('#detectionLimit').disabled=role!=='primary'||!$('#belowDetection').checked;
  });
  $('#belowDetection').addEventListener('change',()=>{
    $('#detectionLimit').disabled=!$('#belowDetection').checked||$('#qaRole').value!=='primary';
  });
  $('#conflictList').addEventListener('click',async event=>{
    const button=event.target.closest('[data-resolve]');
    if(!button)return;
    button.disabled=true;
    try{await resolveConflict(button.dataset.resolve,button.dataset.resolution)}
    catch(error){alert(`Conflict haijatatuliwa: ${error.message}`);button.disabled=false}
  });
  $('#runAnalysis').addEventListener('click',runAnalysis);
  $('#logout').addEventListener('click',logoutSecurely);
  addEventListener('online',()=>{loadProjects().then(refreshConflicts).catch(()=>{})});
  await Promise.all([renderSamples(),refreshConflicts()]);
});
