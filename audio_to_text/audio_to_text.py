import os
import argparse
import whisper

def transcribe_videos(input_folder: str, output_folder: str, model_name: str = "base"):
    # Load Whisper model
    print(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Supported video formats

    for filename in os.listdir(input_folder):
        video_path = os.path.join(input_folder, filename)
        output_path = os.path.join(
            output_folder, os.path.splitext(filename)[0] + ".txt"
        )

        print(f"Transcribing: {video_path}")
        result = model.transcribe(video_path)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(f"Saved transcription to: {output_path}")


if __name__ == "__main__":
    transcribe_videos("./downloads", "./test", "tiny")
