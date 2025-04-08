import os
from django.core.management.base import BaseCommand
from openai import OpenAI
from chatapp.infrastructure.models.document_db import DocumentDB

class Command(BaseCommand):
    help = 'Carga archivos .txt y .md a la base de datos con embeddings'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Ruta a la carpeta con documentos')

    def handle(self, *args, **kwargs):
        directory = kwargs['directory']
        client = OpenAI()

        if not os.path.exists(directory):
            self.stderr.write(self.style.ERROR(f"❌ Carpeta no encontrada: {directory}"))
            return

        files_loaded = 0

        for filename in os.listdir(directory):
            if not filename.endswith(('.txt', '.md')):
                continue

            path = os.path.join(directory, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

                if len(content.strip()) == 0:
                    self.stdout.write(self.style.WARNING(f"⚠️  {filename} está vacío. Saltando."))
                    continue

                try:
                    embedding = client.embeddings.create(
                        input=content,
                        model="text-embedding-ada-002"
                    ).data[0].embedding

                    DocumentDB.objects.create(
                        title=filename,
                        content=content,
                        embedding=embedding
                    )

                    self.stdout.write(self.style.SUCCESS(f"✅ Cargado: {filename}"))
                    files_loaded += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"❌ Error al procesar {filename}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 {files_loaded} archivos cargados correctamente."))