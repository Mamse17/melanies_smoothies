"""Génère les audios edge-tts demandés dans lab/jobs.json (+ repères de mots)."""
import asyncio, json, pathlib, traceback
import edge_tts
root = pathlib.Path(__file__).parent
out = root / "out"; out.mkdir(exist_ok=True)

async def one(job):
    c = edge_tts.Communicate(job["text"], job.get("voice", "ar-SA-HamedNeural"),
                             rate=job.get("rate", "-20%"), boundary="WordBoundary")
    audio, marks = bytearray(), []
    async for ch in c.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        else:
            marks.append({"text": ch["text"], "start": ch["offset"] / 1e7, "end": (ch["offset"] + ch["duration"]) / 1e7})
    (out / f"{job['id']}.mp3").write_bytes(bytes(audio))
    (out / f"{job['id']}.json").write_text(json.dumps({**job, "marks": marks}, ensure_ascii=False, indent=1), encoding="utf-8")

async def main():
    jobs = json.loads((root / "jobs.json").read_text(encoding="utf-8"))
    report = []
    for job in jobs:
        for attempt in range(3):
            try:
                await one(job); report.append(f"OK {job['id']}"); break
            except Exception:
                if attempt == 2: report.append(f"ERREUR {job['id']}\n{traceback.format_exc()}")
                await asyncio.sleep(2)
    (out / "report.txt").write_text("\n".join(report), encoding="utf-8")
asyncio.run(main())
