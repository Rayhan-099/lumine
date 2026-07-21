# Lumine AI - ML Pipeline Integrity Audit

## Objective
Verify that the refactoring of the backend did not alter or break the original Machine Learning inference logic from the `Viani` implementation.

## Pipeline Trace

### 1. Image Validation & Reception
*   **Original**: FastAPIs `UploadFile` handled the image in `main.py`.
*   **Current**: Preserved exactly in `app/api/endpoints/analyze.py`.
*   **Status**: Unchanged.

### 2. Preprocessing & Input
*   **Original**: The image was read asynchronously (`await image.read()`) into bytes and passed directly to the Hugging Face `requests.post()` call without local resizing or tensor conversion.
*   **Current**: The exact same byte-reading logic is preserved in `app/services/ml_service.py` (`await image.read()`).
*   **Status**: Unchanged.

### 3. Model Request (Hugging Face / Local)
*   **Original**: Target URL was `https://api-inference.huggingface.co/models/google/vit-base-patch16-224` with a hardcoded Bearer token.
*   **Current**: Target URL remains identical. The token was moved to `.env` (`HF_TOKEN`) for security, but the request structure (`headers={"Authorization": f"Bearer {settings.HF_TOKEN}"}`, `data=img_bytes`) is identical.
*   **Status**: Preserved (Secured token).

### 4. Response Parsing & Label Mapping
*   **Original**: 
    ```python
    if isinstance(result, list) and len(result) > 0:
        top = result[0]
        # ...
    ```
*   **Current**: Logic copied verbatim into `ml_service.py`.
*   **Status**: Unchanged.

### 5. Confidence Calculation
*   **Original**: `round(top.get("score", 0) * 100, 2)`
*   **Current**: `round(top.get("score", 0) * 100, 2)`
*   **Status**: Unchanged.

### 6. Fallback Mechanism (Offline Demo)
*   **Original**: If the HF API failed, it randomly selected from a static list of `fallback_labels` (Acne, Skin Rash, Scar, Burn, Dry Skin) with a random confidence score.
*   **Current**: The exact same `except Exception as e:` block and fallback logic is preserved in `ml_service.py`.
*   **Status**: Unchanged.

## Modification Summary
**Files Preserved/Moved:**
*   The logic from `main.py` was moved directly into `app/services/ml_service.py` to decouple the ML operations from the routing logic.

**Files Modified:**
*   `main.py`: Refactored to act solely as the FastAPI entrypoint.
*   The Hugging Face Token was parameterized.

**Conclusion:**
The original inference pipeline was **NOT damaged or altered** in behavior. The image bytes, API request format, and output parsing remain identical to the friend's original Viani implementation.
