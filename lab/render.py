"""Fait tourner le VRAI pipeline audio du bot (lab/bot/bot.py) avec la vraie voix."""
import asyncio, io, json, logging, pathlib, sys
root = pathlib.Path(__file__).parent
sys.path.insert(0, str(root / "bot"))
log = io.StringIO()
logging.basicConfig(level=logging.INFO, stream=log, format="%(levelname)s %(message)s")
import bot
out = root / "render"; out.mkdir(exist_ok=True)
cfg = json.loads((root / "render.json").read_text(encoding="utf-8"))

async def main():
    for voice in cfg["voices"]:
        for i, words in enumerate(cfg["items"]):
            for mode in ("normal", "difficile"):
                name = f"{voice.split('-')[2][:5]}_{i:02d}_{mode}"
                try:
                    audio, fname = await bot.render_audio(words, voice, cfg.get("rate", "-20%"),
                                                          cfg.get("pause", 1.0), stretch=(mode == "normal"))
                    (out / f"{name}.mp3").write_bytes(audio)
                    (out / f"{name}.json").write_text(json.dumps({"words": words, "voice": voice, "mode": mode},
                                                                 ensure_ascii=False), encoding="utf-8")
                except Exception as exc:
                    logging.exception("ERREUR %s", name)
    (out / "log.txt").write_text(log.getvalue(), encoding="utf-8")
asyncio.run(main())
