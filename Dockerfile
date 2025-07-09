# Dockerfile for Reproducible Scientific and Artistic Experiments

FROM python:3.10-slim

WORKDIR /app

COPY implementations/bad_english_bias/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY implementations/bad_english_bias ./implementations/bad_english_bias

CMD ["python", "implementations/bad_english_bias/scientific_art.py", "--study", "linguistic_bias", "--output_format", "both", "--artifacts_dir", "./implementations/bad_english_bias/gallery_assets"]
