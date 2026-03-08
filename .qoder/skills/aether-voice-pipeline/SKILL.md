---
name: aether-voice-pipeline
description: Process real-time voice audio through Thalamic Gate v2 AEC pipeline with emotion detection and barge-in handling. Use when working with live audio streams, implementing voice activity detection, or processing emotional audio signatures.
---

# Aether Voice Pipeline

## Overview

This skill implements the complete voice processing pipeline from Aether OS, including the Thalamic Gate v2 (software-defined AEC), emotion detection, and real-time barge-in handling.

## When to Use

Use this skill when:
- Processing live audio streams from microphone
- Implementing echo cancellation (AEC)
- Detecting emotions from voice (92% F1 score)
- Handling barge-in (user interruption)
- Working with Gemini Live API sessions
- Building voice-first interfaces

## Core Components

### 1. Thalamic Gate v2

Software-defined Automatic Echo Cancellation with <2ms latency.

**Key Features**:
- Processes raw PCM chunks directly
- Sub-2ms processing latency
- Preserves emotional undertones
- Configurable barge-in thresholds

**Usage**:
```python
from core.audio.thalamic_gate import ThalamicGateV2

gate = ThalamicGateV2(
    chunk_size=480,  # 10ms at 48kHz
    echo_threshold_db=-30,
    barge_in_enabled=True
)

processed_chunk = gate.process(audio_chunk)
```

### 2. Emotion Detector

Analyzes voice for emotional signatures with 92% F1 score.

**Detects**:
- Frustration (sighs, pitch changes)
- Cognitive load (breathing patterns)
- Excitement (voice energy)
- Confusion (pause patterns)

**Usage**:
```python
from core.emotion.detector import EmotionDetector

detector = EmotionDetector()
emotion = detector.analyze(audio_features)
# Returns: {emotion: "frustrated", confidence: 0.87}
```

### 3. Barge-In Handler

Manages user interruptions without clipping.

**Configuration**:
```python
BARGE_IN_CONFIG = {
    'detection_latency_ms': 50,
    'fade_out_duration_ms': 200,
    'min_speech_duration_ms': 300,
    'confidence_threshold': 0.65
}
```

**Usage**:
```python
from core.audio.barge_in import BargeInHandler

handler = BargeInHandler()
if handler.detect_interruption(audio_stream):
    handler.fade_out_playback()
    handler.route_to_asr()
```

## Audio Pipeline Architecture

### Capture → Process → Playback Flow

```
Microphone Input
    ↓
[Audio Capture]
    ↓
[Thalamic Gate v2 - AEC]
    ↓
[Emotion Detection]
    ↓
[Barge-In Handler]
    ↓
[Gemini Live Session]
    ↓
[Audio Playback]
```

### Thread-Safe Queues

Each layer communicates via thread-safe queues:

```python
from queue import Queue
import threading

capture_queue = Queue(maxsize=100)
processing_queue = Queue(maxsize=50)
playback_queue = Queue(maxsize=100)

def capture_worker():
    while running:
        chunk = capture_audio()
        capture_queue.put(chunk, timeout=0.01)

def processing_worker():
    while running:
        chunk = capture_queue.get(timeout=0.01)
        processed = thalamic_gate.process(chunk)
        emotion = detector.analyze(processed)
        processing_queue.put((processed, emotion), timeout=0.01)
```

## Configuration

### AetherConfig Settings

```python
AUDIO_CONFIG = {
    'sample_rate': 48000,
    'channels': 1,
    'chunk_size_ms': 10,
    'aec': {
        'enabled': True,
        'latency_target_ms': 2,
        'echo_suppression_db': -30
    },
    'emotion': {
        'enabled': True,
        'model_path': 'models/emotion_v3.pkl',
        'features': ['pitch', 'energy', 'spectral_centroid']
    },
    'barge_in': {
        'enabled': True,
        'detection_threshold': 0.65,
        'fade_duration_ms': 200
    }
}
```

## Performance Metrics

- **AEC Latency**: <2ms (achieved: 1.8ms)
- **Emotion Detection F1**: 92% on test set
- **Barge-In Response**: <100ms total
- **Audio Quality**: 48kHz, 16-bit, mono

## Testing

### Unit Tests

```python
def test_thalamic_gate_latency():
    gate = ThalamicGateV2()
    chunk = generate_test_audio(duration_ms=10)
    
    start = time.perf_counter()
    processed = gate.process(chunk)
    latency_ms = (time.perf_counter() - start) * 1000
    
    assert latency_ms < 2.0
```

### Integration Tests

```python
def test_complete_pipeline():
    pipeline = VoicePipeline()
    
    # Simulate user speaking while bot talks
    pipeline.start_playback(bot_audio)
    sleep(0.5)
    pipeline.start_capture(user_audio)
    
    # Verify barge-in triggered
    assert pipeline.barge_in_triggered
    assert playback_faded_out
    assert user_audio_routed_to_gemini
```

### Real Audio Tests

Test with actual audio scenarios:

```python
def test_frustration_detection():
    detector = EmotionDetector()
    
    # Load frustrated voice sample
    audio = load_audio('samples/frustrated_user.wav')
    emotion = detector.analyze(audio)
    
    assert emotion['primary'] == 'frustrated'
    assert emotion['confidence'] > 0.85
```

## Usage Examples

### Example 1: Live Conversation

```python
from core.engine import AetherEngine

engine = AetherEngine()
engine.start_session()

# User speaks
engine.capture_audio()

# System processes with emotion
response = engine.process(
    include_emotion=True,
    enable_barge_in=True
)

# System responds with detected emotion context
print(f"User emotion: {response.context.emotion}")
```

### Example 2: Barge-In Scenario

```python
# Bot is speaking
bot_audio = synthesize("The weather today is...")
playback.start(bot_audio)

# User interrupts mid-sentence
user_interrupt = capture_audio()

# Barge-in handler detects interruption
if barge_in.detect(user_interrupt):
    playback.fade_out(duration_ms=200)
    gemini.send_audio(user_interrupt)
```

### Example 3: Emotion-Aware Response

```python
# Detect frustration
emotion = detector.analyze(user_audio)

if emotion['primary'] == 'frustrated':
    # Adjust response strategy
    response_config = {
        'tone': 'empathetic',
        'pace': 'slower',
        'detail_level': 'concise'
    }
else:
    response_config = {'tone': 'normal'}

response = gemini.generate(user_audio, config=response_config)
```

## Troubleshooting

### Issue: High AEC Latency (>5ms)

**Solutions**:
1. Reduce chunk size (try 240 samples = 5ms)
2. Optimize audio buffer sizes
3. Check CPU load, reduce other processes

### Issue: False Barge-In Triggers

**Solutions**:
1. Increase confidence threshold (default: 0.65)
2. Add noise floor filter
3. Require minimum speech duration (300ms)

### Issue: Low Emotion Accuracy

**Solutions**:
1. Retune feature extraction parameters
2. Update emotion model with recent data
3. Check audio quality (SNR > 30dB)

## Advanced Patterns

### Dynamic Threshold Adjustment

```python
class AdaptiveBargeIn:
    def __init__(self):
        self.base_threshold = 0.65
        self.time_of_day_factor = 1.0
    
    def adjust_for_time_of_day(self):
        hour = datetime.now().hour
        if 2 <= hour <= 6:  # Night hours
            self.threshold = self.base_threshold * 1.2  # More sensitive
        else:
            self.threshold = self.base_threshold
```

### Multi-Modal Emotion Fusion

```python
def fuse_emotion_cues(audio_emotion, text_sentiment):
    weights = {
        'audio': 0.7,  # Voice tone is primary
        'text': 0.3    # Text sentiment supports
    }
    
    fused_score = (
        weights['audio'] * audio_emotion['confidence'] +
        weights['text'] * text_sentiment['score']
    )
    
    return {
        'emotion': audio_emotion['primary'],
        'confidence': fused_score
    }
```

## Related Resources

- [Architecture Guide](docs/ARCHITECTURE.md) - Complete pipeline documentation
- [Audio Pipeline Benchmarks](tests/benchmarks/audio_pipeline.py)
- [Gemini Live Integration](core/api/gemini_live.py)

## Security Considerations

- Microphone access requires explicit user consent
- Audio data never leaves device without encryption
- Emotion data stored locally only
- Implement rate limiting on API calls
- Audit all audio processing operations
