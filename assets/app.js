/* GenCost calculator. Mirrors the pricing maths in src/build.py */
(function () {
  var el = document.getElementById('gc-data'); if (!el) return;
  var D = JSON.parse(el.textContent), S = D.S, L = S.fmt;
  var $ = function (id) { return document.getElementById(id); };
  var comma = (L === 'es' || L === 'de' || L === 'pt');
  function num(x, dec) {
    var s = (x + 5e-9).toFixed(dec), p = s.split('.'), i = p[0].replace(/\B(?=(\d{3})+(?!\d))/g, comma ? '.' : ',');
    return p.length > 1 ? i + (comma ? ',' : '.') + p[1] : i;
  }
  function usd(x, dec) {
    if (dec === undefined) dec = x >= 100 ? 0 : x >= 1 ? 2 : x >= 0.1 ? 3 : x >= 0.01 ? 4 : 5;
    var s = num(x, dec);
    if (dec > 2) { var d = comma ? ',' : '.', p = s.split(d), b = p[1].replace(/0+$/, ''); while (b.length < 2) b += '0'; s = p[0] + d + b; }
    if (L === 'es' || L === 'de') return s + '\u00a0$';
    if (L === 'pt') return 'US$\u00a0' + s;
    return '$' + s;
  }
  function nint(x) { return num(Math.round(x), 0); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function creditsOut(o, sec) { return o.u === 'cr_s' ? o.v * sec : o.u === 'cr_clip' ? o.v * sec / o.per : o.v; }
  function paygOut(o, sec) { var x = o.u === 'usd_s' ? o.v * sec : o.u === 'usd_clip' ? o.v * sec / o.per : o.v; return Math.max(x, o.min || 0); }
  function price(pl, bill) { if (bill === 'annual') return pl.a != null ? [pl.a, ''] : [pl.m, 'monthly_only']; return pl.m != null ? [pl.m, ''] : [pl.a, 'annual_only']; }
  function compute(job, sec, qty, keep, bill) {
    var J = D.jobs[job], vid = J.t === 'video'; if (!vid) sec = 1;
    var gen = Math.ceil(qty * 100 / keep - 1e-9), rows = [];
    D.offers.forEach(function (o) {
      if (o.j !== job) return;
      var r = { o: o, notes: [] };
      if (o.u.indexOf('cr_') === 0) {
        var cpo = creditsOut(o, sec), need = cpo * gen;
        var ps = o.plans.slice().sort(function (a, b) { return a.cr - b.cr; }), pick = null;
        for (var i = 0; i < ps.length; i++) if (ps[i].cr >= need - 1e-9) { pick = ps[i]; break; }
        var pl = pick || ps[ps.length - 1], pr = price(pl, bill);
        r.per = cpo * pr[0] / pl.cr; r.how = o.how + ' · ' + pl.n;
        if (pr[1]) r.notes.push(S[pr[1]]);
        if (pick) { r.month = pr[0]; r.sub = S.you_pay_plan + ' · ' + S.leftover.replace('{v}', nint(pl.cr - need)).replace('{c}', o.c); }
        else { r.month = null; r.sub = S.exceeds; }
      } else {
        r.per = paygOut(o, sec); r.how = o.how; r.month = r.per * gen;
        if (o.min && o.v * sec < o.min) r.notes.push(S.minimum);
      }
      if (o.u.slice(-5) === '_clip' && sec !== o.per) r.notes.push(S.scaled);
      if (o.ap) r.notes.push(S.approx);
      if (o.nt) r.notes.push(o.nt);
      if (o.pr) r.notes.push(o.pr);
      rows.push(r);
    });
    rows.sort(function (a, b) { if (a.month === null) return b.month === null ? a.per - b.per : 1; if (b.month === null) return -1; return a.month - b.month || a.per - b.per; });
    return { rows: rows, gen: gen };
  }
  window.GC_compute = function (job, sec, qty, keep, bill) {
    return compute(job, sec, qty, keep, bill).rows.map(function (r) { return [r.o.p, r.o.u, r.per, r.month]; });
  };
  function run() {
    var job = $('c-job').value, J = D.jobs[job], vid = J.t === 'video';
    $('f-secs').hidden = !vid; $('l-clips').hidden = !vid; $('l-imgs').hidden = vid;
    var sec = vid ? Math.max(1, Math.min(60, +$('c-secs').value || J.sec)) : 1;
    var qty = Math.max(1, Math.min(100000, Math.round(+$('c-qty').value || 1)));
    var keep = Math.max(5, Math.min(100, +$('c-keep').value || 100));
    var bill = document.querySelector('input[name=bill]:checked').value;
    var res = compute(job, sec, qty, keep, bill), rows = res.rows, gen = res.gen, unit = vid ? S.per_s : S.per_img;
    var h = '';
    rows.forEach(function (r, i) {
      var top = i === 0 && r.month !== null;
      h += '<tr' + (top ? ' class="top"' : '') + '><td><a href="' + r.o.page + '"><b>' + esc(r.o.n) + '</b></a></td><td>' + esc(r.how) +
        (r.notes.length ? '<small>' + esc(r.notes.join(' · ')) + '</small>' : '') + '</td><td class="n num">' + usd(r.per / sec) + esc(unit) +
        '</td><td class="n num">' + usd(r.per) + '</td><td class="n num"><b>' + (r.month === null ? '–' : usd(r.month, 2)) + '</b>' +
        (r.sub ? '<small>' + esc(r.sub) + '</small>' : '') + '</td><td><a class="lnk small" href="' + esc(r.o.src) + '" rel="nofollow noopener" target="_blank">' + esc(S.source) + '</a></td></tr>';
    });
    $('o-rows').innerHTML = h;
    $('o-gen').textContent = nint(gen);
    var b = rows[0]; $('o-best').textContent = b && b.month !== null ? b.o.n + ' · ' + usd(b.month, 2) : '–';
    $('c-model').href = D.model_url + job + '/';
  }
  $('c-job').addEventListener('change', function () { var J = D.jobs[this.value]; if (J.t === 'video') $('c-secs').value = J.sec; run(); });
  ['c-secs', 'c-qty', 'c-keep'].forEach(function (id) { $(id).addEventListener('input', run); });
  Array.prototype.forEach.call(document.querySelectorAll('input[name=bill]'), function (x) { x.addEventListener('change', run); });
  run(); window.GC_ready = true;
})();
