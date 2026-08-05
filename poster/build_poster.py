"""
Build a self-contained academic-poster HTML page from the analysis + charts.
Embeds the three chart PNGs as base64 data URIs so the page needs no external files.
Output: poster/electricity_poster.html  (body-content + inline <style>; ready for Artifact)
Run:  py build_poster.py
"""
import base64
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUT = Path(__file__).parent / "electricity_poster.html"


def datauri(rel):
    b = (ROOT / rel).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode()


imgs = {
    "__RATCHET__": datauri("charts/gas_vs_electricity.png"),
    "__INFLATION__": datauri("charts/electricity_money_chart.png"),
    "__RESIDUAL__": datauri("charts/residual_model.png"),
}

TEMPLATE = r"""<style>
  :root{
    --paper:#eef1f4; --sheet:#f7f9fb; --panel:#ffffff;
    --ink:#161b22; --ink-soft:#47515e; --ink-faint:#7a8593;
    --line:#d8dee6; --line-strong:#c3ccd6;
    --electric:#1f77b4; --electric-deep:#12547f;
    --gas:#c85e1b; --gas-deep:#9c470f;
    --tint:rgba(31,119,180,.055);
    --serif:"Charter","Cambria","Georgia","Times New Roman",serif;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    --mono:ui-monospace,"SF Mono","Cascadia Mono","Consolas","Liberation Mono",monospace;
  }
  *{box-sizing:border-box}
  .wrap{background:var(--paper);padding:32px 20px;min-height:100%;
    font-family:var(--sans);color:var(--ink);line-height:1.5;
    -webkit-font-smoothing:antialiased;}
  .sheet{max-width:1360px;margin:0 auto;background:var(--sheet);
    border:1px solid var(--line);border-radius:4px;
    box-shadow:0 1px 0 rgba(22,27,34,.04),0 18px 48px -24px rgba(22,27,34,.22);
    padding:44px 48px 40px;}

  /* ---- header ---- */
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.18em;
    text-transform:uppercase;color:var(--electric-deep);font-weight:600;}
  .masthead{display:flex;justify-content:space-between;align-items:baseline;
    gap:24px;flex-wrap:wrap;border-bottom:2px solid var(--ink);padding-bottom:20px;}
  h1{font-family:var(--serif);font-weight:700;font-size:44px;line-height:1.04;
    letter-spacing:-.01em;margin:10px 0 8px;text-wrap:balance;max-width:20ch;}
  .sub{font-family:var(--serif);font-size:18px;font-style:italic;color:var(--ink-soft);
    max-width:52ch;}
  .byline{font-family:var(--mono);font-size:12px;color:var(--ink-soft);
    text-align:right;line-height:1.9;white-space:nowrap;}
  .byline b{color:var(--ink);font-weight:600;letter-spacing:.02em;}
  .thesis{margin:18px 0 4px;font-family:var(--serif);font-size:19px;line-height:1.45;
    max-width:96ch;color:var(--ink);}
  .thesis .hl{color:var(--electric-deep);font-weight:700;font-style:normal;}

  /* ---- KPI strip ---- */
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;
    background:var(--line);border:1px solid var(--line);margin:22px 0 6px;border-radius:3px;overflow:hidden;}
  .kpi{background:var(--panel);padding:16px 18px;}
  .kpi .n{font-family:var(--serif);font-weight:700;font-size:38px;line-height:1;
    font-variant-numeric:tabular-nums;letter-spacing:-.02em;}
  .kpi .n.up{color:var(--electric-deep);} .kpi .n.down{color:var(--gas-deep);}
  .kpi .l{font-size:12.5px;color:var(--ink-soft);margin-top:7px;line-height:1.35;max-width:24ch;}
  .kpi .u{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--ink-faint);margin-top:2px;}

  /* ---- body columns ---- */
  .cols{display:grid;grid-template-columns:.82fr 1.12fr 1.06fr;gap:26px;margin-top:26px;align-items:start;}
  .col{display:flex;flex-direction:column;gap:22px;}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:18px 18px 16px;}
  .panel.plain{background:transparent;border:0;padding:0;}
  .panel h2{font-family:var(--serif);font-size:20px;font-weight:700;margin:6px 0 8px;letter-spacing:-.01em;}
  .panel p{font-size:13.5px;margin:0 0 9px;color:var(--ink);}
  .panel p:last-child{margin-bottom:0;}
  .lead{font-size:15px !important;color:var(--ink) !important;}

  /* data table */
  table{width:100%;border-collapse:collapse;font-size:12px;margin:4px 0 10px;}
  th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top;}
  th{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--ink-faint);font-weight:600;border-bottom:1px solid var(--line-strong);}
  td code{font-family:var(--mono);font-size:11px;color:var(--electric-deep);}
  .chip{display:inline-block;font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;
    background:var(--tint);color:var(--electric-deep);border:1px solid var(--line);
    padding:4px 9px;border-radius:999px;margin-top:2px;}

  /* steps */
  ol.steps{margin:2px 0 0;padding:0;list-style:none;counter-reset:s;display:flex;flex-direction:column;gap:8px;}
  ol.steps li{position:relative;padding-left:30px;font-size:13px;counter-increment:s;}
  ol.steps li::before{content:counter(s);position:absolute;left:0;top:-1px;
    width:20px;height:20px;border-radius:50%;background:var(--electric);color:#fff;
    font-family:var(--mono);font-size:11px;font-weight:600;display:grid;place-items:center;}

  /* figures */
  figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:4px;overflow:hidden;}
  figure .fh{display:flex;justify-content:space-between;align-items:center;gap:10px;
    padding:11px 14px 9px;border-bottom:1px solid var(--line);}
  figure .fh .t{font-family:var(--serif);font-weight:700;font-size:15px;}
  figure .tag{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;
    color:var(--ink-faint);}
  figure img{display:block;width:100%;height:auto;background:#fff;padding:8px 10px;}
  figcaption{font-size:12px;color:var(--ink-soft);padding:9px 14px 13px;line-height:1.45;}
  figcaption b{color:var(--ink);}

  /* findings */
  .find{display:flex;flex-direction:column;gap:12px;}
  .find .item{display:grid;grid-template-columns:26px 1fr;gap:10px;align-items:start;}
  .find .r{font-family:var(--serif);font-weight:700;font-size:22px;color:var(--electric);line-height:1;
    font-variant-numeric:tabular-nums;}
  .find .b{font-size:13px;} .find .b b{color:var(--ink);}
  .limit{border-left:3px solid var(--gas);background:#fff;padding:12px 14px;border-radius:0 4px 4px 0;}
  .limit p{font-size:12.5px;color:var(--ink-soft);margin:0 0 7px;}
  .limit p:last-child{margin:0;}
  .limit .lab{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;
    color:var(--gas-deep);font-weight:600;display:block;margin-bottom:6px;}

  /* footer */
  .foot{margin-top:28px;border-top:2px solid var(--ink);padding-top:20px;
    display:grid;grid-template-columns:1.3fr 1fr;gap:30px;align-items:start;}
  .concl{display:flex;flex-direction:column;gap:9px;}
  .concl .h{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--electric-deep);font-weight:600;}
  .concl p{font-size:13px;margin:0;}
  .concl p b{color:var(--ink);}
  .pull{font-family:var(--serif);font-weight:700;font-size:23px;line-height:1.25;letter-spacing:-.01em;
    color:var(--ink);text-wrap:balance;}
  .pull .a{color:var(--gas-deep);}
  .src{font-family:var(--mono);font-size:11px;color:var(--ink-soft);line-height:1.8;margin-top:14px;}
  .src a{color:var(--electric-deep);text-decoration:none;border-bottom:1px solid var(--line-strong);}

  @media (max-width:900px){
    .kpis{grid-template-columns:repeat(2,1fr);}
    .cols{grid-template-columns:1fr;}
    .foot{grid-template-columns:1fr;}
    h1{font-size:34px;} .byline{text-align:left;white-space:normal;}
  }
  @media print{
    .wrap{background:#fff;padding:0;} .sheet{box-shadow:none;border:0;max-width:none;padding:14mm;}
    @page{size:landscape;margin:8mm;}
  }
</style>

<div class="wrap">
<div class="sheet">

  <header>
    <div class="masthead">
      <div>
        <div class="eyebrow">Energy economics &middot; data investigation</div>
        <h1>Why Your Electric Bill Stopped Following Fuel Prices</h1>
        <div class="sub">US electricity prices, natural gas, and the datacenter demand era &mdash; 1978&ndash;2026</div>
      </div>
      <div class="byline">
        <b>Ian&nbsp;Lee</b><br>
        Independent data analysis<br>
        June&nbsp;2026<br>
        Python &middot; pandas &middot; statsmodels
      </div>
    </div>
    <p class="thesis">For decades, US retail electricity tracked the price of natural gas. Around 2020 that link broke &mdash;
      <span class="hl">fuel got cheap again, but bills kept climbing</span> &mdash; and the timing lines up with the first
      sustained growth in US power demand in two decades: the AI datacenter buildout.</p>
  </header>

  <section class="kpis" aria-label="Headline numbers">
    <div class="kpi"><div class="n up">+48%</div><div class="l">Retail electricity, since Jan 2020</div><div class="u">BLS</div></div>
    <div class="kpi"><div class="n down">&minus;65%</div><div class="l">Natural gas, from its 2022 peak</div><div class="u">Henry Hub</div></div>
    <div class="kpi"><div class="n up">+19%</div><div class="l">Electricity <i>since</i> that gas peak &mdash; it rose while gas fell</div><div class="u">2022&rarr;2026</div></div>
    <div class="kpi"><div class="n up">2.6<span style="font-size:20px"> pts/yr</span></div><div class="l">Inflation unexplained by fuel or CPI, since 2023</div><div class="u">Residual</div></div>
  </section>

  <div class="cols">

    <!-- COLUMN 1 -->
    <div class="col">
      <div class="panel plain">
        <div class="eyebrow">Motivation</div>
        <h2>The question</h2>
        <p class="lead">From 2014 to 2020, average US electricity prices were essentially flat. Since 2020 they have risen 48%.</p>
        <p>A jump like that usually has a simple cause: the fuel that runs power plants got more expensive, or general
          inflation lifted everything. So &mdash; is this just fuel and inflation, or is something genuinely new driving it?</p>
      </div>

      <div class="panel">
        <div class="eyebrow">Data &amp; method</div>
        <h2>47 years, three public series</h2>
        <table>
          <thead><tr><th>Series</th><th>Source</th><th>Span</th></tr></thead>
          <tbody>
            <tr><td>Retail electricity, $/kWh</td><td><code>APU000072610</code> &middot; BLS</td><td>1978&ndash;26</td></tr>
            <tr><td>Consumer Price Index</td><td><code>CPIAUCSL</code> &middot; BLS</td><td>monthly</td></tr>
            <tr><td>Henry Hub gas, $/MMBtu</td><td><code>MHHNGSP</code> &middot; EIA</td><td>1997&ndash;26</td></tr>
          </tbody>
        </table>
        <ol class="steps">
          <li>Benchmark electricity against overall inflation (CPI).</li>
          <li>Lag-correlate electricity vs. gas in year-over-year terms.</li>
          <li>Fit a two-factor model (gas&nbsp;+&nbsp;CPI); read what it <i>can't</i> explain.</li>
        </ol>
        <div style="margin-top:12px"><span class="chip">Reproducible &middot; live FRED endpoints &middot; no API keys</span></div>
      </div>
    </div>

    <!-- COLUMN 2 -->
    <div class="col">
      <figure>
        <div class="fh"><span class="t">The ratchet</span><span class="tag">Result 01</span></div>
        <img src="__RATCHET__" alt="Electricity and natural gas indexed to Jan 2020 = 100. Gas spikes fourfold then falls back below its start; electricity rises steadily and stays up.">
        <figcaption>Both series indexed to Jan&nbsp;2020&nbsp;=&nbsp;100. Gas spiked ~4&times; in 2022 and
          <b>round-tripped to &minus;65%</b>; retail electricity followed it <b>up &mdash; and never came back down.</b></figcaption>
      </figure>

      <figure>
        <div class="fh"><span class="t">Not just inflation</span><span class="tag">Result 02</span></div>
        <img src="__INFLATION__" alt="Rolling 6-year percent change of electricity versus CPI since the 1980s, with the 2010s shale decade shaded; electricity now rises above the CPI line.">
        <figcaption>Rolling 6-year % change vs. CPI. The shaded band is the 2010s <b>shale decade</b>, when cheap gas kept
          prices flat &mdash; the old normal. Today electricity is <b>outrunning inflation</b>, a run steeper than 96% of all
          6-year periods since 1984.</figcaption>
      </figure>
    </div>

    <!-- COLUMN 3 -->
    <div class="col">
      <figure>
        <div class="fh"><span class="t">The unexplained gap</span><span class="tag">Result 03</span></div>
        <img src="__RESIDUAL__" alt="Time series of electricity inflation not explained by gas or CPI; near zero historically, lifting to about 2.6 points per year after 2023.">
        <figcaption>A two-factor OLS model (6-month-lagged gas&nbsp;+&nbsp;CPI), trained only on pre-2023 data, predicts what
          electricity inflation <i>should</i> be. The residual sits near zero for most of history &mdash; then <b>lifts to
          ~2.6&nbsp;pts/yr after 2023</b> and stays there.</figcaption>
      </figure>

      <div class="panel plain">
        <div class="eyebrow">Findings</div>
        <div class="find">
          <div class="item"><div class="r">1</div><div class="b"><b>Electricity ratchets.</b> It follows gas up with a
            ~6-month lag (r&nbsp;=&nbsp;0.53) but did not retrace when gas gave back its entire 2022 spike.</div></div>
          <div class="item"><div class="r">2</div><div class="b"><b>A persistent ~2.6 pts/yr</b> of electricity inflation
            since 2023 is unexplained by fuel or CPI &mdash; coinciding with the datacenter-driven return of demand growth.</div></div>
          <div class="item"><div class="r">3</div><div class="b"><b>Elevated, not unprecedented.</b> Prior residual episodes
            (2005&ndash;09) decayed within a couple of years; this one hasn't &mdash; and its driver is still growing.</div></div>
        </div>
      </div>

      <div class="limit">
        <span class="lab">Stated limitations</span>
        <p>The residual is &ldquo;not gas, not CPI&rdquo; &mdash; it bundles datacenter demand with grid capex, plant
          retirements, and electrification. It is not a clean causal estimate.</p>
        <p>Overlapping YoY series are heavily autocorrelated (Durbin&ndash;Watson&nbsp;&approx;&nbsp;0.2): a descriptive
          decomposition, not formal inference.</p>
      </div>
    </div>
  </div>

  <footer class="foot">
    <div class="concl">
      <span class="h">Conclusions</span>
      <p><b>The link between fuel and your bill is broken.</b> In the shale decade, cheap gas meant flat prices; that
        cool-off is absent today.</p>
      <p><b>Whatever replaced fuel as the driver is growing, not fading.</b> The honest claim isn't &ldquo;unprecedented&rdquo;
        &mdash; it's elevated, persistent, and attached to demand that keeps rising.</p>
    </div>
    <div>
      <div class="pull">Not everyone uses AI.<br>But <span class="a">everyone pays an electric bill.</span></div>
      <div class="src">
        Data: BLS &amp; EIA via FRED. Reproducible end-to-end.<br>
        <a href="https://github.com/pachinkodealer/electricity-price-analysis">github.com/pachinkodealer/electricity-price-analysis</a><br>
        &copy; Ian&nbsp;Lee 2026
      </div>
    </div>
  </footer>

</div>
</div>
"""

html = TEMPLATE
for k, v in imgs.items():
    html = html.replace(k, v)
OUT.write_text(html, encoding="utf-8")
print("Wrote", OUT, f"({OUT.stat().st_size/1024:.0f} KB)")
