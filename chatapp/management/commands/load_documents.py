import os
from django.core.management.base import BaseCommand
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError, InternalServerError, AuthenticationError
from chatapp.infrastructure.models.document_db import DocumentDB
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class Command(BaseCommand):
    help = 'Loads .txt and .md files into the database with embeddings'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Path to the documents folder')

    @retry(
        retry=retry_if_exception_type((APIConnectionError, RateLimitError, APITimeoutError, InternalServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def handle(self, *args, **kwargs):
        directory = kwargs['directory']
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.stderr.write(self.style.ERROR("OPENAI_API_KEY not configured in environment variables"))
            return
            
        client = OpenAI(api_key=api_key)

        if not os.path.exists(directory):
            self.stderr.write(self.style.ERROR(f"Folder not found: {directory}"))
            return

        files_loaded = 0

        for filename in os.listdir(directory):
            if not filename.endswith(('.txt', '.md')):
                continue

            path = os.path.join(directory, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

                if len(content.strip()) == 0:
                    self.stdout.write(self.style.WARNING(f"⚠️  {filename} is empty. Skipping."))
                    continue

                try:
                    content = content.replace('\n', ' ')
                    embedding = client.embeddings.create(
                        input=[content],
                        model="text-embedding-3-small"
                    ).data[0].embedding

                    DocumentDB.objects.create(
                        title=filename,
                        content=content,
                        embedding=embedding
                    )

                    self.stdout.write(self.style.SUCCESS(f"Loaded: {filename}"))
                    files_loaded += 1

                except AuthenticationError:
                    self.stderr.write(self.style.ERROR("Authentication error with OpenAI"))
                    return
                except (APIConnectionError, APITimeoutError):
                    self.stderr.write(self.style.ERROR(f"Connection error while processing {filename}. Retrying..."))
                    continue
                except RateLimitError:
                    self.stderr.write(self.style.ERROR(f"Rate limit reached. Please wait a few minutes and try again."))
                    return
                except APIError as e:
                    self.stderr.write(self.style.ERROR(f"API error while processing {filename}: {str(e)}"))
                    continue
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Unexpected error while processing {filename}: {str(e)}"))
                    continue

        self.stdout.write(self.style.SUCCESS(f"\n🎉 {files_loaded} files successfully loaded."))