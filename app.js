async function executeCalxInput(code) {
  if (!code || !code.trim()) return;

  commandHistory.push(code);
  historyIndex = commandHistory.length;

  const row = document.createElement("div");
  row.className = "space-y-1.5";

  const promptHeader = document.createElement("div");
  promptHeader.className = "flex items-start gap-2";
  promptHeader.innerHTML = `
    <span class="text-dandelion-400 font-bold select-none text-xs sm:text-sm">calx&gt;</span>
    <span class="text-slate-200 font-mono whitespace-pre-wrap break-all">${escapeHtml(code)}</span>
  `;
  row.appendChild(promptHeader);

  try {
    // Send input directly to python server.py -> calx_lexer.py
    const response = await fetch("/tokenize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code })
    });

    const result = await response.json();

    if (result.success) {
      latestTokensList = result.tokens;
      totalTokensScanned += result.tokens.length;
      if (tokenCountDisplay) {
        tokenCountDisplay.textContent = `Tokens: ${totalTokensScanned}`;
      }

      const tableContainer = document.createElement("div");
      tableContainer.innerHTML = renderTokenTable(result.tokens);
      row.appendChild(tableContainer);
    } else {
      latestTokensList = [];
      const errBox = document.createElement("div");
      errBox.className = "mt-2 p-3 rounded-lg bg-rose-950/70 border border-rose-800 text-rose-300 text-xs font-mono space-y-1 shadow-md";
      errBox.innerHTML = `
        <div class="flex items-center gap-2 font-bold text-rose-400">
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <span>${escapeHtml(result.error_type || "LexicalError")}:</span>
        </div>
        <p class="pl-6 text-rose-200">${escapeHtml(result.error)}</p>
      `;
      row.appendChild(errBox);
    }
  } catch (err) {
    const errBox = document.createElement("div");
    errBox.className = "mt-2 p-3 rounded-lg bg-rose-950/70 border border-rose-800 text-rose-300 text-xs font-mono";
    errBox.innerHTML = `<span class="font-bold">Server Error:</span> Failed to connect to Python backend (<code>server.py</code>).`;
    row.appendChild(errBox);
  }

  if (terminalHistory) terminalHistory.appendChild(row);
  if (terminalScreen) terminalScreen.scrollTop = terminalScreen.scrollHeight;
}
