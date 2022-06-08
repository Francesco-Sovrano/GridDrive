virtualenv .env -p python3
source .env/bin/activate

echo "Installing other environments' dependencies.."
pip install -r environments/requirements.txt
