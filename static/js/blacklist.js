// static/js/blacklist_popover.js
(function () {
  const getHeader = () => document.querySelector('#profile-header, .profile-header');
  const getPop = () => document.getElementById('bl-popover');

  // === 右鍵開啟（只在 header 上生效） ===
  document.addEventListener('contextmenu', function (ev) {
    const header = ev.target.closest('#profile-header, .profile-header');
    const pop = getPop();
    if (!header || !pop) return;

    // 阻止瀏覽器原生右鍵選單（只在 header 內）
    ev.preventDefault();
    ev.stopPropagation();

    // 顯示並定位在滑鼠右下角，避免超出視窗
    pop.hidden = false;
    requestAnimationFrame(() => {
      const pw = pop.offsetWidth || 180;
      const ph = pop.offsetHeight || 48;
      let x = ev.clientX + 10;
      let y = ev.clientY + 10;
      x = Math.min(x, window.innerWidth - pw - 10);
      y = Math.min(y, window.innerHeight - ph - 10);
      pop.style.left = x + 'px';
      pop.style.top  = y + 'px';
    });
  });

  // 點擊或右鍵在「外部」都關閉（外部右鍵仍保留原生選單）
  document.addEventListener('click', closeIfOpen);
  document.addEventListener('contextmenu', function (ev) {
    const pop = getPop();
    if (!pop || pop.hidden) return;
    if (ev.target.closest('#profile-header, .profile-header, #bl-popover')) return;
    // 不阻止預設 -> 保留外部右鍵選單，同時關閉浮窗
    pop.hidden = true;
  });

  // 在浮窗內操作不要冒泡（避免被外部監聽關掉）
  document.addEventListener('click', function (ev) {
    if (ev.target.closest('#bl-popover')) ev.stopPropagation();
  });

  // ESC / 捲動 / 縮放：關閉
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeIfOpen(); });
  window.addEventListener('scroll',  () => closeIfOpen(), { passive: true });
  window.addEventListener('resize',  () => closeIfOpen());

  function closeIfOpen(){
    const pop = getPop();
    if (pop && !pop.hidden) pop.hidden = true;
  }
})();
