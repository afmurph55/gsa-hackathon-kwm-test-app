(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const data = window.FUELSUPPLY_DATA;
  if (!data || !Array.isArray(data.cases) || !data.cases.length) {
    $("message").hidden = false;
    $("message").textContent = "No saved observations are available. Start the local dashboard and refresh from EIA.";
    return;
  }
  const label = {
    stocks: "Ending stocks", production: "Net production",
    refinery_blender_production: "Refinery / blender production",
    product_supplied: "Product supplied", imports: "Imports", exports: "Exports",
    net_receipts: "Net receipts", biofuels_production: "Biofuels production",
    stock_change: "Stock change"
  };
  const colors = {stocks:"#146b60", production:"#146b60", refinery_blender_production:"#146b60",
    product_supplied:"#bb8126", imports:"#427da7", exports:"#8c6596",net_receipts:"#527896"};
  const localServer = location.protocol === "http:" && ["localhost", "127.0.0.1"].includes(location.hostname);
  let current, allPeriods = false, busy = false;
  let visible = new Set(["production", "refinery_blender_production", "product_supplied"]);
  const numeric = (value, digits=1) => value == null || !Number.isFinite(value)
    ? "—" : value.toLocaleString("en-US", {minimumFractionDigits:digits,maximumFractionDigits:digits});
  const dateText = (period, frequency) => new Date(period + (frequency === "monthly" ? "-01" : "") + "T12:00:00Z")
    .toLocaleDateString("en-US", {timeZone:"UTC",month:"short",...(frequency === "weekly" ? {day:"numeric"} : {year:"numeric"})});
  const keyOf = q => [q.fuel,q.geography,q.frequency].join("|");
  const metric = id => current.response.metrics.find(m => m.metric === id);
  const observations = id => (metric(id)?.observations || []).slice(0, Number($("history").value));
  const latest = id => observations(id)[0];
  const selectedQuery = () => ({fuel:$("fuel").value, geography:$("geography").value,
    frequency:$("frequency").value, lookback_periods:Number($("history").value)});

  function setMessage(message) {
    $("message").textContent = message;
    $("message").hidden = !message;
  }
  function updateControls(changed) {
    const fuel = $("fuel").value;
    for (const option of $("frequency").options) {
      option.disabled = !data.cases.some(c => c.query.fuel === fuel && c.query.frequency === option.value);
    }
    if ($("frequency").selectedOptions[0].disabled) $("frequency").value = "weekly";
    const frequency = $("frequency").value;
    for (const option of $("geography").options) {
      option.disabled = !data.cases.some(c => c.query.fuel === fuel && c.query.frequency === frequency && c.query.geography === option.value);
    }
    if ($("geography").selectedOptions[0].disabled) $("geography").value = "US";
    current = data.cases.find(c => keyOf(c.query) === keyOf(selectedQuery()));
    if (!current) return;
    if (changed !== "history") allPeriods = false;
    render();
  }

  function renderStats() {
    const s=latest("stocks"), d=latest("product_supplied");
    $("stock-value").textContent = numeric(Number.isFinite(s?.value) ? s.value / 1000 : null, 2);
    $("supplied-value").textContent = numeric(d?.value, 1);
    const aligned=s && d && Number.isFinite(s.value) && Number.isFinite(d.value) && s.period===d.period && s.units==="Thousand Barrels" && d.units==="Thousand Barrels per Day" && d.value>0;
    $("ratio-value").textContent = numeric(aligned ? s.value/d.value : null,2);
    const before = observations("stocks")[1];
    if (Number.isFinite(s?.value) && Number.isFinite(before?.value) && before.value > 0) {
      const difference=(s.value-before.value)/1000, pct=100*(s.value-before.value)/before.value;
      $("stock-change").textContent = `${difference>=0?"+":""}${numeric(difference,2)} million bbl (${pct>=0?"+":""}${numeric(pct,1)}%) vs prior period`;
    } else $("stock-change").textContent="Prior-period comparison unavailable";
  }

  function svgNode(name, attributes={}, text) {
    const node=document.createElementNS("http://www.w3.org/2000/svg",name);
    for(const [key,value] of Object.entries(attributes)) node.setAttribute(key,String(value));
    if(text!==undefined) node.textContent=text;
    return node;
  }
  function chart(containerId, series, units, title) {
    const host=$(containerId); host.replaceChildren();
    const width=Math.max(180,host.clientWidth), height=248;
    const left=54,right=12,top=24,bottom=54;
    const x0=left,x1=width-right,y0=top,y1=height-bottom;
    const svg=svgNode("svg",{viewBox:`0 0 ${width} ${height}`,width,height,role:"img","aria-label":title});
    svg.append(svgNode("title",{},title));
    const values=series.flatMap(s=>s.values).filter(v=>Number.isFinite(v.value));
    if(!values.length){svg.append(svgNode("text",{x:width/2,y:height/2,"text-anchor":"middle"},"Select a series to view observations"));host.append(svg);return;}
    const periods=[...new Set(values.map(v=>v.period))].sort();
    const numbers=values.map(v=>v.value); let min=Math.min(...numbers),max=Math.max(...numbers);
    let pad=(max-min)*.18 || Math.max(Math.abs(max)*.1,1);
    min-=pad;max+=pad;
    const x=period=>periods.length===1?(x0+x1)/2:x0+(periods.indexOf(period)/(periods.length-1))*(x1-x0);
    const y=value=>y1-(value-min)/(max-min)*(y1-y0);
    for(let i=0;i<4;i++) {
      const value=min+(max-min)*i/3,py=y(value);
      svg.append(svgNode("line",{x1:x0,x2:x1,y1:py,y2:py,stroke:"#e8eeeb","stroke-width":1}));
      const tick=Math.abs(value)>=1000?numeric(value/1000,1)+"k":numeric(value,Math.abs(value)<20?1:0);
      svg.append(svgNode("text",{x:x0-9,y:py+3,"text-anchor":"end"},tick));
    }
    const ticks=[...new Set([0,Math.floor((periods.length-1)/2),periods.length-1])];
    for(const index of ticks) {
      const p=periods[index];
      svg.append(svgNode("text",{x:x(p),y:y1+20,"text-anchor":index===0?"start":index===periods.length-1?"end":"middle"},dateText(p,current.query.frequency)));
    }
    svg.append(svgNode("text",{x:(x0+x1)/2,y:height-8,"text-anchor":"middle",class:"axis-title"},current.query.frequency==="weekly"?"Week ending":"Observation month"));
    svg.append(svgNode("text",{x:x0,y:12,class:"axis-title"},units));
    for(const s of series) {
      const rows=s.values.filter(v=>Number.isFinite(v.value)).sort((a,b)=>a.period.localeCompare(b.period));
      svg.append(svgNode("polyline",{points:rows.map(v=>`${x(v.period)},${y(v.value)}`).join(" "),fill:"none",stroke:s.color,"stroke-width":2.4,"stroke-linecap":"round","stroke-linejoin":"round"}));
      for(const row of rows) {
        const mark=svgNode("circle",{cx:x(row.period),cy:y(row.value),r:3.5,fill:s.color});
        mark.append(svgNode("title",{},`${s.name}: ${numeric(row.value,2)} ${units} · ${row.period}`));svg.append(mark);
      }
    }
    const hover=svgNode("line",{x1:x0,x2:x0,y1:y0,y2:y1,stroke:"#9aaba6","stroke-width":1,visibility:"hidden"}); svg.append(hover);
    const tip=document.createElement("div");tip.className="tooltip";tip.hidden=true;
    const overlay=svgNode("rect",{x:x0,y:y0,width:Math.max(1,x1-x0),height:y1-y0,fill:"transparent"});
    function show(event) {
      const bounds=svg.getBoundingClientRect();
      const px=Math.min(x1,Math.max(x0,(event.clientX-bounds.left)*width/bounds.width));
      const index=Math.min(periods.length-1,Math.max(0,Math.round((px-x0)/(x1-x0)*(periods.length-1))));
      const p=periods[index];
      hover.setAttribute("x1",x(p));hover.setAttribute("x2",x(p));hover.setAttribute("visibility","visible");
      tip.textContent=[dateText(p,current.query.frequency),...series.map(s=>{
        const row=s.values.find(v=>v.period===p);return `${s.name}: ${numeric(row?.value,2)}`;
      }),units].join("\n");tip.hidden=false;
      tip.style.left=Math.max(0,Math.min(width-220,px+12))+"px";tip.style.top="24px";
    }
    overlay.addEventListener("pointermove",show);overlay.addEventListener("pointerdown",show);
    overlay.addEventListener("pointerleave",()=>{tip.hidden=true;hover.setAttribute("visibility","hidden");});
    svg.append(overlay);host.append(svg,tip);
  }

  function drawCharts() {
    const stocks=observations("stocks").map(v=>({...v,value:v.value==null?null:v.value/1000}));
    $("stock-period-count").textContent=`${stocks.length} periods`;
    chart("stock-chart",[{name:"Stocks",color:colors.stocks,values:stocks}],"Million barrels","Ending stocks over the selected observation periods");
    const production=metric("production")?"production":"refinery_blender_production";
    const flowIds=[production,"product_supplied"];
    chart("flow-chart",flowIds.filter(id=>visible.has(id)).map(id=>({name:label[id],color:colors[id],values:observations(id)})),"Thousand barrels/day","Production and product supplied; production components may be incomplete");
  }

  function renderTable() {
    const host=$("observation-rows");host.replaceChildren();
    const latestPeriod=current.response.observation_periods[0];
    const rows=current.response.metrics.flatMap(m=>observations(m.metric).map(o=>({...o,metric:m.metric})))
      .filter(o=>allPeriods || o.period===latestPeriod).sort((a,b)=>b.period.localeCompare(a.period)||a.metric.localeCompare(b.metric));
    for(const r of rows) {
      const tr=document.createElement("tr");
      [r.period,label[r.metric]||r.metric,numeric(r.value,2),r.units,`${numeric(r.original_value,2)} ${r.original_units}`].forEach((value,index)=>{
        const td=document.createElement("td");td.textContent=value;if(index===2)td.className="numeric";tr.append(td);
      });host.append(tr);
    }
    $("observation-caption").textContent=allPeriods?`${rows.length} observations across the selected history`:`Latest period · ${latestPeriod} · normalized and original units`;
    $("table-toggle").textContent=allPeriods?"Show latest period":"Show all periods";
    $("table-toggle").setAttribute("aria-pressed",String(allPeriods));
  }

  function render() {
    const q=current.query,r=current.response;
    $("registry-count").textContent=`${data.binding_count} mappings`;
    $("registry-version").textContent=`Version ${data.registry_version}`;
    const p=r.observation_periods[0];
    $("period-label").textContent=p?`${q.frequency==="weekly"?"Week ending":"Observation month"}: ${p} · ${r.observation_periods.length} periods saved`:"No observation periods";
    const retrieved=r.retrieval_timestamp?new Date(r.retrieval_timestamp).toLocaleString("en-US",{timeZone:"America/New_York",month:"short",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"}):"Unavailable";
    $("retrieved-label").textContent=`Retrieved ${retrieved}`;
    $("snapshot-status").textContent="Saved EIA snapshot";
    $("definition").textContent=r.resolved_product_definition||"Exact product definition unavailable";
    renderStats();
    const production=metric("production")?"production":"refinery_blender_production";
    $("flow-legend").replaceChildren();
    for(const id of [production,"product_supplied"]) {
      const button=document.createElement("button");button.type="button";button.setAttribute("aria-pressed",String(visible.has(id)));
      const swatch=document.createElement("span");swatch.className="swatch";swatch.style.background=colors[id];swatch.setAttribute("aria-hidden","true");
      button.append(swatch,document.createTextNode(label[id]));button.addEventListener("click",()=>{visible.has(id)?visible.delete(id):visible.add(id);render();});$("flow-legend").append(button);
    }
    const monthly=q.frequency==="monthly",gas=q.fuel==="finished_gasoline";
    const coverage=document.querySelector(".coverage-note");coverage.classList.toggle("partial",monthly||gas||r.status!=="ok");
    $("coverage-label").textContent=monthly||gas?"Partial coverage":"Verified coverage";
    $("coverage-title").textContent=monthly?"Monthly balance components are incomplete":gas?"Exact finished-gasoline exports are excluded":"Five core supply metrics verified";
    $("coverage-copy").textContent=monthly?"Refinery/blender and biofuels production remain separate. The chart shows the refinery/blender component only; it is not total production. Missing accounting terms prevent a complete reconciliation.":gas?"The upstream export series includes gasoline blending components. It is intentionally excluded from this exact finished-gasoline view. Production is EIA's adjusted refinery/blender net production.":"Production, stocks, product supplied, imports and exports have verified mappings. Public market observations do not establish purchasable supply, spare capacity or forecasts.";
    $("source-list").replaceChildren();
    for(const b of r.source_bindings) {
      const item=document.createElement("div");item.className="source";
      const a=document.createElement("a");a.textContent=label[b.internal_metric_id]||b.internal_metric_id;
      if(new URL(b.source_url).hostname==="www.eia.gov"){a.href=b.source_url;a.target="_blank";a.rel="noopener noreferrer";}
      const detail=document.createElement("span");detail.textContent=`${b.facets.series?.[0]||"EIA series"} · ${b.units} · verified ${b.verified_at.slice(0,10)}`;item.append(a,detail);$("source-list").append(item);
    }
    $("limitations").replaceChildren();
    for(const text of r.limitations){const li=document.createElement("li");li.textContent=text;$("limitations").append(li);}
    $("footer-source").textContent=`Registry ${data.registry_version} · ${r.source_bindings.length} selected mappings`;
    renderTable();drawCharts();
    const available=observations("stocks").length;
    if(!busy) {
      const wanted=Number($("history").value);
      const issues=r.data_quality_diagnostics.filter(x=>!x.startsWith("retrieval_modes"));
      setMessage(!localServer?"Saved snapshot. Filters, charts, CSV and printing work offline. Start the local dashboard to refresh from EIA.":
        issues.some(x=>x.includes("upstream")||x.includes("missing_credentials"))?"Some data could not be refreshed. Review available observations and source coverage.":
        available<wanted?`${available} saved periods available; refresh this selection to request ${wanted}.`:"");
    }
    $("refresh").disabled=!localServer||busy;
  }

  async function refresh() {
    if(busy||!localServer)return;
    busy=true;$("refresh").disabled=true;$("refresh").textContent="Refreshing…";
    for(const id of ["fuel","frequency","geography","history"])$(id).disabled=true;
    setMessage("Retrieving verified EIA series for this selection. The API key stays on the local server.");
    try {
      const q=selectedQuery();
      const response=await fetch("/api/refresh",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(q)});
      const payload=await response.json();
      if(!response.ok)throw new Error(payload.error||"Refresh failed. Retry from the local server.");
      const index=data.cases.findIndex(c=>keyOf(c.query)===keyOf(q));
      if(index<0)throw new Error("The refreshed combination is not in verified coverage.");
      data.cases[index]=payload.case;current=payload.case;
      busy=false;render();$("snapshot-status").textContent="Refreshed from EIA";
      setMessage("This selection was refreshed and saved locally. Other selections retain their own retrieval dates.");
    } catch(error) {busy=false;render();setMessage(error.message||"Refresh failed; previous saved data retained.");}
    finally {busy=false;$("refresh").disabled=false;$("refresh").textContent="Refresh from EIA";
      for(const id of ["fuel","frequency","geography","history"])$(id).disabled=false;}
  }

  function exportCsv() {
    const q=current.query,r=current.response;
    const rows=[["fuel","geography","frequency","period","metric","value","units","original_value","original_units","retrieved_at","source_url"]];
    for(const m of r.metrics)for(const o of observations(m.metric)) {
      const source=r.source_bindings.find(b=>b.internal_metric_id===m.metric);
      rows.push([q.fuel,q.geography,q.frequency,o.period,m.metric,o.value,o.units,o.original_value,o.original_units,r.retrieval_timestamp,source?.source_url||""]);
    }
    const csv=rows.map(row=>row.map(v=>'"'+String(v??"").replaceAll('"','""')+'"').join(",")).join("\r\n");
    const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    const a=document.createElement("a");a.href=url;a.download=`fuelsupply-${q.fuel}-${q.geography}-${q.frequency}.csv`;a.hidden=true;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
  }
  for(const id of ["fuel","frequency","geography","history"])$(id).addEventListener("change",()=>updateControls(id));
  $("refresh").addEventListener("click",refresh);
  $("export-csv").addEventListener("click",exportCsv);
  $("table-toggle").addEventListener("click",()=>{allPeriods=!allPeriods;renderTable();});
  $("print-report").addEventListener("click",()=>window.print());
  new ResizeObserver(()=>{if(current)drawCharts();}).observe($("stock-chart"));
  updateControls("initial");
})();
