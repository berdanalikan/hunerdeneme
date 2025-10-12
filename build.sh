#!/usr/bin/env bash
# Render build script

echo "🚀 Starting build process..."

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install -r requirements-render.txt

# Try to install OCR dependencies (optional)
echo "🔍 Attempting to install OCR dependencies..."
pip install paddlepaddle>=3.0.0 || echo "⚠️ PaddlePaddle installation failed, OCR will be disabled"

# Install other optional dependencies
pip install opencv-contrib-python>=4.8.0 || echo "⚠️ OpenCV contrib installation failed"
pip install onnx>=1.16.0 || echo "⚠️ ONNX installation failed"
pip install onnxruntime>=1.19.0 || echo "⚠️ ONNXRuntime installation failed"

echo "✅ Build completed!"
