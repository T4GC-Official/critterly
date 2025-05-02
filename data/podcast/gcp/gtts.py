import argparse
import os
import re
import time
from google.cloud import texttospeech_v1 as texttospeech
from google.cloud import storage
from google.cloud import billing_v1


# The language code and VOICE need to match.
# AU is chosen to easily confirm the model isn't using the default vocoder
# voice - which is US.
# These settings are IGNORED in lieu of the voices in the SSML file.
LANGUAGE_CODE = "en-AU"
VOICE = "en-AU-Wavenet-C"


class GCPTextToSpeech:
    def __init__(self, bucket_name):
        self.client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()
        self.billing_client = billing_v1.CloudBillingClient()

    def _ensure_bucket_exists(self):
        bucket = self.storage_client.bucket(self.bucket_name)
        if not bucket.exists():
            raise ValueError(f"Bucket {self.bucket_name} does not exist.")

    def synthesize_long_audio(self, ssml_text, output_file_name):
        """Synthesizes long-form audio from SSML and saves it to a file."""

        input_text = texttospeech.SynthesisInput(ssml=ssml_text)

        # GCP defaults, assuming SSML might override
        voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE_CODE,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            name=VOICE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        )

        # Create the long audio request
        request = texttospeech.SynthesizeLongAudioRequest(
            parent=f"projects/{self.storage_client.project}/locations/global",
            input=input_text,
            voice=voice,
            audio_config=audio_config,
            output_gcs_uri=f"gs://{self.bucket_name}/{output_file_name}",
        )

        # Make the long audio request
        operation = self.client.synthesize_long_audio(request=request)

        # Poll for operation status
        op = operation.operation.name
        while not operation.done():
            print(f"Waiting for operation to complete... {op}")
            time.sleep(15)  # Poll every 15 seconds
            operation = self.client.get_operation(name=op)

        # Check for errors in the operation result
        result = operation.result()
        if result.error:
            print(f"Error during synthesis: {result.error}")
            return

        # The audio file should now be in your bucket
        print(
            f"Audio content written to file: gs://{self.bucket_name}/{output_file_name}")

        # Download the file or print the gsutil command
        try:  # Assuming you add a --download flag to the script
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(output_file_name)
            blob.download_to_filename(output_file_name)
            print(f"Downloaded audio file to: {output_file_name}")
        except Exception as e:
            print(f"Failed to download file: {e}. Download with: ")
            print(f"gsutil cp gs://{self.bucket_name}/{output_file_name} .")


def count_words_in_ssml(ssml_text):
    """Counts words within SSML tags, excluding the tags themselves."""
    # Updated pattern to match any text within any SSML tags
    pattern = r"<[^>]+>([^<]+)</[^>]+>"
    matches = re.findall(pattern, ssml_text, re.DOTALL)
    total_word_count = 0
    for match in matches:
        # No need for group(1) as findall returns the matched text directly
        text_content = match
        word_count = len(text_content.split())
        total_word_count += word_count
    return total_word_count


def main():
    parser = argparse.ArgumentParser(
        description="Synthesize speech from SSML using GCP Text-to-Speech.")
    parser.add_argument("--input", required=True,
                        help="Path to the input SSML file.")
    parser.add_argument("--output", required=True,
                        help="Name of the output LINEAR16 (wav) file (to be stored in the bucket).")
    parser.add_argument("--count-file", required=True,
                        help="Path to the file storing the word count.")
    parser.add_argument("--limit", type=int, default=1000000,
                        help="Word limit (default: 1000000)")
    parser.add_argument("--bucket", required=True,
                        help="Name of the Google Cloud Storage bucket.")
    parser.add_argument("--usage", required=False, default=False,
                        help="If true, only retrieves and records usage from GCP billing apis, then exits.")

    args = parser.parse_args()

    import pudb
    pudb.set_trace()

    # Read the current count from the count file
    if os.path.exists(args.count_file):
        with open(args.count_file, "r") as f:
            current_count = int(f.read().strip())
    else:
        current_count = 0

    with open(args.input, "r") as f:
        ssml_text = f.read()

    word_count = count_words_in_ssml(ssml_text)
    total_count = current_count + word_count

    if total_count > args.limit:
        print(f"Word count exceeds limit ({total_count} > {args.limit}).")
        proceed = input("Enter 'y' to continue, or 'n' to stop: ")
        if proceed.lower() != 'y':
            return

    tts = GCPTextToSpeech(args.bucket)
    tts.synthesize_long_audio(ssml_text, args.output)

    # TODO(prashanth@): Get actual usage from GCP
    print(f"Total usage count {total_count}, writing to count file.")
    with open(args.count_file, "w") as f:
        f.write(str(total_count))


if __name__ == "__main__":
    main()
