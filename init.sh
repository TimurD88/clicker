conda create -n "clicker" python=3.12
conda activate clicker
pip install -r requirements.txt
python -m playwright install --with-deps chromium