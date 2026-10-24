/* Blank templates only: no patient inputs, persistent storage, or network requests. */
'use strict';
const copyButton = document.querySelector('[data-copy]');
const copyText = document.getElementById('copy-text');
const status = document.getElementById('copy-status');
copyButton?.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(copyText.textContent);
    status.textContent = 'Blank template copied. Paste it into the EHR or an approved clinical system.';
  } catch {
    copyText.hidden = false;
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(copyText);
    selection.removeAllRanges();
    selection.addRange(range);
    copyText.scrollIntoView({block:'center'});
    status.textContent = 'Automatic copy is unavailable. The blank template below is selected; use Copy, or download the Markdown file.';
  }
});
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
