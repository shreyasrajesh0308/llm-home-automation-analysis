import whisper
model = whisper.load_model("base", download_root="/Users/duanchenda/Desktop/gitplay/llm-home-automation-analysis/asset")
result = model.transcribe("/Users/duanchenda/Desktop/gitplay/llm-home-automation-analysis/asset/sample_command.mp3")
print(result["text"])
