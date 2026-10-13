/* The Horcrux Protocol — story layer for CTFd (injected via Theme Footer).
   Reads window.HX_SCENES (scenes.json) + window.HX_SIG (sigils). On the
   challenges page it draws the Patronus progress strip from real solve state,
   plays the prologue once, and fires cinematic interstitials on actual solves
   (fetch hook on /challenges/attempt) plus the rift/temptation/finale gates. */
(function () {
  if (window.__HX_INIT__) return; window.__HX_INIT__ = true;
  var SC = window.HX_SCENES || {}, SIG = window.HX_SIG || {}, SEAL = window.HX_SEAL || '';
  var ORDER = ['HX-01','HX-02','HX-03','HX-04','HX-05','HX-06'];
  var idToCode = {}, lockedCodes = {};

  function el(id){ return document.getElementById(id); }
  function onChalPage(){ return /\/challenges\/?$/.test(location.pathname); }
  function paras(a){ return (a||[]).map(function(p){ return '<p>'+p+'</p>'; }).join(''); }

  /* "seen once" flags are namespaced per CTFd account, so every NEW account
     starts fresh and gets the prologue + each challenge's arrival scene — even
     on a browser where a previous account already watched them. */
  function uid(){ try { return (window.CTFd && CTFd.user && CTFd.user.id) || (window.init && window.init.userId) || 'anon'; } catch(e){ return 'anon'; } }
  function seenGet(base){ try { return localStorage.getItem(base+'-'+uid()) === '1'; } catch(e){ return false; } }
  function seenSet(base){ try { localStorage.setItem(base+'-'+uid(), '1'); } catch(e){} }

  function ensureVeil(){
    if (el('hx-veil')) return;
    var v = document.createElement('div'); v.id = 'hx-veil';
    v.innerHTML = '<div id="hx-scene"></div>';
    v.addEventListener('click', function(e){ if (e.target === v) closeVeil(); });
    document.body.appendChild(v);
  }
  /* read-timer: the primary "continue" button on a story beat is held for
     READ_SECONDS with a filling countdown ring, so players read the scene
     before advancing. Skipped on the interactive quiz. The ✕ always bails. */
  var READ_SECONDS = 10, skipReadTimer = false, readT = null;
  function armReadTimer(){
    var scene = el('hx-scene'); if (!scene) return;
    var btn = scene.querySelector('.hx-actions .hx-btn.p'); if (!btn) return;
    if (readT){ clearTimeout(readT); readT = null; }
    btn.classList.add('counting');
    var ring = document.createElement('span'); ring.className = 'hx-ring';
    ring.style.setProperty('--hx-read', READ_SECONDS + 's');
    ring.innerHTML = '<svg viewBox="0 0 20 20"><circle class="bg" cx="10" cy="10" r="8"></circle><circle class="fg" cx="10" cy="10" r="8"></circle></svg>';
    btn.insertBefore(ring, btn.firstChild);
    readT = setTimeout(function(){
      btn.classList.remove('counting');
      if (ring.parentNode) ring.parentNode.removeChild(ring);
      readT = null;
    }, READ_SECONDS * 1000);
  }
  function openVeil(){
    ensureVeil(); el('hx-veil').classList.add('open'); el('hx-scene').scrollTop = 0;
    if (skipReadTimer){ skipReadTimer = false; return; }
    armReadTimer();
  }
  function closeVeil(){
    var v = el('hx-veil'); if (v) v.classList.remove('open');
    if (readT){ clearTimeout(readT); readT = null; }
    audioPhase('ambient');   // back to the board -> exploration track
  }

  /* intro */
  var introIdx = 0;
  function openIntro(){ if (!SC.intro) return; introIdx = 0; showIntro(); }
  function showIntro(){
    var b = SC.intro.beats[introIdx], last = introIdx >= SC.intro.beats.length - 1;
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.introDone()">Skip ✕</button>' +
      (b.beat ? '<div class="hx-beat">'+b.beat+'</div>' : '') + paras(b.body) +
      '<div class="hx-actions">' +
      (introIdx > 0 ? '<button class="hx-btn" onclick="HX.intro(-1)">Back</button>' : '<span></span>') +
      (last ? '<button class="hx-btn p" onclick="HX.introDone()">'+(SC.intro.cta||'Begin')+' ▸</button>'
            : '<button class="hx-btn p" onclick="HX.intro(1)">Continue →</button>') +
      '</div>';
    openVeil();
  }
  function introStep(d){ introIdx += d; showIntro(); }
  function introDone(){ seenSet('hx-intro-seen'); closeVeil(); }

  /* stage solve */
  function openSolve(code){
    var st = SC.stages[code]; if (!st || !st.solve) return; var s = st.solve;
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.close()">×</button>' +
      (s.beat ? '<div class="hx-beat">'+s.beat+'</div>' : '') +
      (s.title ? '<h2>'+s.title+'</h2>' : '') + (s.who ? '<div class="hx-who">'+s.who+'</div>' : '') +
      paras(s.body) + (s.flag ? '<div class="hx-flag">HORCRUX{ '+s.flag.replace(/ /g,'_')+' }</div>' : '') +
      '<div class="hx-actions"><button class="hx-btn p" onclick="HX.afterSolve(\''+code+'\')">'+(s.cta||'Continue')+'</button></div>';
    openVeil();
  }
  function afterSolve(code){
    closeVeil(); refreshStrip();
    if (SC.temptation && SC.temptation.after === code) setTimeout(openTemptation, 450);
    else if (SC.finale && SC.finale.after === code) setTimeout(function(){ openFinale('enter'); }, 450);
    else if (SC.stages[code] && SC.stages[code].rift) setTimeout(function(){ openRift(code); }, 450);
  }
  function openRift(code){
    var r = SC.stages[code].rift; if (!r) return;
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.close()">×</button>' +
      (r.beat ? '<div class="hx-beat">'+r.beat+'</div>' : '') + paras(r.body) +
      '<div class="hx-actions"><button class="hx-btn p" onclick="HX.close()">'+(r.cta||'On ▸')+'</button></div>';
    openVeil();
  }

  /* stage arrival: the "unlock" story card (e.g. HX-01's "On arrival"), shown
     the first time a player opens an unlocked challenge. First-open-only,
     remembered per code; closing the veil reveals CTFd's real challenge modal
     underneath. Replay any time with HX.openUnlock('HX-0N'). */
  function unlockSeen(code){ return seenGet('hx-unlock-'+code); }
  function openUnlock(code){
    var st = SC.stages[code]; if (!st || !st.unlock) return; var u = st.unlock;
    seenSet('hx-unlock-'+code);
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.close()">×</button>' +
      (u.beat ? '<div class="hx-beat">'+u.beat+'</div>' : '') +
      (u.title ? '<h2>'+u.title+'</h2>' : '') + (u.who ? '<div class="hx-who">'+u.who+'</div>' : '') +
      paras(u.body) +
      '<div class="hx-actions"><button class="hx-btn p" onclick="HX.close()">'+(u.cta||'Continue')+'</button></div>';
    openVeil();
  }
  function maybeUnlock(code){
    if (!code || lockedCodes[code] || unlockSeen(code)) return;   // only unlocked, first open
    var st = SC.stages[code]; if (st && st.unlock) openUnlock(code);
  }

  /* temptation */
  function openTemptation(){
    var t = SC.temptation; if (!t) return;
    audioPhase('tension');
    el('hx-scene').innerHTML =
      '<div class="hx-beat">'+(t.beat||'')+'</div>' + (t.title ? '<h2>'+t.title+'</h2>' : '') + paras(t.body) +
      '<div class="hx-actions">' +
      '<button class="hx-btn" onclick="HX.temp(\'refuse\')">'+t.refuseLabel+'</button>' +
      '<button class="hx-btn p" onclick="HX.temp(\'accept\')">'+t.acceptLabel+'</button></div>';
    openVeil();
  }
  function tempResolve(choice){
    var t = SC.temptation, s = choice === 'refuse' ? t.refuse : t.badend;
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.close()">×</button>' + paras(s.body) +
      '<div class="hx-actions"><button class="hx-btn p" onclick="'+(choice==='refuse'?'HX.temptGo()':'HX.openTemptation()')+'">'+s.cta+'</button></div>';
    el('hx-scene').scrollTop = 0;
  }
  // After refusing the temptation (and committing to go on), play the rift that
  // sits on the temptation's stage — the glimpse of the war right before HX-04 —
  // then let the player continue. The afterSolve chain can't do this because the
  // temptation already owns that stage's solve transition.
  function temptGo(){
    var after = SC.temptation && SC.temptation.after;
    if (after && SC.stages[after] && SC.stages[after].rift) openRift(after);
    else closeVeil();
  }

  /* finale + capstone quiz */
  var quizOrder = {};
  function openFinale(part){
    audioPhase('finale');
    if (part === 'quiz'){ renderQuiz(); return; }
    var F = SC.finale, s = F[part], acts = '';
    if (part === 'enter') acts = '<button class="hx-btn p" onclick="HX.fin(\'quiz\')">'+s.cta+'</button>';
    else if (part === 'pass') acts = '<button class="hx-btn" onclick="HX.fin(\'fail\')">'+s.altLabel+'</button><button class="hx-btn p" onclick="HX.close()">'+s.cta+'</button>';
    else /* fail */ acts = '<button class="hx-btn" onclick="HX.fin(\'pass\')">'+(s.altLabel||'See the other ending')+'</button><button class="hx-btn p" onclick="HX.fin(\'quiz\')">'+(s.cta||'Try again')+'</button>';
    el('hx-scene').innerHTML =
      '<button class="hx-x" onclick="HX.close()">×</button>' +
      (s.beat ? '<div class="hx-beat">'+s.beat+'</div>' : '') + (s.title ? '<h2>'+s.title+'</h2>' : '') +
      paras(s.body) + '<div class="hx-actions">'+acts+'</div>';
    openVeil();
  }
  function qesc(t){ return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function renderQuiz(){
    var Q = SC.finale && SC.finale.quiz; if (!Q){ openFinale('pass'); return; }
    quizOrder = {};
    var h = '<button class="hx-x" onclick="HX.close()">×</button>' +
      (Q.beat ? '<div class="hx-beat">'+Q.beat+'</div>' : '') +
      (Q.title ? '<h2>'+Q.title+'</h2>' : '') + (Q.intro ? '<p>'+Q.intro+'</p>' : '') +
      '<div id="hx-quiz">';
    Q.questions.forEach(function(q, i){
      h += '<div class="hx-q"><div class="hx-q-t">'+(i+1)+'. '+qesc(q.q)+'</div>';
      if (q.type === 'text'){
        h += '<input class="hx-q-in" type="text" autocomplete="off" spellcheck="false" data-qi="'+i+'" placeholder="type your answer">';
      } else if (q.type === 'choice'){
        q.options.forEach(function(opt, oi){
          h += '<label class="hx-q-opt"><input type="radio" name="hxq'+i+'" value="'+oi+'"><span>'+qesc(opt)+'</span></label>';
        });
      } else if (q.type === 'order'){
        h += '<div class="hx-ord-seq" id="hx-ord-'+i+'"></div><div class="hx-ord-pool">';
        q.items.forEach(function(it){
          h += '<button type="button" class="hx-ord-item" data-qi="'+i+'" data-name="'+qesc(it)+'" onclick="HX.ordPick('+i+',this)">'+qesc(it)+'</button>';
        });
        h += '</div><button type="button" class="hx-ord-reset" onclick="HX.ordReset('+i+')">&#8634; reset order</button>';
      }
      h += '</div>';
    });
    h += '</div><div class="hx-quiz-err" id="hx-quiz-err"></div>' +
      '<div class="hx-actions"><button class="hx-btn p" onclick="HX.quizSubmit()">'+(Q.cta||'Submit')+'</button></div>';
    var sc = el('hx-scene'); sc.innerHTML = h; sc.scrollTop = 0;
    Q.questions.forEach(function(q, i){ if (q.type === 'order') renderOrd(i); });
    skipReadTimer = true; installFocusGuard(); openVeil();
    // CTFd's challenge modal (if still up) traps focus; the guard neutralizes
    // it, so now we can safely place the caret in the first text answer.
    var first = sc.querySelector('.hx-q-in');
    if (first) setTimeout(function(){ try { first.focus(); } catch(e){} }, 40);
  }
  /* A Bootstrap modal keeps a document-level focusin listener that pulls focus
     back inside itself, which stops you typing into the quiz inputs in our
     overlay. This capture-phase guard runs first and halts the event while the
     story veil is open and focus is inside it, so the field keeps the caret. */
  var focusGuarded = false;
  function installFocusGuard(){
    if (focusGuarded) return; focusGuarded = true;
    document.addEventListener('focusin', function(e){
      var v = el('hx-veil');
      if (v && v.classList.contains('open') && v.contains(e.target)) e.stopImmediatePropagation();
    }, true);
  }
  function renderOrd(i){
    var seq = quizOrder[i] || [], box = el('hx-ord-'+i); if (!box) return;
    box.innerHTML = seq.length
      ? seq.map(function(n, ix){ return '<span class="hx-ord-chip">'+(ix+1)+'. '+qesc(n)+'</span>'; }).join('')
      : '<span class="hx-ord-empty">click the names in the order you met them…</span>';
  }
  function ordPick(i, btn){
    if (btn.disabled) return;
    (quizOrder[i] = quizOrder[i] || []).push(btn.getAttribute('data-name'));
    btn.disabled = true; btn.classList.add('used'); renderOrd(i);
  }
  function ordReset(i){
    quizOrder[i] = [];
    var items = document.querySelectorAll('#hx-quiz .hx-ord-item[data-qi="'+i+'"]');
    for (var k = 0; k < items.length; k++){ items[k].disabled = false; items[k].classList.remove('used'); }
    renderOrd(i);
  }
  function qnorm(s){ return (s||'').toLowerCase().replace(/[^a-z0-9]/g,''); }
  function quizSubmit(){
    var Q = SC.finale.quiz, n = Q.questions.length, correct = 0, missing = false;
    Q.questions.forEach(function(q, i){
      if (q.type === 'text'){
        var inp = document.querySelector('#hx-quiz .hx-q-in[data-qi="'+i+'"]'), v = inp ? inp.value : '';
        if (!v.trim()){ missing = true; return; }
        if ((q.accept||[]).map(qnorm).indexOf(qnorm(v)) >= 0) correct++;
      } else if (q.type === 'choice'){
        var sel = document.querySelector('#hx-quiz input[name="hxq'+i+'"]:checked');
        if (!sel){ missing = true; return; }
        if (parseInt(sel.value, 10) === q.answer) correct++;
      } else if (q.type === 'order'){
        var seq = quizOrder[i] || [];
        if (seq.length < q.correct.length){ missing = true; return; }
        if (seq.join('|') === q.correct.join('|')) correct++;
      }
    });
    if (missing){ el('hx-quiz-err').textContent = 'Answer every part before you braid the thread.'; return; }
    var passed = correct >= (Q.passMin || Math.ceil((n + 1) / 2));
    recordFinale(correct, n, passed);   // server-side, for grading; never shown to the player
    openFinale(passed ? 'pass' : 'fail');
  }
  function recordFinale(correct, total, passed){
    try {
      var nonce = (window.init && window.init.csrfNonce) ||
                  (window.CTFd && window.CTFd.config && window.CTFd.config.csrfNonce) || '';
      fetch('/api/v1/horcrux/finale', { method: 'POST', credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'CSRF-Token': nonce },
        body: JSON.stringify({ correct: correct, total: total, passed: passed }) });
    } catch (e) {}
  }

  /* progress strip */
  function sigSVG(code){ return SIG[code] || ''; }
  function buildStrip(list){
    var cur = -1; for (var i=0;i<list.length;i++){ if (!list[i].solved){ cur = i; break; } }
    var allSolved = list.length > 0 && list.every(function(it){ return it.solved; });
    var nodes = '';
    list.forEach(function(it, i){
      var icon = it.solved
        ? '<div class="hx-ic"><div class="hx-pat">'+sigSVG(it.code)+'</div></div>'
        : '<div class="hx-ic"><div class="hx-dot"></div></div>';
      nodes += '<div class="'+((i===cur&&!it.solved)?'hx-node cur':'hx-node')+'">'+icon+'<div class="hx-lab">'+it.code.replace('HX-','')+'</div></div>';
    });
    var html = '<div class="hx-mast">' +
        '<div class="hx-kick">Department of Mysteries · Case File</div>' +
        '<h1 class="hx-h1">The Horcrux Protocol</h1>' +
        '<div class="hx-sub">Shadows Over Hogwarts — six fragments to carry home</div>' +
        '<div class="hx-meta">Investigator: G. Weasley, Unspeakable &nbsp;•&nbsp; Status: Open ' +
        '&nbsp;·&nbsp; <span id="hx-replay" onclick="HX.openIntro()">↻ replay intro</span>' +
        (allSolved ? '&nbsp;·&nbsp; <span id="hx-replay-finale" onclick="HX.fin(\'enter\')">↻ replay finale</span>' : '') + '</div>' +
      '</div>' +
      '<div class="hx-rail"><div class="hx-line"></div><div class="hx-nodes">'+nodes+'</div></div>';
    var strip = el('hx-strip');
    if (!strip){
      strip = document.createElement('div'); strip.id = 'hx-strip';
      var board = document.querySelector('[x-data="ChallengeBoard"]');
      if (board && board.parentNode) board.parentNode.insertBefore(strip, board);
      else { var jt = document.querySelector('.jumbotron'); if (jt) jt.parentNode.insertBefore(strip, jt.nextSibling); else (document.querySelector('main')||document.body).prepend(strip); }
    }
    // the case-file masthead replaces CTFd's generic "Challenges" hero
    var jumbo = document.querySelector('.jumbotron'); if (jumbo) jumbo.style.display = 'none';
    strip.innerHTML = html;
  }
  function loadState(cb){
    fetch('/api/v1/challenges', { credentials:'same-origin', headers:{ 'Accept':'application/json' } })
      .then(function(r){ return r.json(); })
      .then(function(j){
        var data = (j && j.data) || {}; var arr = Array.isArray(data) ? data : (data.data || []);
        // Sort by id so anonymized ("???") stages still map to their code by
        // position — CTFd hides a locked challenge's name but keeps its real id.
        var sorted = arr.slice().sort(function(a, b){ return a.id - b.id; });
        idToCode = {}; lockedCodes = {}; var map = {};
        sorted.forEach(function(c, i){
          var m = /HX-0?(\d)/.exec(c.name || '');
          var code = m ? ('HX-0'+m[1]) : (ORDER[i] || null);
          if (!code) return;
          idToCode[c.id] = code; map[code] = c;
          if (!m || c.name === '???' || c.type === 'hidden') lockedCodes[code] = true;
        });
        cb(ORDER.map(function(code){ var c = map[code]; return { code: code, solved: c ? !!c.solved_by_me : false }; }));
      })
      .catch(function(){ cb(ORDER.map(function(code){ return { code: code, solved: false }; })); });
  }
  /* solve detection: poll the real solved-state and fire the cinematic when a
     fragment flips unsolved -> solved. Robust against CTFd's bundle (an ES
     module that loads after this inline script and captures window.fetch). */
  var knownSolved = null, lastSig = '';
  function applyState(list){
    var sig = list.map(function(it){ return it.solved ? '1' : '0'; }).join('');
    var newly = [];
    if (knownSolved) list.forEach(function(it){ if (it.solved && !knownSolved[it.code]) newly.push(it.code); });
    if (sig !== lastSig){ buildStrip(list); lastSig = sig; }
    enrichCards();
    knownSolved = {}; list.forEach(function(it){ knownSolved[it.code] = it.solved; });
    var veilOpen = el('hx-veil') && el('hx-veil').classList.contains('open');
    if (newly.length && !veilOpen){
      try { var bs = el('challenge-window'); if (bs && window.bootstrap){ var inst = bootstrap.Modal.getInstance(bs); if (inst) inst.hide(); } } catch(e){}
      openSolve(newly[0]);
    }
  }
  function refreshStrip(){ if (!onChalPage()) return; loadState(applyState); }

  /* ---- rich story cards: dress each real CTFd tile like the mockup ----
     Non-destructive: CTFd's bare .challenge-inner is hidden via CSS (on the
     [data-hx] hook) and we append our own .hxc overlay. A MutationObserver
     re-applies it whenever Alpine re-renders the board (e.g. after a solve).
     enrichCards() is idempotent, so the observer it triggers settles at once. */
  function cardCode(btn){
    var c = idToCode[btn.value]; if (c) return c;
    var p = btn.querySelector('.challenge-inner p');
    var m = p && /HX-0?(\d)/.exec(p.textContent || ''); return m ? 'HX-0'+m[1] : null;
  }
  function enrichCards(){
    var btns = document.querySelectorAll('.challenge-button');
    for (var i = 0; i < btns.length; i++){
      var btn = btns[i], code = cardCode(btn), st = code && SC.stages[code];
      if (!st) continue;
      var solved = btn.classList.contains('challenge-solved');
      var locked = !!lockedCodes[code] && !solved;
      var want = solved ? 'done' : (locked ? 'locked' : 'active');
      if (btn.getAttribute('data-hx') === code && btn.getAttribute('data-hx-state') === want && btn.querySelector('.hxc')) continue;
      var old = btn.querySelector('.hxc'); if (old) old.parentNode.removeChild(old);
      var wrap = document.createElement('div');
      if (locked){
        wrap.className = 'hxc locked';
        wrap.innerHTML =
          '<div class="hxc-seal">' + SEAL + '</div>' +
          '<div class="hxc-kick">'+code+' &middot; '+(st.domain||'')+'</div>' +
          '<div class="hxc-name hxc-sealed">— sealed —</div>' +
          '<div class="hxc-ghost">— unknown —</div>' +
          '<div class="hxc-blurb">Recover the fragment before it to break this seal.</div>' +
          '<div class="hxc-foot"><span class="hxc-tag locked">Sealed against you</span></div>';
      } else {
        var tag = solved ? (st.doneTag || 'Sealed · at rest') : 'Awaiting you';
        var sig = solved ? '<div class="hxc-sigil">'+sigSVG(code)+'</div>' : '';
        var phrase = (solved && st.flagphrase) ? '<span class="hxc-phrase">“'+st.flagphrase+'”</span>' : '';
        wrap.className = 'hxc ' + want;
        wrap.innerHTML = sig +
          '<div class="hxc-kick">'+code+' · '+(st.domain||'')+'</div>' +
          '<div class="hxc-name">'+(st.ghost||'')+'</div>' +
          '<div class="hxc-ghost">'+(st.ghostName||'')+'</div>' +
          '<div class="hxc-blurb">'+(st.blurb||'')+'</div>' +
          '<div class="hxc-foot"><span class="hxc-tag">'+tag+'</span>'+phrase+'</div>';
      }
      btn.appendChild(wrap);
      btn.setAttribute('data-hx', code); btn.setAttribute('data-hx-state', want);
    }
    // relabel CTFd's anonymized "???" category header
    var heads = document.querySelectorAll('.category-header h3');
    for (var k = 0; k < heads.length; k++){
      if (heads[k].textContent.trim() === '???') heads[k].textContent = 'Sealed fragments';
    }
  }
  /* ---- hint dialogs: CTFd core-beta unlocks hints with native confirm()/
     alert(), which embedded/automation browsers suppress (then the hint snaps
     shut and never unlocks — the classic "clicking does nothing"). We override
     the two theme hooks with on-theme in-page dialogs. displayUnlock must
     return a Promise<bool>; showHint awaits it before POSTing the unlock. ---- */
  function hxDialog(o){
    return new Promise(function(resolve){
      var d = document.createElement('div'); d.className = 'hx-dlg-veil';
      d.innerHTML = '<div class="hx-dlg" role="dialog" aria-modal="true">' +
        (o.title ? '<div class="hx-dlg-t">'+o.title+'</div>' : '') +
        '<div class="hx-dlg-b">'+(o.body||'')+'</div>' +
        '<div class="hx-dlg-a">' +
        (o.cancelLabel ? '<button class="hx-btn" data-x>'+o.cancelLabel+'</button>' : '') +
        '<button class="hx-btn p" data-ok>'+(o.okLabel||'OK')+'</button></div></div>';
      function done(v){ if (d.parentNode) d.parentNode.removeChild(d); resolve(v); }
      d.addEventListener('click', function(e){ if (e.target === d) done(false); });
      d.querySelector('[data-ok]').onclick = function(){ done(true); };
      var x = d.querySelector('[data-x]'); if (x) x.onclick = function(){ done(false); };
      document.body.appendChild(d);
      try { d.querySelector('[data-ok]').focus(); } catch(e){}
    });
  }
  function installHintHooks(){
    var C = window.CTFd; if (!C || !C._functions || !C._functions.challenge) return false;
    var ch = C._functions.challenge; if (ch.__hxHooked) return true; ch.__hxHooked = true;
    ch.displayUnlock = function(){ return hxDialog({ title:'Unlock this hint?',
      body:'Reading this hint will spend some of your points. Do you want to continue?',
      okLabel:'Unlock hint', cancelLabel:'Not yet' }); };
    ch.displayUnlockError = function(resp){
      var msg = 'This hint could not be unlocked.';
      try { if (resp && resp.errors){ msg = (resp.errors.score || resp.errors[0] || JSON.stringify(resp.errors)); }
            else if (resp && resp.message) msg = resp.message; } catch(e){}
      return hxDialog({ title:'Not unlocked', body:msg, okLabel:'Got it' });
    };
    ch.displayHint = function(h){ return hxDialog({ title:'Hint', body:(h && h.content) || '', okLabel:'Got it' }); };
    return true;
  }

  /* ---- soundtrack (optional) -----------------------------------------------
     Off until you add tracks and enable it. To wire your own music:
       1. drop ambient.mp3 / tension.mp3 / finale.mp3 into  horcrux-ctf/audio/
       2. in scenes.json set  audio.enabled: true  (tweak volume / filenames)
       3. docker compose up -d  (nginx serves them at /audio/*.mp3)
     Three phases swap automatically: ambient (exploring) -> tension (the Fred
     temptation) -> finale (the endgame). Browsers block autoplay, so it arms on
     the first click; a ♪ toggle (bottom-right, remembered per browser) mutes. */
  var AUDIO = { cfg: null, el: null, phase: 'ambient', muted: false, started: false };
  function audioInit(){
    AUDIO.cfg = SC.audio || null;
    try { AUDIO.muted = localStorage.getItem('hx-muted') === '1'; } catch(e){}
    if (!AUDIO.cfg || !AUDIO.cfg.enabled) return;   // nothing until you enable it
    audioAddBtn();
    document.addEventListener('pointerdown', function(){
      if (!AUDIO.started){ AUDIO.started = true; audioPlay(AUDIO.phase); }
    }, { once: true });
  }
  function audioVol(){
    var v = (AUDIO.cfg && AUDIO.cfg.volume != null) ? AUDIO.cfg.volume : 0.5;
    try { var s = localStorage.getItem('hx-vol'); if (s !== null && s !== '') v = parseFloat(s); } catch(e){}
    if (isNaN(v)) v = 0.5; return Math.max(0, Math.min(1, v));
  }
  function audioPlay(p){
    if (!AUDIO.cfg || !AUDIO.cfg.enabled) return;
    var t = AUDIO.cfg.tracks || {}, src = t[p] || t.ambient; if (!src) return;
    if (!AUDIO.el){ AUDIO.el = new Audio(); AUDIO.el.loop = true; AUDIO.el.volume = audioVol(); }
    if (AUDIO.el.getAttribute('data-track') !== p){ AUDIO.el.src = src; AUDIO.el.setAttribute('data-track', p); }
    if (!AUDIO.muted) AUDIO.el.play().catch(function(){});
  }
  function audioSetVolume(v){
    v = Math.max(0, Math.min(1, isNaN(v) ? 0.5 : v));
    if (AUDIO.el) AUDIO.el.volume = v;
    try { localStorage.setItem('hx-vol', String(v)); } catch(e){}
  }
  function audioPhase(p){ AUDIO.phase = p; if (AUDIO.started) audioPlay(p); }
  function audioToggle(){
    AUDIO.muted = !AUDIO.muted;
    try { localStorage.setItem('hx-muted', AUDIO.muted ? '1' : '0'); } catch(e){}
    if (AUDIO.muted){ if (AUDIO.el) AUDIO.el.pause(); }
    else { AUDIO.started = true; audioPlay(AUDIO.phase); }
    audioBtnLabel();
  }
  function audioAddBtn(){
    if (el('hx-audio')) return;
    var wrap = document.createElement('div'); wrap.id = 'hx-audio';
    var b = document.createElement('button'); b.id = 'hx-mute'; b.type = 'button'; b.onclick = audioToggle;
    var sl = document.createElement('input'); sl.id = 'hx-vol-sl'; sl.type = 'range';
    sl.min = 0; sl.max = 1; sl.step = 0.01; sl.value = audioVol();
    sl.setAttribute('aria-label', 'Music volume');
    sl.oninput = function(){ audioSetVolume(parseFloat(sl.value)); };
    wrap.appendChild(b); wrap.appendChild(sl); document.body.appendChild(wrap);
    audioBtnLabel();
  }
  function audioBtnLabel(){ var b = el('hx-mute'); if (b) b.textContent = AUDIO.muted ? '♪ off' : '♪ on'; }

  var cardObs = null, enrichT = null;
  function scheduleEnrich(){ clearTimeout(enrichT); enrichT = setTimeout(enrichCards, 60); }
  function watchBoard(){
    if (cardObs) return;
    var board = document.querySelector('[x-data="ChallengeBoard"]'); if (!board) return;
    cardObs = new MutationObserver(scheduleEnrich);
    cardObs.observe(board, { childList: true, subtree: true });
  }
  /* fire the arrival ("unlock") scene when a fragment card is opened. Capture
     phase so we resolve the code before CTFd swaps the board; the defer lets
     idToCode/lockedCodes settle. CTFd still opens its modal underneath. */
  var openHooked = false;
  function watchOpen(){
    if (openHooked) return; openHooked = true;
    document.addEventListener('click', function(e){
      var t = e.target; if (!t || !t.closest) return;
      var btn = t.closest('.challenge-button'); if (!btn) return;
      var code = cardCode(btn);
      setTimeout(function(){ maybeUnlock(code); }, 60);
    }, true);
  }

  window.HX = { close: closeVeil, intro: introStep, introDone: introDone, openIntro: openIntro,
    openUnlock: openUnlock, afterSolve: afterSolve, temp: tempResolve, openTemptation: openTemptation,
    temptGo: temptGo, fin: openFinale, ordPick: ordPick, ordReset: ordReset, quizSubmit: quizSubmit };

  function boot(){
    if (!onChalPage()) return; ensureVeil();
    var tries = 0, iv = setInterval(function(){
      tries++;
      if (document.querySelector('[x-data="ChallengeBoard"]') || tries > 40){
        clearInterval(iv); refreshStrip(); watchBoard(); audioInit(); watchOpen();
        var ht = 0, hiv = setInterval(function(){ if (installHintHooks() || ++ht > 80) clearInterval(hiv); }, 150);
        setInterval(function(){ if (document.visibilityState === 'visible') refreshStrip(); }, 2500);
        if (!seenGet('hx-intro-seen')) setTimeout(openIntro, 600);
      }
    }, 150);
  }
  if (document.readyState !== 'loading') boot(); else document.addEventListener('DOMContentLoaded', boot);
})();
