## Repository overview

This project is a local access control system that combines YOLO-based vehicle detection + EasyOCR plate reading and a Streamlit dashboard. Key runtime pieces:

- Vision (main.py): captures camera frames, runs YOLO (`yolov8n.pt`) and EasyOCR, shows a CV window and writes access logs to SQLite.
- Dashboard (dashboard.py): Streamlit web UI that reads `sistema_campus.db` directly with sqlite3/pandas.
- DB helpers (banco_dados.py): a small wrapper that creates `sistema_campus.db` and exposes `cadastrar_veiculo`, `buscar_veiculo`, `registrar_acesso` and `fechar`.
- Data population (dml.py): seeds the DB with representative records (plates are uppercase strings of length ~7).
- Orchestrator (start.py): spawns the Streamlit dashboard in background and runs the vision script.

## Quick dev commands (examples)

Install the libraries used by the repo (recommended):

```bash
pip uninstall opencv-python-headless -y
pip install opencv-python easyocr ultralytics streamlit pandas
```

Run only the vision system (camera window):

```bash
python main.py
```

Run only the dashboard (in a separate terminal):

```bash
streamlit run dashboard.py
```

Start both together (launches Streamlit in background then the vision app):

```bash
python start.py
```

## Important conventions & patterns (do not change lightly)

- Plate normalization: plates are stored and compared uppercase without separators. `banco_dados.cadastrar_veiculo` calls `placa.upper()`; callers should pass plain alphanumeric strings (e.g. `RIO2A19`).
- Plate format: code assumes 7-character plates (Mercosul / legacy); OCR post-processing in `main.py` is tuned to return 7-char normalized strings.
- Vehicle types/status: the DB and UI use literal strings: `tipo` ∈ {`CARRO`, `MOTO`}, `status` ∈ {`AUTORIZADO`, `BLOQUEADO`}.
- DB file path: the SQLite file is `sistema_campus.db` in repo root and is created automatically by `BancoDeDados` on first run. `dashboard.py` opens that file directly with `sqlite3`.
- YOLO model: the repo includes `yolov8n.pt` at root. `main.py` loads it with `YOLO('yolov8n.pt')` (ultralytics API). If you replace the model file keep the same filename or update the loader.

## Integration & debugging tips

- Camera: `cv2.VideoCapture(0)` is used. On systems with multiple cameras or virtual cameras change the index (0 → 1, etc.).
- GPU: EasyOCR is created with `easyocr.Reader(['pt'], gpu=False)` in `main.py`. Set `gpu=True` only if you have compatible CUDA/Torch installed. The ultralytics YOLO model will also use available CUDA automatically if Torch with CUDA is present.
- Streamlit concurrency: `start.py` launches Streamlit with `subprocess.Popen(['streamlit','run','dashboard.py'])` and then runs `main.py`. If you need to debug the dashboard independently prefer running `streamlit run dashboard.py` in its own terminal.

## Files to inspect when making changes

- `main.py` — vision loop, OCR heuristic (`processar_ocr_inteligente`), ROI cropping and UI canvas constants (LARGURA_TELA, ALTURA_TELA).
- `banco_dados.py` — single place for DB schema and helper methods.
- `dml.py` — example seed data showing common plate examples and statuses.
- `dashboard.py` — Streamlit UI; note it uses raw SQL via sqlite3 and pandas rather than `BancoDeDados`.
- `start.py` — orchestrator script used for local demos; useful when changing startup behavior or adding logging.

## Safe, discoverable edits examples

- Add a new column to `veiculos`: update `banco_dados.criar_tabelas()` to create the column (use ALTER TABLE for existing DB), then adapt `dashboard.py` queries and any code that reads `buscar_veiculo`.
- Change camera resolution: update `LARGURA_TELA` and `ALTURA_TELA` in `main.py` and adjust ROI math if necessary.
- Swap model file: replace `yolov8n.pt` and verify `model = YOLO('yolov8n.pt')` loads; test detection confidence and classes.

## What is not present / expectations

- There are no automated tests in the repo. Be conservative when changing DB schema or the plate normalization logic.
- The dashboard and vision code access the same DB file concurrently. SQLite works for this simple local workload, but tests should be done if you plan to scale or run from multiple hosts.

If anything here is unclear or you want the instructions tailored (for CI, tests, or Docker), tell me which area to expand and I'll iterate.
