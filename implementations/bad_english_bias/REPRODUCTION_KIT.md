# Reproduction Kit for Scientific and Artistic Claims

## Scientific Reproduction
- Build and run the Docker image:
  ```bash
  docker build -t linguistic-bias-art .
  docker run --rm -v $(pwd)/implementations/bad_english_bias/gallery_assets:/app/implementations/bad_english_bias/gallery_assets linguistic-bias-art
  ```
- All outputs will be in `implementations/bad_english_bias/gallery_assets/`

## Artistic Installation
- See `gallery_assets/README.md` for setup and display instructions.
- All dependencies are open-source and listed in `requirements.txt`.

## Human Validation
- See `human_validation/README.md` and use the provided CSV template for annotation.

## Contact
For questions, see the main README or contact the maintainers.
