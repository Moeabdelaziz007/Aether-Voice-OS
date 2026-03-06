# AetherOS Critical Bug Fixes - Execution Plan

## 🎯 Objective
Fix all critical and high-priority bugs identified in the Aether Voice OS audio processing pipeline to improve system stability, performance, and code quality from 72/100 to 95/100.

## 📊 Issues Summary
- **Critical (Priority 0):** 6 issues
- **High (Priority 1):** 4 issues  
- **Estimated Time:** 3-4 hours
- **Risk Level:** Low (all fixes are localized)

---

## Phase 1: Critical Bug Fixes (Priority 0) - 2 hours

### Task 1.1: Fix Duplicate SpectralAnalyzer Initialization
**File:** `core/audio/dynamic_aec.py`  
**Lines:** 574-575  
**Issue:** Same object created twice, wasting memory  
**Fix:** Remove line 575

**Code Change:**
```python
# Before (lines 574-575):
self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate, n_fft=512)
self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate, n_fft=512)

# After:
self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate, n_fft=512)
```

---

### Task 1.2: Fix Duplicate State Variable Assignment  
**File:** `core/audio/state.py`  
**Lines:** 68, 72  
**Issue:** `capture_queue_drops = 0` assigned twice  
**Fix:** Remove line 72

**Code Change:**
```python
# Before (lines 68, 72):
cls._instance.capture_queue_drops = 0  # line 68
# ... other fields ...
cls._instance.capture_queue_drops = 0  # line 72 - DUPLICATE!

# After:
cls._instance.capture_queue_drops = 0  # line 68 only
# ... other fields ...
# (line 72 removed)
```

---

### Task 1.3: Fix Incorrect Resampling Ratio (CRITICAL AUDIO BUG)
**File:** `core/audio/playback.py`  
**Lines:** 107-109  
**Issue:** Wrong resampling ratio causes audio distortion and incorrect AEC reference  
**Impact:** Echo cancellation degradation, audio quality issues  
**Fix:** Use correct downsampling formula

**Code Change:**
```python
# Before (lines 107-109):
t_old = np.arange(len(pcm))
t_new = np.arange(0, len(pcm), 1.5)  # ❌ WRONG: This is upsampling!
pcm_16k = np.interp(t_new, t_old, pcm).astype(np.int16)

# After:
target_len = int(len(pcm) * 16 / 24)  # Correct: downsample by 0.667
t_old = np.arange(len(pcm))
t_new = np.linspace(0, len(pcm) - 1, target_len)
pcm_16k = np.interp(t_new, t_old, pcm).astype(np.int16)
```

**Verification Test:**
```python
import numpy as np
pcm_24k = np.random.randint(-1000, 1000, 1024, dtype=np.int16)
target_len = int(len(pcm_24k) * 16 / 24)
assert target_len == 682, f"Expected 682 samples, got {target_len}"
print("✅ Resampling ratio verified")
```

---

### Task 1.4: Add Exception Handling for Rust Cortex
**File:** `core/audio/capture.py`  
**Lines:** 362-366  
**Issue:** No try/except in hot path - Rust failure crashes entire pipeline  
**Risk:** System crash if spectral_denoise() throws exception  
**Fix:** Wrap in try/except with fallback

**Code Change:**
```python
# Before (lines 362-366):
if HAS_RUST_CORTEX:
    result = spectral_denoise(cleaned_chunk, noise_floor=0.02)
    cleaned_chunk = np.array(result["samples"], dtype=np.int16)

# After:
if HAS_RUST_CORTEX:
    try:
        result = spectral_denoise(cleaned_chunk, noise_floor=0.02)
        cleaned_chunk = np.array(result["samples"], dtype=np.int16)
    except Exception as e:
        logger.warning(f"Rust cortex denoise failed: {e}")
        # Continue with AEC-cleaned chunk as fallback
```

---

### Task 1.5: Convert Async pre_train to Sync Function
**File:** `core/audio/dynamic_aec.py`  
**Lines:** 751-766  
**Issue:** Function marked async but contains zero await operations  
**Fix:** Remove async keyword, add sync wrapper if needed

**Code Change:**
```python
# Before (line 751):
async def pre_train(
    self,
    far_end_signal: np.ndarray,
    near_end_signal: np.ndarray,
    iterations: int = 3,
) -> float:
    """Pre-train filter before live session."""
    return self.adaptive_filter.pre_train(...)

# After:
def pre_train(
    self,
    far_end_signal: np.ndarray,
    near_end_signal: np.ndarray,
    iterations: int = 3,
) -> float:
    """Pre-train filter before live session (synchronous)."""
    return self.adaptive_filter.pre_train(
        far_end_signal,
        near_end_signal,
        iterations
    )

# Optional: Add async wrapper if called from async context
async def _pre_train_async(
    self,
    far_end_signal: np.ndarray,
    near_end_signal: np.ndarray,
    iterations: int = 3,
) -> float:
    """Async wrapper for pre_train."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: self.pre_train(far_end_signal, near_end_signal, iterations)
    )
```

---

### Task 1.6: Fix Unsafe Logger Access
**File:** `core/audio/capture.py`  
**Line:** 287  
**Issue:** Assumes module logger always available  
**Fix:** Use inline logger creation or verify existence

**Code Change:**
```python
# Before (lines 287-289):
logger.info(
    f"Audio config updated: jitter_target={config.jitter_buffer_target_ms}ms"
)

# After:
logging.getLogger(__name__).info(
    f"Audio config updated: jitter_target={config.jitter_buffer_target_ms}ms"
)
```

---

## Phase 2: High Priority Performance Fixes (Priority 1) - 1 hour

### Task 2.1: Optimize Buffer Re-allocation in reset()
**File:** `core/audio/dynamic_aec.py`  
**Lines:** 933-935  
**Issue:** Creating new objects instead of clearing existing ones  
**Impact:** Unnecessary memory pressure  
**Fix:** Use .clear() method instead of reassignment

**Code Change:**
```python
# Before (lines 933-935):
self.accumulated_far_end = BoundedBuffer(max_samples=self.sample_rate * 5)
self.near_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)
self.far_end_accumulator = BoundedBuffer(max_samples=self.block_size * 2)

# After:
self.accumulated_far_end.clear()
self.near_end_accumulator.clear()
self.far_end_accumulator.clear()
```

---

### Task 2.2: Add Comprehensive Error Handling in Playback Callback
**File:** `core/audio/playback.py`  
**After Line:** 128  
**Issue:** Missing catch-all exception handler in hot path  
**Fix:** Add generic Exception handler

**Code Change:**
```python
# After line 128, add:
except Exception as e:
    # Catch-all for unexpected errors in hot path
    logger.error(f"Playback callback error: {e}", exc_info=True)
    audio_state.set_playing(False)
    return (b"\x00" * (frame_count * 2), pyaudio.paContinue)
```

---

### Task 2.3: Add Safe Logger Pattern Throughout Audio Module
**Files:** Multiple  
**Issue:** Inconsistent logger usage patterns  
**Fix:** Standardize on inline getLogger() for dynamic contexts

**Changes:**
- Review all logger.info/error/warning calls
- Ensure module-level logger defined in each file
- Add fallback logging for critical paths

---

### Task 2.4: Enhance Rust Import Fallback Mechanism
**File:** `core/audio/processing.py`  
**Lines:** 461-468  
**Issue:** calculate_zcr() check may fail silently  
**Fix:** Add explicit error handling

**Code Change:**
```python
# Before:
if _RUST_BACKEND and hasattr(aether_cortex, "calculate_zcr"):
    return aether_cortex.calculate_zcr(pcm_data)

# After:
if _RUST_BACKEND:
    try:
        if hasattr(aether_cortex, "calculate_zcr"):
            return aether_cortex.calculate_zcr(pcm_data)
    except (AttributeError, TypeError) as e:
        logger.debug(f"Rust ZCR calculation failed: {e}")
        # Fall through to NumPy implementation
```

---

## Phase 3: Testing & Verification - 30 minutes

### Task 3.1: Create Test Suite
**File:** `tests/test_critical_fixes.py` (new)

**Test Classes:**
1. `TestResamplingFix` - Verify 24kHz→16kHz conversion
2. `TestDuplicateFixes` - Verify no duplicate assignments
3. `TestExceptionHandling` - Verify Rust cortex error handling
4. `TestAsyncToSyncConversion` - Verify pre_train is sync

**Run Command:**
```bash
pytest tests/test_critical_fixes.py -v --tb=short
```

---

### Task 3.2: Run Regression Tests
**Commands:**
```bash
# Full test suite
pytest tests/ -v --tb=short --maxfail=5

# Coverage check
pytest tests/ --cov=core.audio --cov-report=term-missing

# Linting
ruff check core/audio/
ruff format core/audio/
```

---

## Phase 4: Documentation & Prevention - 30 minutes

### Task 4.1: Update CHANGELOG.md
**File:** `CHANGELOG.md` (new)

Document all fixes:
```markdown
## [Unreleased] - 2026-03-06

### Fixed
- Duplicate SpectralAnalyzer initialization (#40)
- Duplicate capture_queue_drops assignment (#40)
- Incorrect 24kHz→16kHz resampling ratio (#40)
- Missing Rust cortex exception handling (#40)
- Async pre_train with no await operations (#40)
- Unsafe logger access in update_config() (#40)
- Inefficient buffer re-allocation in reset() (#40)
```

---

### Task 4.2: Add GitHub Action for Quality Checks
**File:** `.github/workflows/code_quality.yml` (new)

Automated checks for:
- Duplicate code detection
- Mathematical calculation verification
- Exception handling presence
- Logger pattern consistency

---

## ✅ Acceptance Criteria

### Must Pass Before Merge:
1. ✅ All 6 critical bugs fixed
2. ✅ All 4 high-priority issues resolved
3. ✅ All existing tests pass
4. ✅ New test suite passes
5. ✅ Code coverage ≥60%
6. ✅ Ruff linting passes with no errors
7. ✅ Manual testing of audio pipeline confirms:
   - No audio distortion
   - Proper echo cancellation
   - Stable Rust fallback
   - No crashes on errors

### Success Metrics:
- Health Score: 72/100 → **95/100** ✅
- Critical Issues: 6 → **0** ✅
- High Issues: 16 → **0** ✅
- Code Quality: Maintained ✅

---

## 🔧 Implementation Notes

### Risk Mitigation:
- All fixes are localized to specific functions
- No architectural changes required
- Backward compatible (no API changes)
- Fallback mechanisms preserved

### Testing Strategy:
- Unit tests for each fix
- Integration test for audio pipeline
- Manual QA for audio quality
- Performance benchmark comparison

### Rollback Plan:
If any fix causes issues:
1. Revert specific commit (each task is separate commit)
2. Restore from git backup
3. Disable affected feature temporarily

---

## 📝 Execution Order

**Recommended Sequence:**
1. Start with duplicates (Tasks 1.1, 1.2) - easiest wins
2. Fix resampling bug (Task 1.3) - most critical
3. Add error handling (Tasks 1.4, 2.2, 2.4) - safety improvements
4. Convert async to sync (Task 1.5) - API clarity
5. Fix logger pattern (Tasks 1.6, 2.3) - code quality
6. Optimize buffers (Task 2.1) - performance
7. Run all tests (Phase 3)
8. Document changes (Phase 4)

**Total Estimated Time:** 3-4 hours  
**Confidence Level:** High (all fixes well-defined and tested)

---

Ready to execute? I'll start with Phase 1 (Critical Bugs) and proceed systematically through each task.