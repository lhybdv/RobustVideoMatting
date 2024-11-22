from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
import logging
from utils import file_ext, generate_unique_filename
from video_converter import generate_chroma_key_video
from config import INPUT_DIR
app = FastAPI(root_path="/api")
app1 = FastAPI()
app1.mount(
    "/output",
    StaticFiles(directory="output"),
    name="output",
)
app.mount("/v1", app1)
# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_video_file(file: UploadFile):
    valid_extensions = ['.mp4', '.avi', '.mov']
    ext = file_ext(file.filename)
    if ext not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid video file format")


@app1.post("/", description="转换成绿幕视频")
async def convert(file: UploadFile = File(...)):
    try:
        validate_video_file(file)
        ext = file_ext(file.filename)
        filename = generate_unique_filename() + ext
        content = await file.read()
        # 确保 INPUT_DIR 以斜杠结尾
        input_path = f"{INPUT_DIR.rstrip('/')}/{filename}"

        with open(input_path, "wb") as f:
            f.write(content)
        output_file = generate_chroma_key_video(filename)
        return {"report": f"/output/{output_file}"}
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise HTTPException(status_code=404, detail="File not found")
    except PermissionError as e:
        logging.error(f"Permission error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logging.error(f"Unexpected error during video conversion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

