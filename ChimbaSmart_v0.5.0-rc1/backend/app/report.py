import html, datetime
from .geo import compass

def _svg(rows, w=520, h=360):
    if not rows: return ""
    xs, ys = [r["e"] for r in rows], [r["n"] for r in rows]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
    dx,dy=max(x1-x0,1.0),max(y1-y0,1.0)
    scale=min((w-80)/dx,(h-90)/dy)
    ox=w/2-(x0+x1)/2*scale; oy=h/2+(y0+y1)/2*scale
    s=[]
    for r in rows:
        col="#777" if r["grade"] is None else "#c0392b" if r["grade"]<.5 else "#e0a800" if r["grade"]<2 else "#1e8449"
        cx,cy=ox+r["e"]*scale,oy-r["n"]*scale
        s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{col}"/><text x="{cx+8:.1f}" y="{cy+3:.1f}" font-size="9">{html.escape(r.get("sample_id",r.get("hole_id","")))}</text>')
    bar_px=min(90,max(20,90))
    bar_m=bar_px/scale if scale else 0
    s.append(f'<path d="M{w-40} 55 V25 M{w-48} 34 L{w-40} 25 L{w-32} 34" stroke="#111" fill="none" stroke-width="2"/><text x="{w-45}" y="18" font-size="10">N</text>')
    s.append(f'<path d="M30 {h-25} h{bar_px}" stroke="#111" stroke-width="3"/><text x="30" y="{h-30}" font-size="9">{bar_m:.0f} m</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="border:1px solid #999">{"".join(s)}</svg>'

def build_html(user, rows, tr, plane, qa_checks=None, input_hash=None):
    tb = "".join(f'<tr><td>{html.escape(r.get("sample_id",r.get("hole_id","")))}</td><td>{html.escape(r["kind"])}</td><td>{r.get('depth') if r.get('depth') is not None else '—'}</td><td>{html.escape(r["rock"])}</td><td>{"" if r["grade"] is None else r["grade"]}</td></tr>' for r in rows)
    t = f'Madini yanaongezeka upande wa <b>{compass(tr["bearing"])}</b> ({tr["bearing"]:.0f}°), uhakika: {tr["confidence"]}.' if tr.get("ok") else tr.get("msg", "")
    p = f'Strike {plane["strike"]:.0f}°, Dip {plane["dip"]:.0f}° kuelekea {compass(plane["dip_dir"])}.' if plane else "Data hazitoshi kukadiria strike/dip."
    qa_checks=qa_checks or []
    qa_rows="".join(f"<tr><td>{html.escape(str(q.get('sample_id','')))}</td><td>{html.escape(str(q.get('role','')))}</td><td>{html.escape(str(q.get('status','')))}</td><td>{html.escape(str(q.get('detail','')))}</td></tr>" for q in qa_checks)
    qa_html=f"<h3>QA/QC</h3><table><tr><th>Sampuli</th><th>Role</th><th>Hali</th><th>Maelezo</th></tr>{qa_rows}</table>" if qa_checks else "<p class=n>QA/QC haijafanyiwa tathmini kwenye data hii.</p>"
    provenance=f"<p class=n>Input hash: {html.escape(str(input_hash))}</p>" if input_hash else ""
    method=f"<p class=n>Trend method: {html.escape(str(tr.get('method','not available')))}; sampuli zilizotumika: {tr.get('n_used',tr.get('n','—'))}; outliers excluded: {tr.get('outliers_excluded',0)}; sample type: {html.escape(str(tr.get('sample_type','—')))}</p>"
    return f"""<html><meta charset=utf-8><style>body{{font-family:sans-serif;margin:30px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #bbb;padding:5px;font-size:12px}}h1{{color:#0f4c47}}.n{{color:#666;font-size:11px}}</style>
<h1>Ripoti ya Sampuli</h1><p>Mtumiaji: {html.escape(user)} | Tarehe: {datetime.date.today()}</p>{_svg(rows)}
<h3>Mwelekeo</h3><p>{t}</p><p>{p}</p>{method}{qa_html}{provenance}<h3>Sampuli za uso</h3>
<table><tr><th>Namba ya sampuli</th><th>Aina</th><th>Kina (m)</th><th>Mwamba</th><th>g/t</th></tr>{tb}</table>
<p class=n>Ripoti hii ni muhtasari wa data zilizowekwa na mtumiaji. Si makadirio ya rasilimali (si JORC/NI 43-101). Makadirio yanategemea idadi na ubora wa sampuli.</p></html>"""

def to_pdf(doc):
    try:
        from weasyprint import HTML
        return HTML(string=doc).write_pdf(), "application/pdf"
    except Exception as exc:
        raise RuntimeError("PDF engine haipatikani au imeshindwa; ripoti haijatolewa kama PDF.") from exc
