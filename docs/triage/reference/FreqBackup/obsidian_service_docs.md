✅ Goal Breakdown
You're trying to:

Link your personal Freqtrade docs to your Obsidian Vault.

Clone + sync upstream official docs (e.g. n8n, OpenWebUI, Ollama, Optuna, etc.) as live mirrors inside your Vault.

🧭 Ideal Directory Layout for Obsidian Vault
vbnet
```
MyObsidianVault/
├── FreqtradeDocs/                     ← personal strategies, notes
│   └── (linked from ./freqtrade-user_data/docs)
├── OpenWebUI_Docs/                    ← cloned official repo
├── n8n_Docs/
├── Optuna_Docs/
├── Ollama_Docs/
├── Templates/                         ← optional templates
├── DailyNotes/
└── .obsidian/                         ← Synced via Remotely Save
```

🛠️ Step-by-Step Implementation
1. ✅ Link your personal Freqtrade docs into Obsidian
This lets you write/edit your strategy documentation natively in Obsidian:

powershell
```
# From inside your Obsidian Vault folder
# Replace <PATH_TO_YOUR_FREQTRADE_PROJECT> with the actual path to your freqtrade project directory
New-Item -ItemType SymbolicLink `
  -Path "FreqtradeDocs" `
  -Target "<PATH_TO_YOUR_FREQTRADE_PROJECT>/freqtrade-user_data/docs"
```
2. ✅ Clone official doc repos directly into your vault
Inside your vault folder (MyObsidianVault/):

bash
```
# Clone official docs (read-only)
git clone https://github.com/open-webui/open-webui.git OpenWebUI_Docs
git clone https://github.com/n8n-io/n8n.git n8n_Docs
git clone https://github.com/ollama/ollama.git Ollama_Docs
git clone https://github.com/optuna/optuna-dashboard.git Optuna_Docs
``` 
You can optionally add --depth 1 to clone faster with just the latest snapshot.

3. 🔁 Keep them updated (manual or scripted)
Use the n8n workflow defined in `n8n_doc_mirror_update.md` to automate `git pull` within each cloned directory.

```bash
# Example manual pull (automated via n8n is better)
# From inside your Obsidian Vault folder
cd OpenWebUI_Docs && git pull
cd ../n8n_Docs && git pull
...
```

4. 🧠 Optional: Use n8n to auto-sync + update index notes
(Combine this with the `git pull` workflow from Step 3)

Set up an n8n cron job (`n8n_doc_mirror_update.md`):

*   Pull all official repos weekly/daily.
*   (Optional) After pulls, use n8n nodes (e.g., Read File, Function, Write File) to create or update a master index note (`_Index.md`) with links or summaries of changes.

5. ☁️ Vault Sync via Remotely Save
Ensure you've set up the **Remotely Save** plugin as described in `MasterSetup.md` Section 5.2. This will:

*   Sync your entire vault (personal notes, settings, and the locally updated mirrored docs) to your chosen cloud storage (e.g., OneDrive, S3).
*   Handle sync across multiple devices if configured.

✅ Final Tips
Name each folder in your vault with a Docs suffix to avoid namespace clashes.

Add an _Index.md to each docs repo if it doesn't exist for faster navigation inside Obsidian.

If your vault gets big, use a tagging convention like #n8n, #openwebui, #freqtrade, etc.
