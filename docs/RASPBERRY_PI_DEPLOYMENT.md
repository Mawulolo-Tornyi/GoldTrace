# Raspberry Pi 5 Deployment

Target: Raspberry Pi 5 (8 GB), 64-bit Raspberry Pi OS.

Install the runtime environment:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For PyTorch training/export work, use a development computer. For production edge inference, install compatible `onnxruntime` when ONNX models are available; otherwise the packaged runtime falls back to scikit-learn feature models. TorchScript exports are also included as validated edge artifacts.

For SIM7600, connect the modem by USB, identify the correct serial port (`ls /dev/ttyUSB*`), install `pyserial`, and update `sim7600.serial_port` in `config/settings.yaml`. Keep `production_mode: false` until recipients and the full alert path have been authorized and tested.

Run API:

```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Run demo:

```bash
python main.py --mode demo --scenario high_risk_mining
```

Do not expose the development FastAPI server directly to the public internet. Use a reverse proxy/TLS/authentication for a real deployment.
