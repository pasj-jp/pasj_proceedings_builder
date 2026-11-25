try {
  const link = document.querySelector('#back-search');
  const saved = sessionStorage.getItem('pasj-search');
  if (saved) {
    const url = new URL(saved, location.origin);
    if (url.origin === location.origin && url.pathname === new URL(link.href).pathname) {
      link.href = url.href;
      link.textContent = '検索結果へ戻る';
    }
  }
} catch { /* Search remains available when storage is disabled. */ }
