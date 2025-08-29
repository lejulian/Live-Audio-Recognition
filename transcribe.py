import os
import time
import whisper
import datetime

model = whisper.load_model("medium", device="cpu")

wav_dir = "wavoutput"
output_html = "transcriptions.html"
output_css = "txtstyle.css"

# Write HTML header if file does not exist
if not os.path.exists(output_html):
    with open(output_html, "w") as out_f:
        out_f.write('<link href="txtstyle.css" rel="stylesheet" type="text/css" />')
        out_f.write("<html><head><title>SDR ATC Logging</title></head><body>\n")
        out_f.write("<h1>SDR ATC Intercepts</h1>\n<ul>\n")
    with open(output_css, 'w') as out_css:
        out_css.write("""
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { background: #f9f9f9; margin: 10px 0; padding: 10px; border-radius: 5px; }
        b { color: #555; }
        """)

print("Watching for new WAV files to transcribe... (Ctrl+C to stop)")
while True:
    files = sorted([f for f in os.listdir(wav_dir) if f.lower().endswith(".wav")])
    if files:
        # Read current HTML content (except closing tags)
        if os.path.exists(output_html):
            with open(output_html, "r") as out_f:
                lines = out_f.readlines()
            # Find where the <ul> starts and ends
            ul_start = next(i for i, l in enumerate(lines) if "<ul>" in l)
            ul_end = len(lines)
            for i, l in enumerate(lines):
                if "</ul>" in l:
                    ul_end = i
                    break
            header = lines[:ul_start+1]
            existing_items = lines[ul_start+1:ul_end]
            footer = lines[ul_end:]
        else:
            header = [
                '<link href="txtstyle.css" rel="stylesheet" type="text/css" />',
                "<html><head><title>SDR ATC Logging</title></head><body>\n",
                "<h1>SDR ATC Intercepts</h1>\n",
                "<ul>\n"
            ]
            existing_items = []
            footer = ["</ul>\n", "</body></html>"]

        new_items = []
        for filename in files:
            filepath = os.path.join(wav_dir, filename)
            # Get file modification time
            mod_time = os.path.getmtime(filepath)
            time_str = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
            result = model.transcribe(
                filepath,
                task="translate"
            )
            lang = result['language']
            text = result["text"].strip()
            if text:  # Only add if transcription is not empty
                new_items.append(
                    f"<li><b>Time:</b> {time_str}<br>"
                    f"<b>Detected language:</b> {lang}<br>"
                    f"<b>Transcription:</b> {text}</li>\n"
                )
            os.remove(filepath)

        # Write new HTML with new items at the top
        with open(output_html, "w") as out_f:
            out_f.writelines(header)
            out_f.writelines(new_items)
            out_f.writelines(existing_items)
            out_f.writelines(footer)
    time.sleep(2)  # Check every 2 seconds