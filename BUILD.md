# Build & Test

## Checkout

```bash
git clone https://github.com/smysnk/SikuliGO.git
cd SikuliGO/sikuli-framework
```

## Prerequisites

- Python `3.10+`
- Go `1.24+`

## Required Libraries

### Python packages

Install from `sikuli-framework`:

```bash
python -m pip install --upgrade pip
python -m pip install pytest
python -m pip install sikuligo
python -m pip install "robotframework>=7.0.0"
```

### Native/system libraries

- macOS: built-in `screencapture` (already present by default).
- Linux: screenshot tooling such as ImageMagick `import` or `scrot` is required for capture-based logging paths.
- Optional OCR support: install `tesseract` and `leptonica` libraries on your OS.
- Optional OpenCV support: install OpenCV dev libraries on your OS.

## Build `sikuligo` Binary

From repository root (`SikuliGO`):

```bash
go build -o ./sikuligo ./cmd/sikuligrpc
```

## Run unit tests

From `sikuli-framework`:

```bash
export SIKULI_FRAMEWORK_BACKEND=sikuligo
python -m pytest -q -m "not integration"
```

## Run integration tests

From `sikuli-framework`:

```bash
SIKULIGO_INTEGRATION=1 \
SIKULIGO_BINARY_PATH=../sikuligo \
python -m pytest -q -m integration
```

## Optional: manual server mode

From repository root:

```bash
./sikuligo -listen 127.0.0.1:50051 -admin-listen :8080
```

Then run tests/examples in another shell:

```bash
export SIKULI_GRPC_ADDR=127.0.0.1:50051
```
