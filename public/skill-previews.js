// Result examples: creator screenshots and explicitly labelled illustrative samples.
(() => {
  'use strict';
  const data = window.SKILL_PREVIEW_DATA || {};
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const localImage = value => /^assets\/previews\/[a-z0-9][a-z0-9-]*\.webp$/.test(value || '');
  const sourceLink = value => /^https:\/\//.test(value || '') ? value : '';
  const arrow = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M7 17 17 7M7 7h10v10"/></svg>';
  function markup(id) {
    const preview = data[id];
    if (!preview || !Array.isArray(preview.images) || !preview.images.length || !preview.images.every(image => localImage(image.src))) return '';
    const image = preview.images[0];
    const credit = preview.credit && sourceLink(preview.credit.url) ? `<p class="example-credit">Example by <a href="${esc(preview.credit.url)}" target="_blank" rel="noopener noreferrer">${esc(preview.credit.name)}</a>${preview.credit.license ? ` · ${esc(preview.credit.license)}` : ''}</p>` : '';
    return `<figure class="skill-example" data-example-id="${esc(id)}" aria-label="Example result for ${esc(preview.title)}">
      <div class="example-bar"><h3>See the result</h3>${preview.images.length > 1 ? `<div class="example-options" role="group" aria-label="Example views">${preview.images.map((item, i) => `<button type="button" data-example-index="${i}" aria-pressed="${i === 0}">${esc(item.label)}</button>`).join('')}</div>` : ''}</div>
      <a class="example-image-link" data-example-link href="./${esc(image.src)}" target="_blank" rel="noopener" aria-label="Open the ${esc(preview.title)} example larger in a new tab"><img data-example-image src="./${esc(image.src)}" alt="${esc(image.alt)}" width="${Number(image.width) || 960}" height="${Number(image.height) || 600}" loading="lazy" decoding="async" fetchpriority="low"><span class="example-unavailable" hidden>Example image unavailable.</span></a>
      <figcaption aria-live="polite"><div><span class="example-kind">${esc(preview.label)}</span><p class="example-caption">${esc(preview.caption)}</p></div><a class="example-open" data-example-link href="./${esc(image.src)}" target="_blank" rel="noopener">Open larger ${arrow}</a></figcaption>
      ${credit}</figure>`;
  }
  function mount(root) {
    root.querySelectorAll('.skill-example').forEach(figure => {
      const preview = data[figure.dataset.exampleId];
      if (!preview) return;
      const image = figure.querySelector('[data-example-image]');
      const links = figure.querySelectorAll('[data-example-link]');
      let usedFallback = false;
      figure.addEventListener('click', event => {
        const button = event.target.closest('[data-example-index]');
        if (!button || !figure.contains(button)) return;
        const selected = preview.images[Number(button.dataset.exampleIndex)];
        if (!selected || !localImage(selected.src)) return;
        usedFallback = false;
        figure.querySelector('.example-kind').textContent = preview.label;
        figure.querySelector('.example-caption').textContent = preview.caption;
        const credit = figure.querySelector('.example-credit');
        if (credit) credit.hidden = false;
        figure.querySelectorAll('[data-example-index]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
        image.hidden = false;
        figure.querySelector('.example-unavailable').hidden = true;
        image.alt = selected.alt;
        image.width = selected.width;
        image.height = selected.height;
        image.src = './' + selected.src;
        links.forEach(link => { link.href = './' + selected.src; });
      });
      image.addEventListener('error', () => {
        if (!usedFallback && localImage(preview.sampleSrc) && !image.getAttribute('src').endsWith(preview.sampleSrc)) {
          usedFallback = true;
          image.src = './' + preview.sampleSrc;
          image.alt = 'Illustrative sample output for ' + preview.title;
          image.width = 960;
          image.height = 600;
          links.forEach(link => { link.href = './' + preview.sampleSrc; });
          figure.querySelector('.example-kind').textContent = 'Sample output';
          figure.querySelector('.example-caption').textContent = 'A labelled illustration of the kind of result this skill helps create.';
          const credit = figure.querySelector('.example-credit');
          if (credit) credit.hidden = true;
          return;
        }
        image.hidden = true;
        figure.querySelector('.example-unavailable').hidden = false;
      });
    });
  }
  window.SkillPreviews = Object.freeze({ markup, mount, ids: Object.freeze(Object.keys(data)) });
})();
