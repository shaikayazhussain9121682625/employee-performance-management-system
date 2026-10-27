# Reproducibility Guide

## Requirements
- Python installed
- Node.js and npm installed
- Project dependencies installed

## Backend setup
From the project root, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run backend tests:

```powershell
python -m unittest discover -s backend/tests -v
```

## Dataset validation
Validate the generated 30k dataset:

```powershell
$env:VALIDATION_DATA_DIR = "generated_telugu_30k"
python .\scripts\validate_data.py
Remove-Item Env:VALIDATION_DATA_DIR -ErrorAction SilentlyContinue
```

## Frontend build
```powershell
Push-Location .\frontend
npm run build
Pop-Location
```

## Import safety
Use a separate, new SQLite database for import testing. Never overwrite the application's existing database just to test a generated dataset.

Check importer options first:

```powershell
python .\backend\import_data.py --help
```

## Reproducibility notes
Use the generator's documented seed and options when reproducing the dataset. Record the actual validation output and test results before submitting. Do not claim a check passed unless it ran successfully.
