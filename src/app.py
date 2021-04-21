from encoder.params_model import model_embedding_size as speaker_embedding_size
from utils.argutils import print_args
from utils.modelutils import check_model_paths
from synthesizer.inference import Synthesizer
from encoder import inference as encoder
from vocoder import inference as vocoder
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa
import argparse
import torch
import sys
import os
from audioread.exceptions import NoBackendError
import time
import json
import io
import os
from flask import Flask, jsonify, request, Response, send_file


# Setup
app = Flask(__name__)
if torch.cuda.is_available():
    device_id = torch.cuda.current_device()
    gpu_properties = torch.cuda.get_device_properties(device_id)
    print("Found %d GPUs available. Using GPU %d (%s) of compute capability %d.%d with "
        "%.1fGb total memory.\n" % 
        (torch.cuda.device_count(),
        device_id,
        gpu_properties.name,
        gpu_properties.major,
        gpu_properties.minor,
        gpu_properties.total_memory / 1e9))
else:
    print("Using CPU for inference.\n")
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
enc_model_fpath = Path('encoder/saved_models/pretrained.pt')
syn_model_fpath = Path('synthesizer/saved_models/pretrained/pretrained.pt')
voc_model_fpath = Path('vocoder/saved_models/pretrained/pretrained.pt')
check_model_paths(
    encoder_path=enc_model_fpath,
    synthesizer_path=syn_model_fpath,
    vocoder_path=voc_model_fpath)
print("Preparing the encoder, the synthesizer and the vocoder...")
encoder.load_model(enc_model_fpath)
synthesizer = Synthesizer(syn_model_fpath)
vocoder.load_model(voc_model_fpath)
print("Testing Configuration")
print("Testing encoder")
encoder.embed_utterance(np.zeros(encoder.sampling_rate))
embed = np.random.rand(speaker_embedding_size)
embed /= np.linalg.norm(embed)
embeds = [embed, np.zeros(speaker_embedding_size)]
texts = ["test 1", "test 2"]
print("\tTesting the synthesizer")
mels = synthesizer.synthesize_spectrograms(texts, embeds)
mel = np.concatenate(mels, axis=1)
print("\tTesting the vocoder")
vocoder.infer_waveform(mel, target=200, overlap=50, progress_callback=None)
print("All test complete\n\n")


@app.route('/')
def index():
    return jsonify({'status': 'ok'})


@app.route('/generate/', methods=['POST'])
def generate():
    """Generates wav file from text and source audio file"""
    if 'file' not in request.files:
        return jsonify({'error': 'no audio file'})
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'no text provided'})
    source_audio_file = request.files['file'].save('/tmp/original.wav')
    preprocessed_wav = encoder.preprocess_wav(Path('/tmp/original.wav'))
    original_wav, sampling_rate = librosa.load('/tmp/original.wav')
    preprocessed_wav = encoder.preprocess_wav(original_wav, sampling_rate)
    embed = encoder.embed_utterance(preprocessed_wav)
    texts = [text]
    embeds = [embed]
    specs = synthesizer.synthesize_spectrograms(texts, embeds)
    spec = specs[0]
    generated_wav = vocoder.infer_waveform(spec)
    generated_wav = np.pad(generated_wav, (0, synthesizer.sample_rate), mode="constant")
    generated_wav = encoder.preprocess_wav(generated_wav)
    # filename = "/tmp/{}.wav".format(int(time.time()))
    fio = io.BytesIO()
    sf.write(fio, generated_wav.astype(np.float32), synthesizer.sample_rate, None, None, 'WAV')
    fio.seek(0)
    return send_file(fio, as_attachment=True, attachment_filename='generated.wav', mimetype='audio/wav')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
