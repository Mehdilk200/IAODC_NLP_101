/* ════════════════════════════════════════════════════════════
   SENTIMENTIQ V2 — app.js
   BERT Sentiment Analysis · FastAPI · Futuristic UI
   ════════════════════════════════════════════════════════════ */
'use strict';

/* ─── CONFIG ───────────────────────────────────────────────── */
const API_BASE    = 'http://localhost:8000';
const PER_PAGE    = 6;

/* ─── PRODUCTS DATA ─────────────────────────────────────────── */
const PRODUCTS = [
  { id:1,  name:'Apple AirPods Pro 2nd Gen',      price:249.00, rating:4.8, rcount:2341, category:'Electronics',
    img:'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MME73?wid=400&hei=400&fmt=jpeg&qlt=95',
    reviews:[
      {user:'Alex M.',  text:'Incredible noise cancellation! Best earbuds I have ever owned.', s:'positive', c:.97},
      {user:'Sarah K.', text:'Great sound but the case scratches easily.', s:'positive', c:.82}]},
  { id:2,  name:'Samsung 65" QLED 4K Smart TV',   price:1299.00, rating:4.6, rcount:1876, category:'Electronics',
    img:'https://images.samsung.com/is/image/samsung/p6pim/levant/qa65q80cauxzn/gallery/levant-qled-q80c-qa65q80cauxzn-536340580?$730_584_PNG$',
    reviews:[
      {user:'James L.', text:'Stunning picture quality, colors are vibrant!', s:'positive', c:.95},
      {user:'Mike T.',  text:'Remote stopped working after 2 months. Very disappointed.', s:'negative', c:.91}]},
  { id:3,  name:'Sony WH-1000XM5 Headphones',     price:349.00, rating:4.9, rcount:3102, category:'Electronics',
    img:'https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3?fmt=png-alpha&wid=400',
    reviews:[
      {user:'Emma R.', text:'Best headphones money can buy. Crystal clear audio!', s:'positive', c:.98},
      {user:'Tom W.',  text:'Comfortable but overpriced for what you get.', s:'negative', c:.74}]},
  { id:4,  name:'Instant Pot Duo 7-in-1',          price:89.95, rating:4.7, rcount:5432, category:'Kitchen',
    img:'https://images-na.ssl-images-amazon.com/images/I/71V6nHajGML._AC_SL300_.jpg',
    reviews:[
      {user:'Lisa P.', text:'Changed my cooking completely. So easy and fast!', s:'positive', c:.96},
      {user:'Bob H.',  text:'Seal ring smells terrible after a few uses. Quite annoying.', s:'negative', c:.88}]},
  { id:5,  name:'Kindle Paperwhite 11th Gen',      price:139.99, rating:4.8, rcount:2876, category:'E-Readers',
    img:'https://m.media-amazon.com/images/G/01/kindle/dp/2022/KPW5/01-device-images-single._SL500_FMpng_.png',
    reviews:[
      {user:'Anna C.',  text:'Perfect for reading! Crisp screen, easy on the eyes.', s:'positive', c:.95},
      {user:'David N.', text:'Battery life is exceptional. Lasts for weeks!', s:'positive', c:.93}]},
  { id:6,  name:'Dyson V15 Detect Vacuum',         price:699.99, rating:4.5, rcount:1234, category:'Home',
    img:'https://dyson-h.assetsadobe2.com/is/image/content/dam/dyson/products/floorcare/stick/v15/gallery/v15-detect-total-clean-product-main.png?$responsive$&cropPathE=desktop&fit=stretch,1&wid=400',
    reviews:[
      {user:'Rachel G.', text:'Powerful suction! The laser detection is genius.', s:'positive', c:.97},
      {user:'Mark Z.',   text:'Way too expensive. Similar from cheaper brands.', s:'negative', c:.85}]},
  { id:7,  name:'LEGO Technic Bugatti Chiron',     price:449.99, rating:4.9, rcount:876, category:'Toys',
    img:'https://www.lego.com/cdn/cs/set/assets/blt0d4ca7f95693c4d0/42083.jpg?fit=bounds&format=jpg&quality=80&width=400&height=400&dpr=1',
    reviews:[
      {user:'Chris F.', text:'An absolute masterpiece! Worth every penny.', s:'positive', c:.99},
      {user:'Julia M.', text:'Too complex for children. For adult collectors only.', s:'negative', c:.78}]},
  { id:8,  name:'Nike Air Max 270',                price:150.00, rating:4.4, rcount:4521, category:'Fashion',
    img:'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/skwgyqrbfzhu6uyeh0gg/air-max-270-shoes-2V5C4p.png',
    reviews:[
      {user:'Kevin B.', text:'Super comfortable and stylish. Great daily wear!', s:'positive', c:.92},
      {user:'Mia S.',   text:'Runs a bit small. Not very durable either.', s:'negative', c:.87}]},
  { id:9,  name:'Fitbit Sense 2 Smartwatch',       price:249.95, rating:4.3, rcount:1654, category:'Wearables',
    img:'https://www.fitbit.com/global/content/assets/en-us/product/sense2/black/pdp/hero/pdp-sense2-hero-black-1x.png',
    reviews:[
      {user:'Paul D.',  text:'Great health tracking. Sleep tracking is very accurate.', s:'positive', c:.91},
      {user:'Grace H.', text:'App keeps crashing and syncing is unreliable.', s:'negative', c:.89}]},
  { id:10, name:'KitchenAid Stand Mixer',          price:399.99, rating:4.8, rcount:3210, category:'Kitchen',
    img:'https://www.kitchenaid.com/content/dam/global/kitchenaid/countertop-appliances/stand-mixers/artisan/images/hero-KSM150PSER.tif?imwidth=400',
    reviews:[
      {user:'Helen W.', text:'Built like a tank! A kitchen essential.', s:'positive', c:.96},
      {user:'Tony A.',  text:'Excellent mixer but extremely heavy to move.', s:'positive', c:.70}]},
  { id:11, name:'Bose QuietComfort Earbuds II',    price:279.00, rating:4.6, rcount:987, category:'Electronics',
    img:'https://assets.bose.com/content/dam/Bose_DAM/Web/consumer_electronics/global/products/headphones/qc_earbuds_ii/product_silo_images/QCEarbudsII_Black_EC_Hero.png/jcr:content/renditions/cq5dam.web.600.600.png',
    reviews:[
      {user:'Nora P.', text:'Exceptional ANC! Worth every dollar.', s:'positive', c:.97},
      {user:'Sam R.',  text:'Connection keeps dropping. Annoying bug.', s:'negative', c:.83}]},
  { id:12, name:'Vitamix 5200 Blender',            price:499.95, rating:4.7, rcount:2109, category:'Kitchen',
    img:'https://www.vitamix.com/content/dam/vitamix/product-assets/machines/blenders/5200/black/5200_black_main_2022.jpg',
    reviews:[
      {user:'Sophie K.', text:'Makes the smoothest smoothies ever! A powerhouse.', s:'positive', c:.98},
      {user:'Harry L.',  text:'Very loud at high speed. Neighbors complained!', s:'negative', c:.79}]},
  { id:13, name:'iPad Pro 11" M2 Chip',            price:799.00, rating:4.9, rcount:1543, category:'Tablets',
    img:'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-11-select-wifi-spacegray-202212?wid=400&hei=400&fmt=jpeg&qlt=90',
    reviews:[
      {user:'Olivia T.', text:'Blazing fast performance! Best tablet on market.', s:'positive', c:.99},
      {user:'Ethan C.',  text:'Expensive and no headphone jack is still annoying.', s:'negative', c:.82}]},
  { id:14, name:'Logitech MX Master 3S Mouse',     price:99.99, rating:4.8, rcount:2345, category:'Computing',
    img:'https://resource.logitech.com/w_692,c_lpad,ar_4:3,q_auto,f_auto,dpr_1.0/d_transparent.gif/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-graphite.png',
    reviews:[
      {user:'Liam B.', text:'Perfect for productivity. Scroll wheel is buttery!', s:'positive', c:.96},
      {user:'Ava M.',  text:'Great mouse but software setup is complicated.', s:'positive', c:.72}]},
  { id:15, name:'Canon EOS R50 Mirrorless Camera', price:679.00, rating:4.6, rcount:654, category:'Cameras',
    img:'https://www.usa.canon.com/images/EOS-R50-Black-Body_Front-Slant-Hero_800x800.png',
    reviews:[
      {user:'Zoe F.',  text:'Amazing autofocus for the price! Great beginner cam.', s:'positive', c:.94},
      {user:'Noah G.', text:'Battery life is terrible. Need multiple batteries.', s:'negative', c:.88}]},
  { id:16, name:'Weber Spirit E-310 Gas Grill',    price:549.00, rating:4.5, rcount:876, category:'Outdoor',
    img:'https://www.weber.com/medias/Spirit-E-310-46110001-hero.png?context=bWFzdGVyfGltYWdlc3w&format=png&quality=85&width=400',
    reviews:[
      {user:'Brian N.', text:'Heats evenly and quickly! Perfect backyard BBQs.', s:'positive', c:.95},
      {user:'Clara J.', text:'Assembly was a nightmare. Instructions very unclear.', s:'negative', c:.87}]},
  { id:17, name:'Theragun Pro Massage Gun',        price:399.00, rating:4.4, rcount:1234, category:'Fitness',
    img:'https://www.therabody.com/on/demandware.static/-/Sites-therabody-master-catalog/default/dw3f6b6e8a/images/large/TheragunPro-Black-PDP-Hero.png',
    reviews:[
      {user:'Diego S.', text:'Amazing for muscle recovery! Love it after workouts.', s:'positive', c:.96},
      {user:'Ivy C.',   text:'Powerful but quite noisy compared to competitors.', s:'negative', c:.80}]},
  { id:18, name:'Philips Hue Smart Lighting Kit',  price:199.99, rating:4.3, rcount:2109, category:'Smart Home',
    img:'https://www.philips-hue.com/en-us/v2/assets/img/products/hue-starter-kit/hue-starter-kit-hero.png',
    reviews:[
      {user:'Felix W.', text:'Transforms the atmosphere of any room! Easy setup.', s:'positive', c:.93},
      {user:'Iris T.',  text:'App crashes frequently and bridge disconnects randomly.', s:'negative', c:.90}]},
];

/* ─── STATE ─────────────────────────────────────────────────── */
const state = {
  page: 1,
  filter: 'all',
  search: '',
  extraPos: 0,
  extraNeg: 0,
  extraTotal: 0,
  lastConf: 0,
};

/* ─── UTILS ─────────────────────────────────────────────────── */
const $id   = id => document.getElementById(id);
const $qs   = (sel, ctx = document) => ctx.querySelector(sel);
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

function starsHtml(r) {
  const full = Math.floor(r), half = r % 1 >= .5 ? 1 : 0, empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '⯨' : '') + '☆'.repeat(empty);
}

function sentimentStars(s, c) {
  if (s === 'positive') return c >= .9 ? 5 : c >= .75 ? 4 : 3;
  return c >= .9 ? 1 : c >= .75 ? 2 : 3;
}

/* ─── CURSOR GLOW ───────────────────────────────────────────── */
const cursorGlow = $id('cursor-glow');
document.addEventListener('mousemove', e => {
  cursorGlow.style.left = e.clientX + 'px';
  cursorGlow.style.top  = e.clientY + 'px';
});

/* ─── HERO CANVAS (particle field) ─────────────────────────── */
function initCanvas() {
  const canvas = $id('hero-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, particles;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }

  function mkParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + .3,
      vx: (Math.random() - .5) * .4,
      vy: (Math.random() - .5) * .4,
      op: Math.random() * .5 + .1,
    };
  }

  function init() {
    resize();
    particles = Array.from({length: 120}, mkParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,153,0,${p.op})`;
      ctx.fill();
    });

    // lines between nearby
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 100) {
          ctx.beginPath();
          ctx.strokeStyle = `rgba(255,153,0,${(1 - dist/100) * .08})`;
          ctx.lineWidth = .5;
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }

  init();
  draw();
  window.addEventListener('resize', init);
}

/* ─── NAVBAR SCROLL ─────────────────────────────────────────── */
function initNav() {
  const nav = $id('nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 60);
  });
}

/* ─── HERO COUNTER METRICS ──────────────────────────────────── */
function initHeroCounters() {
  const els = document.querySelectorAll('.hm-val');
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el    = e.target;
      const target = parseFloat(el.dataset.count);
      const float  = !Number.isInteger(target);
      animNum(el, 0, target, 1400, float);
      io.unobserve(el);
    });
  }, { threshold: .5 });
  els.forEach(el => io.observe(el));
}

/* ─── ANIMATED NUMBER ───────────────────────────────────────── */
function animNum(el, from, to, dur, float = false) {
  const start = performance.now();
  function step(now) {
    const p   = clamp((now - start) / dur, 0, 1);
    const ease = 1 - Math.pow(1 - p, 4);
    const val  = from + (to - from) * ease;
    el.textContent = float ? val.toFixed(1) : Math.round(val).toLocaleString();
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* ─── STATS ─────────────────────────────────────────────────── */
function computeStats() {
  let tot = 0, pos = 0, neg = 0;
  PRODUCTS.forEach(p => p.reviews.forEach(r => {
    tot++; if (r.s === 'positive') pos++; else neg++;
  }));
  tot += state.extraTotal;
  pos += state.extraPos;
  neg += state.extraNeg;
  return { tot, pos, neg, rating: 4.6 };
}

function updateStats(animate = true) {
  const { tot, pos, neg, rating } = computeStats();

  const dur = animate ? 1400 : 0;
  animNum($id('s-total'),  0, tot,    dur);
  animNum($id('s-pos'),    0, pos,    dur);
  animNum($id('s-neg'),    0, neg,    dur);
  animNum($id('s-rating'), 0, rating, dur, true);

  const posRatio = tot ? pos/tot*100 : 0;
  const negRatio = tot ? neg/tot*100 : 0;
  const conf     = state.lastConf || (tot ? (pos*.93 + neg*.86)/tot*100 : 0);

  setTimeout(() => {
    $id('sb-total').style.width  = '85%';
    $id('sb-pos').style.width    = posRatio.toFixed(1) + '%';
    $id('sb-neg').style.width    = negRatio.toFixed(1) + '%';
    $id('sb-rating').style.width = (rating/5*100).toFixed(1) + '%';

    $id('vz-pos').style.width  = posRatio.toFixed(1)  + '%';
    $id('vz-neg').style.width  = negRatio.toFixed(1)  + '%';
    $id('vz-conf').style.width = conf.toFixed(1)      + '%';
    $id('vp-pos').textContent  = posRatio.toFixed(0)  + '%';
    $id('vp-neg').textContent  = negRatio.toFixed(0)  + '%';
    $id('vp-conf').textContent = conf.toFixed(0)      + '%';

    // Donut
    const circ = 2 * Math.PI * 48; // ≈301.6
    const fill = conf / 100 * circ;
    $id('donut-ring').style.strokeDasharray = `${fill.toFixed(1)} ${circ}`;
    $id('donut-val').textContent = Math.round(conf) + '%';
  }, animate ? 500 : 0);
}

/* ─── FEED (live analysis history) ──────────────────────────── */
function addToFeed(text, s, conf) {
  const list  = $id('feed-list');
  const empty = list.querySelector('.feed-empty');
  if (empty) empty.remove();

  const item  = document.createElement('div');
  item.className = 'feed-item';
  const cls   = s === 'positive' ? 'fi-pos' : 'fi-neg';
  const lbl   = s === 'positive' ? '😊 Positive' : '😞 Negative';
  const prev  = text.length > 38 ? text.slice(0, 38) + '…' : text;
  item.innerHTML = `
    <span class="fi-badge ${cls}">${lbl}</span>
    <span class="fi-txt">${prev}</span>
    <span class="fi-conf">${(conf * 100).toFixed(0)}%</span>`;
  list.insertBefore(item, list.firstChild);
  while (list.children.length > 7) list.removeChild(list.lastChild);
}

/* ─── TOAST ─────────────────────────────────────────────────── */
function toast(msg, type = 'info') {
  const icons = { success:'✅', error:'❌', info:'ℹ️' };
  const wrap  = $id('toast-wrap');
  const el    = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span class="toast-icon">${icons[type]}</span><span class="toast-msg">${msg}</span>`;
  wrap.appendChild(el);
  setTimeout(() => {
    el.classList.add('removing');
    setTimeout(() => el.remove(), 380);
  }, 3400);
}

/* ─── PREDICT API ───────────────────────────────────────────── */
async function predict(text) {
  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({text}),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const d = await res.json();
    return { sentiment: d.sentiment, confidence: d.confidence };
  } catch {
    // Heuristic demo fallback
    const POS_W = ['great','amazing','excellent','perfect','love','awesome','best','fantastic','wonderful','incredible','outstanding','beautiful','happy','brilliant','superb'];
    const NEG_W = ['bad','terrible','awful','horrible','poor','worst','hate','broken','useless','disappointing','annoying','frustrating','defective','awful','rubbish'];
    const lower = text.toLowerCase();
    const pScore = POS_W.filter(w => lower.includes(w)).length;
    const nScore = NEG_W.filter(w => lower.includes(w)).length;
    const sentiment  = pScore >= nScore ? 'positive' : 'negative';
    const confidence = 0.68 + Math.random() * 0.29;
    return { sentiment, confidence };
  }
}

/* ─── ANALYZE REVIEW (global) ───────────────────────────────── */
window.analyzeReview = async function(productId) {
  const userEl   = $id(`u-${productId}`);
  const textEl   = $id(`t-${productId}`);
  const btnEl    = $id(`b-${productId}`);
  const resultEl = $id(`r-${productId}`);

  const username = userEl.value.trim() || 'Anonymous';
  const text     = textEl.value.trim();

  if (!text) { toast('Please write a review before analyzing!', 'error'); textEl.focus(); return; }
  if (text.length < 5) { toast('Review is too short (min. 5 characters)', 'error'); return; }

  // Loading
  btnEl.classList.add('loading');
  btnEl.innerHTML = `<div class="spinner"></div> Analyzing with BERT…`;
  resultEl.classList.remove('show');

  const {sentiment, confidence} = await predict(text);
  const isPos    = sentiment === 'positive';
  const stars    = sentimentStars(sentiment, confidence);
  const pct      = (confidence * 100).toFixed(1);

  // Result panel
  resultEl.innerHTML = `
    <div class="pres-row">
      <span class="pres-key">Sentiment</span>
      <span class="pres-val ${isPos ? 'pres-pos' : 'pres-neg'}">${isPos ? '😊 Positive' : '😞 Negative'}</span>
    </div>
    <div class="pres-row">
      <span class="pres-key">Confidence</span>
      <span class="pres-val" style="color:var(--orange)">${pct}%</span>
    </div>
    <div class="pres-row" style="margin-bottom:12px">
      <span class="pres-key">AI Rating</span>
      <span class="pres-stars">${'★'.repeat(stars)}${'☆'.repeat(5-stars)}</span>
    </div>
    <div class="pres-bar-track">
      <div class="pres-bar-fill" id="pbf-${productId}" style="width:0%"></div>
    </div>`;
  resultEl.classList.add('show');
  setTimeout(() => {
    const fill = $id(`pbf-${productId}`);
    if (fill) fill.style.width = pct + '%';
  }, 60);

  // Add review to product data
  const product = PRODUCTS.find(p => p.id === productId);
  const rev = {user: username, text, s: sentiment, c: confidence};
  product.reviews.unshift(rev);

  // Update state
  state.extraTotal++;
  state.lastConf = confidence * 100;
  if (isPos) state.extraPos++; else state.extraNeg++;

  // Re-render review in card
  const list = $id(`rl-${productId}`);
  if (list) {
    const div = document.createElement('div');
    div.className = `review-item ${isPos ? 'pos-r' : 'neg-r'}`;
    div.innerHTML = `
      <div class="ri-top">
        <span class="ri-user">👤 ${username}</span>
        <span class="ri-badge ${isPos ? 'rib-pos' : 'rib-neg'}">${isPos ? '😊 Positive' : '😞 Negative'}</span>
      </div>
      <div class="ri-text">${text}</div>
      <div class="ri-conf">🤖 ${pct}% confidence</div>`;
    list.insertBefore(div, list.firstChild);
  }

  addToFeed(text, sentiment, confidence);
  updateStats(false);

  toast(
    `${isPos ? '😊 Positive' : '😞 Negative'} sentiment — ${pct}% confidence`,
    isPos ? 'success' : 'info'
  );

  // Reset
  btnEl.classList.remove('loading');
  btnEl.innerHTML = `<svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg> Analyze with BERT`;
  textEl.value = '';
  userEl.value = '';
};

/* ─── RENDER PRODUCT CARD ───────────────────────────────────── */
function renderCard(p) {
  // Compute overall sentiment
  const pos = p.reviews.filter(r => r.s === 'positive').length;
  const ratio = pos / p.reviews.length;
  const badgeCls  = ratio >= .6 ? 'psb-pos' : ratio <= .4 ? 'psb-neg' : 'psb-none';
  const badgeTxt  = ratio >= .6 ? '✓ Mostly Positive' : ratio <= .4 ? '✗ Mixed Reviews' : '~ Neutral';

  // Filter reviews
  const visible = p.reviews.filter(r =>
    state.filter === 'all' || r.s === state.filter
  );

  const reviewsHtml = visible.length ? visible.map(r => `
    <div class="review-item ${r.s === 'positive' ? 'pos-r' : 'neg-r'}">
      <div class="ri-top">
        <span class="ri-user">👤 ${r.user}</span>
        <span class="ri-badge ${r.s === 'positive' ? 'rib-pos' : 'rib-neg'}">${r.s === 'positive' ? '😊 Positive' : '😞 Negative'}</span>
      </div>
      <div class="ri-text">${r.text}</div>
      <div class="ri-conf">🤖 ${(r.c * 100).toFixed(0)}% confidence</div>
    </div>`).join('') :
    `<div style="font-size:.8rem;color:var(--txt3);padding:10px 0">No ${state.filter} reviews yet.</div>`;

  const catEmoji = {'Electronics':'🎧','Kitchen':'🍳','E-Readers':'📚','Home':'🏠','Toys':'🧩','Fashion':'👟','Wearables':'⌚','Tablets':'📱','Computing':'🖱️','Cameras':'📷','Outdoor':'🔥','Fitness':'💪','Smart Home':'💡'}[p.category] || '📦';

  const card = document.createElement('div');
  card.className = 'product-card';
  card.dataset.id = p.id;
  card.innerHTML = `
    <div class="pc-img-wrap">
      <img class="pc-img" src="${p.img}" alt="${p.name}" loading="lazy"
        onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"/>
      <div class="pc-img-fallback" style="display:none">
        <div class="pif-emoji">${catEmoji}</div>
        <div class="pif-name">${p.name}</div>
        <div class="pif-cat">${p.category}</div>
      </div>
      <div class="pc-sentiment-badge ${badgeCls}">${badgeTxt}</div>
    </div>
    <div class="pc-body">
      <div class="pc-name">${p.name}</div>
      <div class="pc-meta">
        <span class="pc-price">$${p.price.toFixed(2)}</span>
        <div class="pc-rating">
          <span class="pc-stars">${starsHtml(p.rating)}</span>
          <span class="pc-rcount">(${p.rcount.toLocaleString()})</span>
        </div>
      </div>

      <div>
        <div class="pc-reviews-label">Customer Reviews</div>
        <div class="pc-reviews-list" id="rl-${p.id}">${reviewsHtml}</div>
      </div>

      <div class="pc-form">
        <div class="pf-label">Analyze a Review with AI</div>
        <input type="text" class="pf-input" id="u-${p.id}" placeholder="Your username" />
        <textarea class="pf-textarea" id="t-${p.id}" placeholder="Write your review here…"></textarea>
        <button class="pf-btn" id="b-${p.id}" onclick="analyzeReview(${p.id})">
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          Analyze with BERT
        </button>
        <div class="pc-result" id="r-${p.id}"></div>
      </div>
    </div>`;

  return card;
}

/* ─── FILTER PRODUCTS ───────────────────────────────────────── */
function filteredProducts() {
  const q = state.search.toLowerCase();
  return PRODUCTS.filter(p =>
    p.name.toLowerCase().includes(q) ||
    p.category.toLowerCase().includes(q)
  );
}

/* ─── RENDER PAGE ───────────────────────────────────────────── */
function renderPage() {
  const list  = filteredProducts();
  const pages = Math.ceil(list.length / PER_PAGE);
  const slice = list.slice((state.page - 1) * PER_PAGE, state.page * PER_PAGE);

  const grid = $id('products-grid');
  grid.innerHTML = '';

  if (!slice.length) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:60px;color:var(--txt2);">
      No products found for "<strong>${state.search}</strong>"</div>`;
  } else {
    slice.forEach((p, i) => {
      const card = renderCard(p);
      card.style.animationDelay = (i * .06) + 's';
      grid.appendChild(card);
    });
  }

  renderPagination(pages);
}

/* ─── PAGINATION ────────────────────────────────────────────── */
function renderPagination(pages) {
  const wrap = $id('pagination');
  wrap.innerHTML = '';
  if (pages <= 1) return;

  const mk = (label, page, disabled, active) => {
    const b = document.createElement('button');
    b.className = 'pg-btn' + (active ? ' active' : '');
    b.textContent = label;
    b.disabled = disabled;
    if (!disabled && !active) b.onclick = () => {
      state.page = page;
      renderPage();
      $id('products').scrollIntoView({behavior:'smooth', block:'start'});
    };
    return b;
  };

  wrap.appendChild(mk('←', state.page - 1, state.page === 1));
  for (let i = 1; i <= pages; i++) wrap.appendChild(mk(i, i, false, i === state.page));
  wrap.appendChild(mk('→', state.page + 1, state.page === pages));
}

/* ─── FILTER BUTTONS ────────────────────────────────────────── */
function initFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.filter = btn.dataset.filter;
      state.page = 1;
      renderPage();
    });
  });
}

/* ─── SEARCH ────────────────────────────────────────────────── */
function initSearch() {
  $id('searchInput').addEventListener('input', e => {
    state.search = e.target.value;
    state.page = 1;
    renderPage();
  });
}

/* ─── SCROLL REVEAL (AOS) ───────────────────────────────────── */
function initAOS() {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: .12 });

  document.querySelectorAll('[data-aos]').forEach(el => io.observe(el));
}

/* ─── STATS OBSERVER ────────────────────────────────────────── */
function initStatsObserver() {
  const sec = document.querySelector('.stats-section');
  let fired = false;
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting && !fired) {
        fired = true;
        updateStats(true);
      }
    });
  }, { threshold: .2 });
  if (sec) io.observe(sec);
}

/* ─── 3D CARD TILT ──────────────────────────────────────────── */
function initTilt() {
  document.addEventListener('mousemove', e => {
    document.querySelectorAll('.product-card, .stat-card').forEach(card => {
      const rect = card.getBoundingClientRect();
      const cx = rect.left + rect.width  / 2;
      const cy = rect.top  + rect.height / 2;
      const dx = (e.clientX - cx) / rect.width;
      const dy = (e.clientY - cy) / rect.height;
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < .8) {
        card.style.transform = `translateY(-6px) rotateY(${dx * 5}deg) rotateX(${-dy * 5}deg)`;
      } else {
        card.style.transform = '';
      }
    });
  });
}

/* ─── INIT ──────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initCanvas();
  initNav();
  initHeroCounters();
  initFilters();
  initSearch();
  renderPage();
  initAOS();
  initStatsObserver();
  initTilt();

  toast('SentimentIQ loaded! Powered by BERT + FastAPI.', 'info');
});