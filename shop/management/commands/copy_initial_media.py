import shutil

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Copy bundled product images to persistent media storage without overwriting uploads.'

    def handle(self, *args, **options):
        source_root = settings.BASE_DIR / 'media'
        destination_root = settings.MEDIA_ROOT
        copied_count = 0

        if source_root.resolve() == destination_root.resolve():
            self.stdout.write('Media storage already uses the bundled media directory.')
            return

        for source in source_root.rglob('*'):
            if not source.is_file():
                continue

            destination = destination_root / source.relative_to(source_root)
            if destination.exists():
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied_count += 1

        self.stdout.write(self.style.SUCCESS(f'Copied {copied_count} bundled media files.'))
