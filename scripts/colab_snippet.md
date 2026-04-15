Colab setup snippet for Ultimate Tic-Tac-Toe

1) Install from GitHub (recommended if you push the repo):

```python
!pip install git+https://github.com/<your-user>/ultimate_tictactoe.git
```

2) Or build a wheel locally and upload to Drive, then install in Colab:

Local (on your machine):
```bash
python -m pip install --upgrade build
python -m build
# copy dist/*.whl to Google Drive
```

Colab:
```python
from google.colab import drive
drive.mount('/content/drive')
!pip install /content/drive/MyDrive/path/to/ultimate_tictactoe-0.1.0-py3-none-any.whl
```

3) Mount Drive and use it for persistence of `ai/heuristic_weights.json` and `ai/tt.pkl`:

```python
from google.colab import drive
drive.mount('/content/drive')
import shutil, os
dst = '/content/ultimate_tictactoe/ai'
os.makedirs(dst, exist_ok=True)
shutil.copy('/content/drive/MyDrive/ai/heuristic_weights.json', dst)
shutil.copy('/content/drive/MyDrive/ai/tt.pkl', dst)
# then import and run
import sys
sys.path.insert(0, '/content/ultimate_tictactoe')
from main import main
```

4) Quick run (example):
```python
!python -m ultimate_tictactoe.main --mode ai_vs_ai --depth1 4 --depth2 3
```
