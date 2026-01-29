from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    help = "Generate per-app and inter-app Django model graphs"

    def handle(self, *args, **options):
        base_dir = Path("model-graphs")
        apps_dir = base_dir / "apps"
        inter_dir = base_dir / "inter-app"

        apps_dir.mkdir(parents=True, exist_ok=True)
        inter_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write("Collecting app labels...")

        app_labels = []
        for app in apps.get_app_configs():
            if app.name.startswith("django."):
                continue
            if app.name.startswith("django.contrib."):
                continue
            if app.label == "django_extensions":
                continue
            app_labels.append(app.label)

        # per-app graphs
        for label in app_labels:
            self.stdout.write(f"Generating graphs for {label}")

            try:
                call_command(
                    "graph_models",
                    label,
                    "--inheritance",
                    output=str(apps_dir / f"{label}_inheritance.svg"),
                )
            except Exception as e:
                self.stderr.write(f"[warn] inheritance graph failed for {label}: {e}")

            try:
                call_command(
                    "graph_models",
                    label,
                    "--no-inheritance",
                    output=str(apps_dir / f"{label}_relations.svg"),
                )
            except Exception as e:
                self.stderr.write(f"[warn] relations graph failed for {label}: {e}")

        # inter-app graphs
        self.stdout.write("Generating inter-app graphs")

        try:
            call_command(
                "graph_models",
                "--all-applications",
                "--inheritance",
                output=str(inter_dir / "backend_inheritance.svg"),
            )
        except Exception as e:
            self.stderr.write(f"[warn] inter inheritance failed: {e}")

        try:
            call_command(
                "graph_models",
                "--all-applications",
                "--no-inheritance",
                output=str(inter_dir / "backend_relations.svg"),
            )
        except Exception as e:
            self.stderr.write(f"[warn] inter relations failed: {e}")

        self.stdout.write(self.style.SUCCESS("Model graph generation completed"))
