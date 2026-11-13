import { useRef, useState } from "react";
import { Aperture, ArrowUpRight, AudioLines, Check, ChevronDown, Clapperboard, Film, ImagePlus, Layers3, LoaderCircle, LockKeyhole, Music2, MonitorPlay, Plus, Settings2, ShieldCheck, Sparkles, Upload, Youtube, X } from "lucide-react";

const styles = [
  ["Photorealistic", "Natural live-action footage"],
  ["Cinematic", "Film lighting and camera movement"],
  ["Old Money", "Quiet luxury and timeless tailoring"],
  ["Documentary", "Observational, authentic scenes"],
  ["Commercial", "Polished premium advertising"],
  ["Modern Minimal", "Clean lines and restrained colour"],
  ["Anime", "Stylised animation"],
  ["Custom", "Describe your own visual direction"]
];
const languages = ["English", "Dutch", "Spanish", "French", "German"];
const ratios = [{label:"Vertical · 9:16",value:"9:16"},{label:"Landscape · 16:9",value:"16:9"},{label:"Square · 1:1",value:"1:1"},{label:"Classic · 4:3",value:"4:3"}];

function Field({label,children,hint}) {
  return <label className="field"><span className="field-label">{label}</span>{children}{hint&&<small className="hint">{hint}</small>}</label>;
}
function UploadTile({title,subtitle,file,onFile}) {
  const ref=useRef(null);
  const preview=file&&file.type.startsWith("image/")?URL.createObjectURL(file):null;
  return <div className={"upload-tile "+(file?"has-file":"")} onClick={()=>ref.current?.click()} role="button" tabIndex={0} onKeyDown={e=>e.key==="Enter"&&ref.current?.click()}>
    <input ref={ref} type="file" accept="image/*" hidden onChange={e=>onFile(e.target.files?.[0]||null)}/>
    {file?<><div className="file-preview">{preview?<img src={preview} alt={title}/>:<ImagePlus/>}</div><span className="upload-name">{file.name}</span><button className="remove-file" onClick={e=>{e.stopPropagation();onFile(null)}} aria-label="Remove file"><X size={14}/></button></>:<><span className="upload-icon"><ImagePlus size={19}/></span><strong>{title}</strong><small>{subtitle}</small><span className="upload-action"><Plus size={13}/> Add image</span></>}
  </div>;
}

export default function App() {
  const [prompt,setPrompt]=useState("");
  const [script,setScript]=useState("");
  const [language,setLanguage]=useState("English");
  const [duration,setDuration]=useState(30);
  const [ratio,setRatio]=useState("9:16");
  const [resolution,setResolution]=useState("720p");
  const [style,setStyle]=useState("Photorealistic");
  const [customStyle,setCustomStyle]=useState("");
  const [voice,setVoice]=useState(true);
  const [captions,setCaptions]=useState(true);
  const [music,setMusic]=useState(false);
  const [startFrame,setStartFrame]=useState(null);
  const [endFrame,setEndFrame]=useState(null);
  const [scriptFile,setScriptFile]=useState(null);
  const [busy,setBusy]=useState(false);
  const [notice,setNotice]=useState("");
  const [activeTab,setActiveTab]=useState("create");
  const [advanced,setAdvanced]=useState(false);
  const canSubmit=prompt.trim().length>0&&!busy;
  const durationLabel=duration<60?duration+" sec":Math.floor(duration/60)+" min"+(duration%60?" "+(duration%60)+" sec":"");

  async function generate() {
    if(!canSubmit)return;
    setBusy(true);setNotice("");
    try {
      const body=new FormData();
      body.append("settings",JSON.stringify({prompt,script,language,duration_seconds:duration,aspect_ratio:ratio,resolution,style,custom_style:customStyle,voiceover:voice,captions,music}));
      if(scriptFile)body.append("script_file",scriptFile);
      if(startFrame)body.append("start_frame",startFrame);
      if(endFrame)body.append("end_frame",endFrame);
      const response=await fetch("/api/generate",{method:"POST",body});
      const data=await response.json().catch(()=>({}));
      if(!response.ok)throw new Error(data.message||"The generation service is not connected yet.");
      setNotice(data.message||"Your job has been queued.");
    } catch(error) { setNotice(error.message||"Could not reach the generation service."); }
    finally {setBusy(false);}
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Aperture size={21}/></div><div><b>GENTLEMAN</b><span>VIDEO STUDIO</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>
        <button className={activeTab==="create"?"nav-item active":"nav-item"} onClick={()=>setActiveTab("create")}><Sparkles size={17}/> Create video <span className="nav-dot"/></button>
        <button className={activeTab==="library"?"nav-item active":"nav-item"} onClick={()=>setActiveTab("library")}><Layers3 size={17}/> My library</button>
        <button className={activeTab==="youtube"?"nav-item active":"nav-item"} onClick={()=>setActiveTab("youtube")}><Youtube size={17}/> YouTube channel</button>
      </nav>
      <div className="sidebar-bottom"><div className="private-card"><ShieldCheck size={16}/><div><b>Private workspace</b><small>Access protection will be configured before launch.</small></div></div><div className="profile"><div className="avatar">GS</div><div><b>Studio owner</b><small>Personal workspace</small></div><Settings2 size={16}/></div></div>
    </aside>
    <main className="main-area">
      <header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <b>{activeTab==="create"?"Create video":activeTab==="library"?"My library":"YouTube channel"}</b></div><div className="top-actions"><span className="engine-status"><i/> Engine setup pending</span><button className="icon-button" title="Settings"><Settings2 size={18}/></button></div></header>
      {activeTab==="create"?<div className="content">
        <div className="page-heading"><div><div className="eyebrow"><Sparkles size={13}/> AI VIDEO WORKSPACE</div><h1>Bring your vision <em>to life.</em></h1><p>Describe the video. Shape every detail. Let the studio handle the production.</p></div><div className="heading-chip"><LockKeyhole size={14}/> Private by design</div></div>
        <div className="studio-grid">
          <section className="panel creation-panel">
            <div className="panel-heading"><div><span className="step">01</span><div><h2>Creative brief</h2><p>Start with an idea or provide a complete script.</p></div></div><span className="required">PROMPT REQUIRED</span></div>
            <Field label="What should we create?"><textarea className="prompt-input" value={prompt} onChange={e=>setPrompt(e.target.value)} placeholder="A confident gentleman walks through a quiet European city at golden hour. Slow cinematic camera movement, natural light, refined wardrobe..." rows={5}/></Field>
            <div className="script-header"><span className="field-label">SCRIPT <i>OPTIONAL</i></span><label className="text-upload"><Upload size={14}/> Upload file<input type="file" accept=".txt,.md,.srt,.docx,.pdf" hidden onChange={e=>setScriptFile(e.target.files?.[0]||null)}/></label></div>
            <textarea className="script-input" value={script} onChange={e=>setScript(e.target.value)} placeholder="Paste your narration or scene-by-scene script here..." rows={4}/>
            {scriptFile&&<div className="attached-file"><Film size={14}/>{scriptFile.name}<button onClick={()=>setScriptFile(null)}><X size={13}/></button></div>}
            <div className="section-divider"/>
            <div className="panel-heading compact"><div><span className="step">02</span><div><h2>Video settings</h2><p>Choose the format and visual direction.</p></div></div></div>
            <div className="form-grid">
              <Field label="Video language"><select value={language} onChange={e=>setLanguage(e.target.value)}>{languages.map(v=><option key={v}>{v}</option>)}</select></Field>
              <Field label="Aspect ratio"><select value={ratio} onChange={e=>setRatio(e.target.value)}>{ratios.map(v=><option value={v.value} key={v.value}>{v.label}</option>)}</select></Field>
              <Field label="Resolution"><select value={resolution} onChange={e=>setResolution(e.target.value)}><option>480p</option><option>720p</option><option>1080p</option></select></Field>
              <Field label="Video length"><div className="duration-control"><input type="range" min="10" max="300" step="5" value={duration} onChange={e=>setDuration(Number(e.target.value))}/><strong>{durationLabel}</strong></div></Field>
            </div>
            <Field label="Visual style"><div className="style-grid">{styles.map(([name,desc])=><button type="button" key={name} className={"style-option "+(style===name?"selected":"")} onClick={()=>setStyle(name)}><span className="style-radio">{style===name&&<Check size={11}/>}</span><span><b>{name}</b><small>{desc}</small></span></button>)}</div></Field>
            {style==="Custom"&&<Field label="Describe your custom style"><input value={customStyle} onChange={e=>setCustomStyle(e.target.value)} placeholder="e.g. 1970s film grain, warm analogue colour..."/></Field>}
            <button className="advanced-toggle" onClick={()=>setAdvanced(!advanced)}><Settings2 size={15}/> Advanced production options <ChevronDown size={15} className={advanced?"rotated":""}/></button>
            {advanced&&<div className="advanced-options"><label className="toggle-row"><span><AudioLines size={16}/> Voice-over narration</span><input type="checkbox" checked={voice} onChange={e=>setVoice(e.target.checked)}/></label><label className="toggle-row"><span><Clapperboard size={16}/> Automatic captions</span><input type="checkbox" checked={captions} onChange={e=>setCaptions(e.target.checked)}/></label><label className="toggle-row"><span><Music2 size={16}/> Background music</span><input type="checkbox" checked={music} onChange={e=>setMusic(e.target.checked)}/></label></div>}
            <div className="section-divider"/>
            <div className="panel-heading compact"><div><span className="step">03</span><div><h2>Reference frames</h2><p>Guide the opening and ending of your video.</p></div></div><span className="optional">OPTIONAL</span></div>
            <div className="upload-grid"><UploadTile title="Start frame" subtitle="Opening visual reference" file={startFrame} onFile={setStartFrame}/><UploadTile title="End frame" subtitle="Final visual reference" file={endFrame} onFile={setEndFrame}/></div>
            <div className="generate-row"><div className="cost-note"><LockKeyhole size={14}/><span>No paid AI APIs configured</span></div><button className="generate-button" disabled={!canSubmit} onClick={generate}>{busy?<LoaderCircle className="spin" size={17}/>:<Sparkles size={17}/>} Generate video <ArrowUpRight size={16}/></button></div>
            {notice&&<div className="notice" role="status">{notice}</div>}
          </section>
          <aside className="right-column">
            <section className="preview-card"><div className="preview-top"><span>OUTPUT PREVIEW</span><span className="preview-badge">LIVE SETTINGS</span></div><div className={"preview-screen ratio-"+ratio.replace(":","-")}><div className="preview-glow"/><div className="preview-content"><div className="preview-emblem"><Aperture size={34}/></div><span>YOUR NEXT VIDEO</span><small>Preview will appear here</small></div><div className="preview-corner">GS / 001</div></div><div className="preview-meta"><div><small>FORMAT</small><b>{ratio} · {resolution}</b></div><div><small>DURATION</small><b>{durationLabel}</b></div><div><small>LANGUAGE</small><b>{language}</b></div></div></section>
            <section className="panel workflow-card"><div className="side-title"><h3>Production workflow</h3><span className="muted-pill">PLANNED</span></div><div className="workflow-list"><div className="workflow-item"><span className="workflow-icon"><Sparkles size={15}/></span><div><b>Creative direction</b><small>Prompt and script analysis</small></div><span className="workflow-state">Ready</span></div><div className="workflow-item"><span className="workflow-icon"><Film size={15}/></span><div><b>Scene generation</b><small>Open Wan video models</small></div><span className="workflow-state pending">Pending</span></div><div className="workflow-item"><span className="workflow-icon"><AudioLines size={15}/></span><div><b>Audio & captions</b><small>Narration, music and subtitles</small></div><span className="workflow-state pending">Pending</span></div><div className="workflow-item"><span className="workflow-icon"><MonitorPlay size={15}/></span><div><b>Final assembly</b><small>Render and export MP4</small></div><span className="workflow-state pending">Pending</span></div></div></section>
            <section className="youtube-card"><div className="youtube-icon"><Youtube size={20}/></div><div><b>Connect your YouTube</b><p>Review finished videos and publish to your channel when you're ready.</p><button onClick={()=>setActiveTab("youtube")}>Set up channel <ArrowUpRight size={14}/></button></div></section>
          </aside>
        </div>
        <footer className="footer-note"><ShieldCheck size={14}/> Your creative files stay in your workspace. Generation and account security will be enabled in the next integration phase.</footer>
      </div>:<div className="content secondary-page"><div className="page-heading"><div><div className="eyebrow"><Sparkles size={13}/> WORKSPACE</div><h1>{activeTab==="library"?"Your video library":"YouTube channel"}</h1><p>{activeTab==="library"?"Generated projects and exported videos will appear here.":"Connect your channel securely to publish reviewed videos."}</p></div></div><section className="panel empty-state">{activeTab==="library"?<><Layers3 size={30}/><h2>Your library is ready</h2><p>Your generated videos will be collected here once the WanGP engine is connected.</p><button className="secondary-button" onClick={()=>setActiveTab("create")}>Create your first video</button></>:<><Youtube size={32}/><h2>YouTube connection</h2><p>OAuth setup is not enabled yet. We will configure the Google Cloud project and secure callback before asking you to connect your channel.</p><span className="muted-pill">INTEGRATION NOT CONFIGURED</span></>}</section></div>}
    </main>
  </div>;
}