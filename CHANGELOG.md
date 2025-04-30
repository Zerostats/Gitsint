## 📦 CHANGELOG

### `v0.3.0`

#### ✨ Features

- **🔐 Gitleaks integration**  
  - Added `--gitleaks` CLI flag to run Gitleaks scan on cloned repositories.
  - Automatically downloads the correct Gitleaks binary for your OS and architecture.
  - Scans each local repo after cloning and stores secrets (if found) in results.
  - Outputs structured secret findings inside `out[]` for clean reporting.

- **📦 Gitleaks Setup Utility**  
  - Added a utility (`utils/gitleaks.py`) that:
    - Detects platform and architecture
    - Downloads the latest Gitleaks binary (v8.25.1)
    - Extracts to `./utils/gitleaks/` inside project root
    - Ensures executable permissions

- **🧠 Organization support**  
  - Added `--org` flag to fetch repositories from a specified GitHub organization.

- **📁 Output directory**  
  - Added `--output <path>` to store results and cloned repos in a custom location.

- **🆕 Auto-update**  
  - Added `--check-update` flag to check PyPI for latest `gitsint` version and self-update if needed.

---

### 🐛 Fixes

- Fixed repository clone URL logic to support organization repositories properly.
- Improved error handling when:
  - `repo_obj` is undefined during clone failures
  - Gitleaks returns invalid/empty JSON
- Prevented crash when `--output` was missing by falling back to `./results`.

---

### 🖨️ CLI / Output Improvements

- Updated `print_result()` to:
  - Detect `gitleaks` output
  - Pretty-print secrets with rule, file, and masked token line
- Updated README with:
  - `--gitleaks` documentation and examples
  - New help block reflecting all recent arguments
