'use strict';

window.App = (function () {
  const apiBase = '';  // 使用相对路径，因为前后端现在在同一个服务器上

  async function fetchStyles() {
    const res = await fetch(`${apiBase}/styles`);
    if (!res.ok) throw new Error('获取风格失败');
    return res.json();
  }

  async function generate(payload) {
    const endpoint = (window.useAI ? '/generate/ai' : '/generate/preview');
    const res = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('生成失败');
    return res.json();
  }

  function fillStyleOptions(selectEl, styles) {
    selectEl.innerHTML = '';
    styles.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.name}`;
      selectEl.appendChild(opt);
    });
  }

  function bindStyleInfo(selectEl, styles) {
    const info = document.getElementById('style-info');
    const img = document.getElementById('style-image');
    const name = document.getElementById('style-name');
    const desc = document.getElementById('style-desc');

    function render() {
      const id = selectEl.value;
      const s = styles.find(x => x.id === id);
      if (!s) { info.hidden = true; return; }
      name.textContent = s.name || '';
      desc.textContent = s.description || '';
      if (s.example_image) {
        img.src = s.example_image;
        img.alt = s.name || '示例图';
      } else {
        img.removeAttribute('src');
        img.alt = '示例图';
      }
      info.hidden = false;
    }

    selectEl.addEventListener('change', render);
    render();
  }

  function setPreview(html) {
    const iframe = document.getElementById('preview');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(html);
    doc.close();
  }

  function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.style.display = 'flex';
    }
  }

  function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.style.display = 'none';
    }
  }

  function getPreviewHTML() {
    const iframe = document.getElementById('preview');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    return doc.documentElement.outerHTML;
  }

  async function downloadImage() {
    const iframe = document.getElementById('preview');
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    // 默认取整页截图；若未来添加特定画布id，可优先选择该元素
    const target = doc.body || doc.documentElement;
    const canvas = await html2canvas(target, { backgroundColor: null, scale: 2 });
    const url = canvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = url;
    a.download = 'xhs_cover.png';
    a.click();
  }

  function exportCode() {
    const html = getPreviewHTML();
    const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'xhs_cover.html';
    a.click();
    URL.revokeObjectURL(url);
  }

  async function copyCode() {
    const html = getPreviewHTML();
    await navigator.clipboard.writeText(html);
    alert('已复制HTML到剪贴板');
  }

  async function init() {
    const form = document.getElementById('generate-form');
    const select = document.getElementById('style');
    const useAIBox = document.getElementById('useAI');

    try {
      const styles = await fetchStyles();
      fillStyleOptions(select, styles);
      bindStyleInfo(select, styles);
    } catch (e) {
      console.error(e);
      alert('初始化失败：无法加载风格列表');
    }

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      window.useAI = !!useAIBox.checked;
      const payload = {
        title: document.getElementById('title').value.trim(),
        author: document.getElementById('author').value.trim(),
        style_id: document.getElementById('style').value
      };
      if (!payload.title) {
        alert('请填写标题');
        return;
      }
      
      // 显示loading
      showLoading();
      
      try {
        const { html } = await generate(payload);
        setPreview(html);
      } catch (err) {
        console.error(err);
        alert('生成失败');
      } finally {
        // 无论成功还是失败都隐藏loading
        hideLoading();
      }
    });

    // 绑定导出按钮
    document.getElementById('btn-shot').addEventListener('click', () => {
      downloadImage().catch(err => { console.error(err); alert('下载图片失败'); });
    });
    document.getElementById('btn-export').addEventListener('click', exportCode);
    document.getElementById('btn-copy').addEventListener('click', () => {
      copyCode().catch(() => alert('复制失败')); 
    });
  }

  return { init };
})();


