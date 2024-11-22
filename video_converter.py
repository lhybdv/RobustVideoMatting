import contextlib
import logging
from pathlib import Path

import torch

from config import INPUT_DIR, MODEL_PATH, MODEL_TYPE, OUTPUT_DIR
from inference import convert_video
from model import MattingNetwork
from utils import check_file_exists, delete_file, file_ext, generate_unique_filename

logging.basicConfig(level=logging.INFO)


def load_model():
    try:
        model = MattingNetwork(MODEL_TYPE).eval().cuda()  # or "resnet50"
        check_file_exists(MODEL_PATH, "Model file")
        model.load_state_dict(torch.load(MODEL_PATH, weights_only=True))
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise


def prepare_conversion(input_file: str):
    check_file_exists(INPUT_DIR + input_file, "Input file")
    ext = file_ext(input_file)
    output_file = f"{generate_unique_filename()}{ext}"
    return output_file


def convert_video_with_logging(input_file: str, model):
    logging.info(f"Starting video conversion for input file: {input_file}")
    logging.debug(f"Model type: {MODEL_TYPE}, Model path: {MODEL_PATH}")
    try:
        output_file = prepare_conversion(input_file)
        convert_video(
            model,
            input_source=INPUT_DIR + input_file,
            output_type="video",
            output_composition=OUTPUT_DIR + output_file,
            output_alpha=None,
            output_foreground=None,
            output_video_mbps=4,
            downsample_ratio=None,
            seq_chunk=12,
        )
        return output_file
    except Exception as e:
        logging.error(f"Failed to convert video: {e}")
        raise


def generate_chroma_key_video(input_file: str) -> str:
    model = load_model()
    try:
        output_file = convert_video_with_logging(input_file, model)
        return output_file
    finally:
        with contextlib.suppress(Exception):
            file_path = Path(INPUT_DIR + input_file)
            logging.info(f"Deleting input file: {file_path}")
            delete_file(file_path)
