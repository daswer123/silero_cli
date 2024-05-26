import argparse
import os
from loguru import logger
from tqdm import tqdm
from silero_tts.silero_tts import SileroTTS

def main():
    parser = argparse.ArgumentParser(description='Silero TTS CLI')
    parser.add_argument('--list-models', action='store_true', help='List available models')
    parser.add_argument('--list-speakers', action='store_true', help='List available speakers for a model')
    parser.add_argument('--language', type=str, help='Language code')
    parser.add_argument('--model', type=str, help='Model ID (default: latest version for the language)')
    parser.add_argument('--speaker', type=str, help='Speaker name (default: first available speaker for the model)')
    parser.add_argument('--sample-rate', type=int, default=48000, help='Sample rate (default: 48000)')
    parser.add_argument('--device', type=str, default='cpu', help='Device to use (default: cpu)')
    parser.add_argument('--text', type=str, help='Text to synthesize')
    parser.add_argument('--input-file', type=str, help='Input text file to synthesize')
    parser.add_argument('--input-dir', type=str, help='Input directory with text files to synthesize')
    parser.add_argument('--output-file', type=str, default='output.wav', help='Output audio file (default: output.wav)')
    parser.add_argument('--output-dir', type=str, default='output', help='Output directory for synthesized audio files (default: output)')
    args = parser.parse_args()

    try:
        if args.list_models:
            models = SileroTTS.get_available_models()
            logger.info(f"Available models: {models}")
        else:
            if not args.language:
                logger.error("Please specify the language using the --language flag.")
                logger.info(f"Available languages: {', '.join(SileroTTS.get_available_languages())}")
                return
            elif args.language not in SileroTTS.get_available_languages():
                logger.error(f"Language '{args.language}' is not supported.")
                logger.info(f"Available languages: {', '.join(SileroTTS.get_available_languages())}")
                return

            if not args.model:
                args.model = SileroTTS.get_latest_model(args.language)
                logger.warning(f"Using the latest model for {args.language}: {args.model}")
                logger.info(f"You can specify a different model using the --model flag.")
                logger.info(f"Example: --model v4_ru")
                logger.info(f"Available models for {args.language}: {', '.join(SileroTTS.get_available_models()[args.language])}")

            logger.info(f"Initializing TTS with model: {args.model}, language: {args.language}, speaker: {args.speaker}")
            tts = SileroTTS(model_id=args.model, language=args.language, speaker=args.speaker,
                            sample_rate=args.sample_rate, device=args.device)
            logger.success(f"TTS initialized successfully.")

            if not args.speaker:
                logger.warning(f"Using the default speaker: {tts.speaker}")
                logger.info(f"You can specify a different speaker using the --speaker flag.")
                logger.info(f"Example: --speaker aidar")
                logger.info(f"Available speakers for model {args.model}: {', '.join(tts.get_available_speakers())}")

            if args.list_speakers:
                speakers = tts.get_available_speakers()
                logger.info(f"Available speakers for model {args.model}: {speakers}")
            else:
                if not (args.text or args.input_file or args.input_dir):
                    logger.error("Please provide either --text, --input-file, or --input-dir argument.")
                    return

                if args.text:
                    logger.info(f"Synthesizing speech from text: {args.text}")
                    tts.tts(args.text, args.output_file)
                    logger.success(f"Speech synthesized successfully. Output saved to: {args.output_file}")
                elif args.input_file:
                    logger.info(f"Synthesizing speech from file: {args.input_file}")
                    tts.from_file(args.input_file, args.output_file)
                    logger.success(f"Speech synthesized successfully. Output saved to: {args.output_file}")
                elif args.input_dir:
                    if not os.path.exists(args.output_dir):
                        os.makedirs(args.output_dir)

                    txt_files = [f for f in os.listdir(args.input_dir) if f.endswith('.txt')]
                    logger.info(f"Found {len(txt_files)} text files in directory: {args.input_dir}")

                    for txt_file in tqdm(txt_files, desc="Synthesizing"):
                        input_path = os.path.join(args.input_dir, txt_file)
                        output_path = os.path.join(args.output_dir, f"{os.path.splitext(txt_file)[0]}.wav")
                        tts.from_file(input_path, output_path)

                    logger.success(f"Batch synthesis completed. Output files saved in: {args.output_dir}")
    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
